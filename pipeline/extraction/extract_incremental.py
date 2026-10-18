import argparse
import csv
import json
import os
from datetime import datetime, timezone
from pathlib import Path

import psycopg
from psycopg import sql
from dotenv import load_dotenv


# ============================================================
# PROJECT PATHS
# ============================================================

# Repository root:
# ETL_CIGNALCARE_PIPELINE-GROUP10/
BASE_DIR = Path(__file__).resolve().parents[2]

EXTRACT_DIR = BASE_DIR / "data" / "extracted"
STATE_DIR = BASE_DIR / "state"

STATE_FILE = STATE_DIR / "watermarks.json"
LOG_FILE = STATE_DIR / "extraction_log.csv"


# ============================================================
# APPROVED SOURCE TABLES
# LAB 3 = EXTRACTION ONLY
# ============================================================

TABLES = {

    "users": {
        "columns": [
            "id",
            "location",
            "status",
            "created_at",
            "updated_at",
        ],
        "watermark": "coalesce",
        "id_type": "int",
    },

    "prepaid_plans": {
        "columns": [
            "id",
            "plan_code",
            "plan_name",
            "amount",
            "validity_days",
            "status",
            "created_at",
            "updated_at",
        ],
        "watermark": "coalesce",
        "id_type": "int",
    },

    "prepaid_transactions": {
        "columns": [
            "id",
            "reference_no",
            "user_id",
            "plan_id",
            "amount",
            "payment_method",
            "transaction_date",
            "status",
            "created_at",
        ],
        "watermark": "created_at",
        "id_type": "int",
    },

    "load_requests": {
        "columns": [
            "id",
            "user_id",
            "plan_id",
            "amount",
            "payment_method",
            "payment_status",
            "reference_no",
            "payment_completed_at",
            "fulfilled_at",
            "status",
            "created_at",
            "updated_at",
        ],
        "watermark": "coalesce",
        "id_type": "int",
    },

    "tickets": {
        "columns": [
            "id",
            "user_id",
            "category",
            "priority",
            "status",
            "incident_id",
            "created_at",
            "updated_at",
        ],
        "watermark": "coalesce",
        "id_type": "int",
    },

    "technician_requests": {
        "columns": [
            "id",
            "user_id",
            "issueDescription",
            "source",
            "screen_issue",
            "status",
            "incident_id",
            "created_at",
            "updated_at",
        ],
        "watermark": "coalesce",
        "id_type": "int",
    },

    "troubleshoot_outcomes": {
        "columns": [
            "id",
            "user_id",
            "location",
            "model_id",
            "model_name",
            "issue_id",
            "issue_label",
            "outcome",
            "created_at",
            "session_id",
            "support_mode",
            "is_final",
            "video_watched",
            "steps_completed",
            "total_steps",
            "last_step_id",
        ],
        "watermark": "created_at",
        "id_type": "str",
    },

    "support_incidents": {
        "columns": [
            "id",
            "issue_key",
            "issue_label",
            "location",
            "status",
            "report_count",
            "distinct_subscribers",
            "first_reported_at",
            "last_reported_at",
            "confirmed_at",
            "resolved_at",
            "dismissed_at",
            "created_at",
            "updated_at",
        ],
        "watermark": "coalesce",
        "id_type": "str",
    },
}


# ============================================================
# TIME HELPERS
# ============================================================

def utc_now():
    return datetime.now(timezone.utc)


def iso(value):
    if value is None:
        return None

    if isinstance(value, datetime):
        return value.isoformat()

    return str(value)


# ============================================================
# DIRECTORIES
# ============================================================

def ensure_directories():

    EXTRACT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    STATE_DIR.mkdir(
        parents=True,
        exist_ok=True
    )


# ============================================================
# WATERMARK STATE
# ============================================================

def load_state():

    if not STATE_FILE.exists():
        return {}

    with STATE_FILE.open(
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


def save_state(state):

    temporary_file = STATE_FILE.with_suffix(".tmp")

    with temporary_file.open(
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            state,
            file,
            indent=2
        )

    temporary_file.replace(STATE_FILE)


# ============================================================
# EXTRACTION LOG
# ============================================================

def ensure_log():

    if LOG_FILE.exists():
        return

    with LOG_FILE.open(
        "w",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.writer(file)

        writer.writerow([
            "batch_id",
            "table_name",
            "mode",
            "extracted_rows",
            "started_at",
            "finished_at",
            "watermark_expression",
            "new_watermark",
            "new_watermark_id",
            "status",
            "output_file",
        ])


def append_log(values):

    with LOG_FILE.open(
        "a",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.writer(file)

        writer.writerow(values)


# ============================================================
# CSV SERIALIZATION
# ============================================================

def serialize(value):

    if value is None:
        return ""

    if isinstance(value, datetime):
        return value.isoformat()

    return str(value)


# ============================================================
# WATERMARK SQL
# ============================================================

def build_watermark_expression(config):

    if config["watermark"] == "created_at":

        return sql.Identifier(
            "created_at"
        )

    return sql.SQL(
        "COALESCE({}, {})"
    ).format(
        sql.Identifier("updated_at"),
        sql.Identifier("created_at"),
    )


def watermark_label(config):

    if config["watermark"] == "created_at":
        return "created_at"

    return "COALESCE(updated_at, created_at)"


# ============================================================
# STATE ID CONVERSION
# ============================================================

def convert_state_id(value, id_type):

    if value is None:
        return None

    if id_type == "int":
        return int(value)

    return str(value)


# ============================================================
# EXTRACT ONE TABLE
# ============================================================

def extract_table(
    cur,
    table_name,
    config,
    state,
    batch_id,
    full_refresh=False,
):

    started = utc_now()

    columns = config["columns"]

    id_column = "id"

    # --------------------------------------------------------
    # Build quoted identifiers.
    #
    # This correctly handles mixed-case:
    #
    # "issueDescription"
    # --------------------------------------------------------

    column_list = sql.SQL(", ").join(
        sql.Identifier(column)
        for column in columns
    )

    table_identifier = sql.Identifier(
        "public",
        table_name
    )

    watermark_expression = (
        build_watermark_expression(config)
    )

    watermark_sql_label = watermark_label(
        config
    )

    previous = None

    if not full_refresh:

        previous = state.get(
            table_name
        )


    # ========================================================
    # INCREMENTAL EXTRACTION
    # ========================================================

    if previous:

        last_timestamp = datetime.fromisoformat(
            previous["watermark"]
        )

        last_id = convert_state_id(
            previous["id"],
            config["id_type"]
        )

        query = sql.SQL("""
            SELECT
                {columns},
                {watermark} AS __etl_watermark

            FROM {table}

            WHERE
                ({watermark}) > %s

                OR

                (
                    ({watermark}) = %s
                    AND {id_column} > %s
                )

            ORDER BY
                ({watermark}) ASC,
                {id_column} ASC

        """).format(

            columns=column_list,

            table=table_identifier,

            watermark=watermark_expression,

            id_column=sql.Identifier(
                id_column
            ),
        )

        cur.execute(
            query,
            (
                last_timestamp,
                last_timestamp,
                last_id,
            )
        )

        mode = "incremental"


    # ========================================================
    # INITIAL FULL EXTRACTION
    # ========================================================

    else:

        query = sql.SQL("""
            SELECT
                {columns},
                {watermark} AS __etl_watermark

            FROM {table}

            ORDER BY
                ({watermark}) ASC,
                {id_column} ASC

        """).format(

            columns=column_list,

            table=table_identifier,

            watermark=watermark_expression,

            id_column=sql.Identifier(
                id_column
            ),
        )

        cur.execute(query)

        mode = "full_initial"


    # ========================================================
    # FETCH ROWS
    # ========================================================

    rows = cur.fetchall()


    # ========================================================
    # DETERMINE WATERMARK
    #
    # IMPORTANT:
    #
    # The last value is now the calculated
    # __etl_watermark, NOT simply updated_at.
    # ========================================================

    watermark_index = len(columns)

    new_watermark = None
    new_id = None

    if rows:

        new_watermark = rows[-1][
            watermark_index
        ]

        new_id = rows[-1][0]

        if new_watermark is None:

            raise RuntimeError(
                f"{table_name}: "
                "calculated ETL watermark is NULL."
            )


    # ========================================================
    # OUTPUT FILE
    # ========================================================

    batch_stamp = utc_now().strftime(
        "%Y%m%dT%H%M%S%fZ"
    )

    output_path = (
        EXTRACT_DIR
        / f"{batch_stamp}_{table_name}.csv"
    )


    # ========================================================
    # WRITE CSV
    #
    # IMPORTANT:
    # __etl_watermark is NOT written to the CSV.
    # Only approved source columns are exported.
    # ========================================================

    with output_path.open(
        "w",
        newline="",
        encoding="utf-8-sig"
    ) as file:

        writer = csv.writer(file)

        writer.writerow(columns)

        for row in rows:

            writer.writerow([
                serialize(value)
                for value in row[:len(columns)]
            ])


    finished = utc_now()


    # ========================================================
    # SAVE WATERMARK
    # ONLY AFTER SUCCESSFUL FILE CREATION
    # ========================================================

    if rows:

        state[table_name] = {

            "watermark": iso(
                new_watermark
            ),

            "id": serialize(
                new_id
            ),

            "watermark_expression": (
                watermark_sql_label
            ),

            "updated_at": iso(
                finished
            ),
        }


    # ========================================================
    # LOG
    # ========================================================

    append_log([

        batch_id,

        table_name,

        mode,

        len(rows),

        iso(started),

        iso(finished),

        watermark_sql_label,

        iso(new_watermark),

        serialize(new_id),

        "SUCCESS",

        str(
            output_path.relative_to(
                BASE_DIR
            )
        ),
    ])


    return (
        len(rows),
        output_path
    )


# ============================================================
# MAIN
# ============================================================

def main():

    parser = argparse.ArgumentParser(
        description=(
            "CignalCare+ Lab 3 "
            "incremental source extraction"
        )
    )

    parser.add_argument(
        "--full",
        action="store_true",
        help=(
            "Ignore saved watermarks "
            "and perform a full extraction."
        ),
    )

    parser.add_argument(
        "--table",
        choices=sorted(
            TABLES.keys()
        ),
        help=(
            "Extract only one source table."
        ),
    )

    args = parser.parse_args()


    # ========================================================
    # ENVIRONMENT
    # ========================================================

    load_dotenv(BASE_DIR / ".env")

    database_url = os.getenv(
        "DATABASE_URL"
    )

    if not database_url:

        raise SystemExit(
            "❌ DATABASE_URL was not found in .env"
        )


    # ========================================================
    # PREPARE
    # ========================================================

    ensure_directories()

    ensure_log()

    state = load_state()

    batch_id = utc_now().strftime(
        "%Y%m%dT%H%M%S%fZ"
    )


    if args.table:

        selected_tables = [
            args.table
        ]

    else:

        selected_tables = list(
            TABLES.keys()
        )


    # ========================================================
    # HEADER
    # ========================================================

    print("=" * 78)

    print(
        "CignalCare+ LAB 3 - "
        "INCREMENTAL SOURCE EXTRACTION"
    )

    print("=" * 78)

    print(
        f"Batch ID: {batch_id}"
    )

    print(
        "Mode:",
        "FULL" if args.full
        else "INITIAL / INCREMENTAL"
    )

    print()


    total_rows = 0


    # ========================================================
    # CONNECTION
    # ========================================================

    try:

        with psycopg.connect(
            database_url,
            connect_timeout=15,
            sslmode=os.getenv(
                "DB_SSLMODE",
                "require"
            )
        ) as conn:

            print(
                "✅ PostgreSQL/Supabase "
                "connection successful\n"
            )

            with conn.cursor() as cur:

                for table_name in selected_tables:

                    print(
                        "-" * 78
                    )

                    print(
                        f"Extracting: "
                        f"{table_name}"
                    )

                    try:

                        count, output_path = (
                            extract_table(

                                cur,

                                table_name,

                                TABLES[
                                    table_name
                                ],

                                state,

                                batch_id,

                                full_refresh=args.full,
                            )
                        )

                        save_state(
                            state
                        )

                        total_rows += count

                        print(
                            f"Rows extracted: "
                            f"{count:,}"
                        )

                        print(
                            f"Output: "
                            f"{output_path}"
                        )


                    except Exception as error:

                        append_log([

                            batch_id,

                            table_name,

                            "failed",

                            0,

                            iso(
                                utc_now()
                            ),

                            iso(
                                utc_now()
                            ),

                            "",

                            "",

                            "",

                            (
                                f"FAILED: "
                                f"{type(error).__name__}: "
                                f"{error}"
                            ),

                            "",
                        ])

                        raise


    except Exception as error:

        print()

        print(
            "=" * 78
        )

        print(
            "❌ EXTRACTION FAILED"
        )

        print(
            "=" * 78
        )

        print(
            f"Error type: "
            f"{type(error).__name__}"
        )

        print(
            f"Message: "
            f"{error}"
        )

        raise SystemExit(1)


    # ========================================================
    # SUCCESS
    # ========================================================

    print()

    print(
        "=" * 78
    )

    print(
        "✅ EXTRACTION COMPLETE"
    )

    print(
        "=" * 78
    )

    print(
        f"Tables processed: "
        f"{len(selected_tables)}"
    )

    print(
        f"Total rows extracted: "
        f"{total_rows:,}"
    )

    print(
        f"Extracted files: "
        f"{EXTRACT_DIR}"
    )

    print(
        f"Watermarks: "
        f"{STATE_FILE}"
    )

    print(
        f"Execution log: "
        f"{LOG_FILE}"
    )

    print(
        "=" * 78
    )


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()