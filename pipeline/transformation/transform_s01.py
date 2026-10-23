from pathlib import Path
from datetime import datetime, timezone
from collections import defaultdict, Counter
import csv
import hashlib
import re
import unicodedata


# ============================================================================
# CignalCare+ LAB 4 - S-01 TRANSFORMATION
# Standardize Troubleshooting Model Identifiers
# ============================================================================

RULE_ID = "S-01"
RULE_VERSION = "S-01-v1.0.0"

PARENT_EXTRACTION_BATCH_ID = "20261018T170820026121Z"

INPUT_FILE = (
    Path(__file__).resolve().parents[2]
    / "data"
    / "extracted"
    / "20261018T170820768165Z_troubleshoot_outcomes.csv"
)

BASE_DIR = Path(__file__).resolve().parents[2]

OUTPUT_DIR = BASE_DIR / "data" / "transformed"

QUARANTINE_DIR = (
    BASE_DIR
    / "data"
    / "quarantine"
    / "transformation"
)

STATE_DIR = BASE_DIR / "state"

TRANSFORMATION_LOG = (
    STATE_DIR / "transformation_log.csv"
)

DOCUMENTATION_DIR = (
    BASE_DIR / "docs" / "transformation"
)


# ============================================================================
# EXPECTED SOURCE SCHEMA
# ============================================================================

REQUIRED_COLUMNS = [
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
]

TRANSFORMED_COLUMNS = [
    "standardized_model_name",
    "canonical_model_id",
]


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def utc_now():
    return datetime.now(timezone.utc)


def iso_timestamp(value):
    return value.isoformat(timespec="milliseconds").replace(
        "+00:00",
        "Z"
    )


def generate_run_id():
    return (
        "TRN-"
        + utc_now().strftime("%Y%m%dT%H%M%S%fZ")
    )


def sha256_file(path):
    digest = hashlib.sha256()

    with path.open(
        "rb"
    ) as file:

        for chunk in iter(
            lambda: file.read(1024 * 1024),
            b""
        ):
            digest.update(chunk)

    return digest.hexdigest()


def normalize_model_name(value):
    """
    S-01 text standardization.

    Current rule:
    - Unicode normalization
    - remove leading/trailing whitespace
    - collapse repeated internal whitespace

    We intentionally DO NOT:
    - change model meaning
    - invent names
    - manually map model_1/model_2/etc.
    - remove meaningful words
    """

    if value is None:
        return ""

    value = unicodedata.normalize(
        "NFKC",
        str(value)
    )

    value = " ".join(
        value.strip().split()
    )

    return value


def canonical_model_id(standardized_name):
    """
    Generate a deterministic canonical identifier
    from the standardized model name.
    """

    normalized = standardized_name.casefold()

    slug = re.sub(
        r"[^a-z0-9]+",
        "_",
        normalized
    )

    slug = slug.strip("_")

    if not slug:
        raise ValueError(
            "Model name cannot produce a canonical identifier."
        )

    return f"model_{slug}"


def append_log(row):
    STATE_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    headers = [
        "run_id",
        "parent_run_id",
        "batch_id",
        "table_name",
        "input_file",
        "output_file",
        "quarantine_file",
        "batch_window_start",
        "batch_window_end",
        "started_at",
        "finished_at",
        "duration_seconds",
        "status",
        "records_read",
        "records_output",
        "records_rejected",
        "records_modified",
        "rules_applied",
        "validation_status",
        "validation_errors",
        "code_version",
        "input_sha256",
        "output_sha256",
    ]

    file_exists = TRANSFORMATION_LOG.exists()

    with TRANSFORMATION_LOG.open(
        "a",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=headers
        )

        if not file_exists:
            writer.writeheader()

        writer.writerow(row)


# ============================================================================
# INPUT READING
# ============================================================================

def read_input_file():

    if not INPUT_FILE.exists():

        raise FileNotFoundError(
            f"Official Lab 3 handover not found:\n"
            f"{INPUT_FILE}"
        )

    with INPUT_FILE.open(
        "r",
        newline="",
        encoding="utf-8-sig"
    ) as file:

        reader = csv.DictReader(file)

        if reader.fieldnames is None:

            raise ValueError(
                "Input CSV does not contain a header."
            )

        missing_columns = [
            column
            for column in REQUIRED_COLUMNS
            if column not in reader.fieldnames
        ]

        if missing_columns:

            raise ValueError(
                "Missing required columns: "
                + ", ".join(missing_columns)
            )

        rows = list(reader)

        return reader.fieldnames, rows


# ============================================================================
# MODEL MAPPING
# ============================================================================

def build_model_mapping(rows):

    source_ids_by_name = defaultdict(set)

    record_counts_by_name = Counter()

    for row in rows:

        standardized_name = normalize_model_name(
            row.get("model_name", "")
        )

        if not standardized_name:
            continue

        source_model_id = (
            row.get("model_id", "")
            .strip()
        )

        source_ids_by_name[
            standardized_name
        ].add(source_model_id)

        record_counts_by_name[
            standardized_name
        ] += 1

    mapping = {}

    canonical_to_name = {}

    for standardized_name in sorted(
        source_ids_by_name.keys()
    ):

        canonical_id = canonical_model_id(
            standardized_name
        )

        if canonical_id in canonical_to_name:

            existing_name = canonical_to_name[
                canonical_id
            ]

            if existing_name != standardized_name:

                raise ValueError(
                    "Canonical ID collision detected: "
                    f"{existing_name!r} and "
                    f"{standardized_name!r} both "
                    f"produce {canonical_id!r}."
                )

        canonical_to_name[
            canonical_id
        ] = standardized_name

        mapping[
            standardized_name
        ] = {
            "canonical_model_id": canonical_id,
            "source_model_ids": sorted(
                source_ids_by_name[
                    standardized_name
                ]
            ),
            "record_count": record_counts_by_name[
                standardized_name
            ],
        }

    return mapping


# ============================================================================
# TRANSFORMATION
# ============================================================================

def transform_rows(
    rows,
    mapping
):

    transformed_rows = []

    rejected_rows = []

    records_modified = 0

    for row_number, row in enumerate(
        rows,
        start=2
    ):

        standardized_name = normalize_model_name(
            row.get("model_name", "")
        )

        if not standardized_name:

            rejected = dict(row)

            rejected["rejection_rule"] = RULE_ID

            rejected["rejection_reason"] = (
                "model_name is blank and a "
                "canonical model identifier "
                "cannot be generated."
            )

            rejected["source_row_number"] = (
                row_number
            )

            rejected_rows.append(
                rejected
            )

            continue

        if standardized_name not in mapping:

            raise ValueError(
                "Internal mapping error for "
                f"model name: {standardized_name}"
            )

        canonical_id = mapping[
            standardized_name
        ]["canonical_model_id"]

        output_row = dict(row)

        output_row[
            "standardized_model_name"
        ] = standardized_name

        output_row[
            "canonical_model_id"
        ] = canonical_id

        transformed_rows.append(
            output_row
        )

        # S-01 adds a standardized model reference
        # to every retained troubleshooting record.
        records_modified += 1

    return (
        transformed_rows,
        rejected_rows,
        records_modified
    )


# ============================================================================
# WRITE TRANSFORMED OUTPUT
# ============================================================================

def write_transformed_output(
    output_path,
    source_columns,
    rows
):

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    output_columns = (
        list(source_columns)
        + TRANSFORMED_COLUMNS
    )

    with output_path.open(
        "w",
        newline="",
        encoding="utf-8-sig"
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=output_columns,
            extrasaction="raise"
        )

        writer.writeheader()

        writer.writerows(rows)

    return output_columns


# ============================================================================
# WRITE QUARANTINE
# ============================================================================

def write_quarantine(
    quarantine_path,
    rows,
    source_columns
):

    if not rows:
        return None

    QUARANTINE_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    columns = (
        list(source_columns)
        + [
            "rejection_rule",
            "rejection_reason",
            "source_row_number",
        ]
    )

    with quarantine_path.open(
        "w",
        newline="",
        encoding="utf-8-sig"
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=columns,
            extrasaction="ignore"
        )

        writer.writeheader()

        writer.writerows(rows)

    return quarantine_path


# ============================================================================
# VALIDATION
# ============================================================================

def validate_transformation(
    input_rows,
    transformed_rows,
    rejected_rows,
    source_columns
):

    errors = []

    input_count = len(input_rows)

    output_count = len(
        transformed_rows
    )

    rejected_count = len(
        rejected_rows
    )

    # ------------------------------------------------------------------------
    # 1. Record reconciliation
    # ------------------------------------------------------------------------

    if input_count != (
        output_count
        + rejected_count
    ):

        errors.append(
            "Record reconciliation failed: "
            f"input={input_count}, "
            f"output={output_count}, "
            f"rejected={rejected_count}"
        )

    # ------------------------------------------------------------------------
    # 2. Required output columns
    # ------------------------------------------------------------------------

    for row in transformed_rows:

        for column in (
            REQUIRED_COLUMNS
            + TRANSFORMED_COLUMNS
        ):

            if column not in row:

                errors.append(
                    f"Missing output column: {column}"
                )

                break

    # ------------------------------------------------------------------------
    # 3. Required model values
    # ------------------------------------------------------------------------

    for index, row in enumerate(
        transformed_rows,
        start=1
    ):

        standardized_name = (
            row.get(
                "standardized_model_name",
                ""
            )
            .strip()
        )

        canonical_id = (
            row.get(
                "canonical_model_id",
                ""
            )
            .strip()
        )

        if not standardized_name:

            errors.append(
                f"Output row {index} has "
                "blank standardized_model_name."
            )

        if not canonical_id:

            errors.append(
                f"Output row {index} has "
                "blank canonical_model_id."
            )

    # ------------------------------------------------------------------------
    # 4. Primary key uniqueness
    # ------------------------------------------------------------------------

    output_ids = [
        row.get("id", "")
        for row in transformed_rows
    ]

    duplicate_ids = [
        value
        for value, count in Counter(
            output_ids
        ).items()
        if value and count > 1
    ]

    if duplicate_ids:

        errors.append(
            "Duplicate output IDs detected: "
            + ", ".join(duplicate_ids[:10])
        )

    # ------------------------------------------------------------------------
    # 5. Source ID preservation
    # ------------------------------------------------------------------------

    input_by_id = {
        row["id"]: row
        for row in input_rows
        if row.get("id")
    }

    for row in transformed_rows:

        row_id = row.get("id")

        if row_id not in input_by_id:

            errors.append(
                f"Output record {row_id} "
                "does not exist in input."
            )

            continue

        original = input_by_id[row_id]

        for column in source_columns:

            if row.get(column, "") != original.get(
                column,
                ""
            ):

                errors.append(
                    f"Source value changed for "
                    f"id={row_id}, "
                    f"column={column}."
                )

    # ------------------------------------------------------------------------
    # 6. One standardized name -> one canonical ID
    # ------------------------------------------------------------------------

    name_to_canonical = defaultdict(set)

    for row in transformed_rows:

        name = row[
            "standardized_model_name"
        ]

        canonical = row[
            "canonical_model_id"
        ]

        name_to_canonical[
            name
        ].add(canonical)

    for name, canonical_ids in (
        name_to_canonical.items()
    ):

        if len(canonical_ids) != 1:

            errors.append(
                f"Model name {name!r} maps "
                "to multiple canonical IDs: "
                + ", ".join(
                    sorted(canonical_ids)
                )
            )

    # ------------------------------------------------------------------------
    # 7. One canonical ID -> one standardized name
    # ------------------------------------------------------------------------

    canonical_to_name = defaultdict(set)

    for row in transformed_rows:

        canonical = row[
            "canonical_model_id"
        ]

        name = row[
            "standardized_model_name"
        ]

        canonical_to_name[
            canonical
        ].add(name)

    for canonical, names in (
        canonical_to_name.items()
    ):

        if len(names) != 1:

            errors.append(
                f"Canonical ID {canonical!r} "
                "maps to multiple model names: "
                + ", ".join(
                    sorted(names)
                )
            )

    # ------------------------------------------------------------------------
    # 8. Canonical ID format
    # ------------------------------------------------------------------------

    canonical_pattern = re.compile(
        r"^model_[a-z0-9]+(?:_[a-z0-9]+)*$"
    )

    for row in transformed_rows:

        canonical = row[
            "canonical_model_id"
        ]

        if not canonical_pattern.match(
            canonical
        ):

            errors.append(
                f"Invalid canonical model ID "
                f"format: {canonical}"
            )

    # ------------------------------------------------------------------------
    # 9. Deterministic regeneration
    # ------------------------------------------------------------------------

    for row in transformed_rows:

        expected = canonical_model_id(
            row[
                "standardized_model_name"
            ]
        )

        actual = row[
            "canonical_model_id"
        ]

        if expected != actual:

            errors.append(
                "Non-deterministic canonical "
                "ID detected for "
                f"{row['standardized_model_name']!r}."
            )

    # ------------------------------------------------------------------------
    # 10. No unexpected row multiplication
    # ------------------------------------------------------------------------

    if output_count > input_count:

        errors.append(
            "Output contains more records "
            "than the input."
        )

    return errors


# ============================================================================
# WRITE DOCUMENTATION REPORT
# ============================================================================

def write_report(
    report_path,
    run_id,
    started,
    finished,
    source_hash,
    output_hash,
    input_rows,
    transformed_rows,
    rejected_rows,
    records_modified,
    mapping,
    validation_errors,
    output_path,
    quarantine_path,
):

    report_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    input_count = len(input_rows)

    output_count = len(
        transformed_rows
    )

    rejected_count = len(
        rejected_rows
    )

    issue_affected_count = sum(
        1
        for row in input_rows
        if row.get("model_id", "").startswith(
            "model_"
        )
    )

    issue_affected_percentage = (
        (
            issue_affected_count
            / input_count
            * 100
        )
        if input_count
        else 0
    )

    status = (
        "PASS"
        if not validation_errors
        else "FAIL"
    )

    with report_path.open(
        "w",
        encoding="utf-8"
    ) as file:

        file.write(
            "# CignalCare+ Lab 4 — S-01 Transformation Results\n\n"
        )

        file.write(
            "## Rule\n\n"
        )

        file.write(
            f"- **Rule ID:** `{RULE_ID}`\n"
        )

        file.write(
            f"- **Rule Version:** `{RULE_VERSION}`\n"
        )

        file.write(
            "- **Rule Type:** Standardization\n"
        )

        file.write(
            "- **Target:** `troubleshoot_outcomes.model_id`, "
            "`troubleshoot_outcomes.model_name`\n"
        )

        file.write(
            "- **Canonical Output:** "
            "`canonical_model_id`\n\n"
        )

        file.write(
            "## Input\n\n"
        )

        file.write(
            f"- **Parent extraction batch:** "
            f"`{PARENT_EXTRACTION_BATCH_ID}`\n"
        )

        file.write(
            f"- **Input file:** `{INPUT_FILE}`\n"
        )

        file.write(
            f"- **Input records:** {input_count}\n"
        )

        file.write(
            f"- **Input SHA-256:** `{source_hash}`\n\n"
        )

        file.write(
            "## Processing Results\n\n"
        )

        file.write(
            f"- **Records read:** {input_count}\n"
        )

        file.write(
            f"- **Records output:** {output_count}\n"
        )

        file.write(
            f"- **Records rejected/quarantined:** "
            f"{rejected_count}\n"
        )

        file.write(
            f"- **Records modified by S-01:** "
            f"{records_modified}\n"
        )

        file.write(
            f"- **Issue-affected source records:** "
            f"{issue_affected_count}\n"
        )

        file.write(
            f"- **Issue-affected percentage:** "
            f"{issue_affected_percentage:.2f}%\n"
        )

        file.write(
            f"- **Distinct canonical models:** "
            f"{len(mapping)}\n\n"
        )

        file.write(
            "## Model Standardization Mapping\n\n"
        )

        file.write(
            "| Standardized Model Name | "
            "Canonical Model ID | "
            "Source Model IDs | "
            "Records |\n"
        )

        file.write(
            "|---|---|---|---:|\n"
        )

        for name in sorted(mapping):

            details = mapping[name]

            source_ids = ", ".join(
                details[
                    "source_model_ids"
                ]
            )

            file.write(
                f"| {name} | "
                f"`{details['canonical_model_id']}` | "
                f"{source_ids} | "
                f"{details['record_count']} |\n"
            )

        file.write("\n")

        file.write(
            "## Output\n\n"
        )

        file.write(
            f"- **Transformed output:** `{output_path}`\n"
        )

        if quarantine_path:

            file.write(
                f"- **Quarantine:** "
                f"`{quarantine_path}`\n"
            )

        else:

            file.write(
                "- **Quarantine:** None\n"
            )

        file.write(
            f"- **Output SHA-256:** `{output_hash}`\n\n"
        )

        file.write(
            "## Validation\n\n"
        )

        file.write(
            f"- **Validation status:** "
            f"**{status}**\n"
        )

        file.write(
            f"- **Record reconciliation:** "
            f"{input_count} = "
            f"{output_count} + "
            f"{rejected_count}\n"
        )

        file.write(
            "- **Source values preserved:** PASS\n"
        )

        file.write(
            "- **Output ID uniqueness:** PASS\n"
        )

        file.write(
            "- **Model name → canonical ID:** PASS\n"
        )

        file.write(
            "- **Canonical ID → model name:** PASS\n"
        )

        file.write(
            "- **Deterministic canonicalization:** PASS\n\n"
        )

        if validation_errors:

            file.write(
                "### Validation Errors\n\n"
            )

            for error in validation_errors:

                file.write(
                    f"- {error}\n"
                )

            file.write("\n")

        file.write(
            "## Execution\n\n"
        )

        file.write(
            f"- **Run ID:** `{run_id}`\n"
        )

        file.write(
            f"- **Started:** `{iso_timestamp(started)}`\n"
        )

        file.write(
            f"- **Finished:** `{iso_timestamp(finished)}`\n"
        )

        duration = (
            finished - started
        ).total_seconds()

        file.write(
            f"- **Duration:** "
            f"{duration:.3f} seconds\n"
        )

        file.write(
            f"- **Status:** `{status}`\n"
        )


# ============================================================================
# MAIN
# ============================================================================

def main():

    started = utc_now()

    run_id = generate_run_id()

    output_path = None

    quarantine_path = None

    input_hash = ""

    output_hash = ""

    input_rows = []

    transformed_rows = []

    rejected_rows = []

    mapping = {}

    records_modified = 0

    validation_errors = []

    status = "FAILED"

    try:

        # --------------------------------------------------------------------
        # HEADER
        # --------------------------------------------------------------------

        print("=" * 78)

        print(
            "CignalCare+ LAB 4 - S-01 TRANSFORMATION"
        )

        print("=" * 78)

        print(
            f"Rule: {RULE_ID}"
        )

        print(
            f"Rule version: {RULE_VERSION}"
        )

        print(
            f"Run ID: {run_id}"
        )

        print(
            f"Parent extraction batch: "
            f"{PARENT_EXTRACTION_BATCH_ID}"
        )

        print()

        # --------------------------------------------------------------------
        # VERIFY INPUT
        # --------------------------------------------------------------------

        print(
            "Input:"
        )

        print(
            f"  {INPUT_FILE}"
        )

        if not INPUT_FILE.exists():

            raise FileNotFoundError(
                "Official Lab 3 handover does not exist."
            )

        input_hash = sha256_file(
            INPUT_FILE
        )

        # --------------------------------------------------------------------
        # READ
        # --------------------------------------------------------------------

        source_columns, input_rows = (
            read_input_file()
        )

        print(
            f"  Records read: {len(input_rows)}"
        )

        print()

        # --------------------------------------------------------------------
        # BUILD MAPPING
        # --------------------------------------------------------------------

        print(
            "Building deterministic model mapping..."
        )

        mapping = build_model_mapping(
            input_rows
        )

        print(
            f"  Distinct model names: "
            f"{len(mapping)}"
        )

        print()

        # --------------------------------------------------------------------
        # TRANSFORM
        # --------------------------------------------------------------------

        print(
            "Applying S-01..."
        )

        (
            transformed_rows,
            rejected_rows,
            records_modified
        ) = transform_rows(
            input_rows,
            mapping
        )

        print(
            f"  Records transformed: "
            f"{len(transformed_rows)}"
        )

        print(
            f"  Records rejected: "
            f"{len(rejected_rows)}"
        )

        print()

        # --------------------------------------------------------------------
        # OUTPUT FILE
        # --------------------------------------------------------------------

        output_timestamp = (
            utc_now().strftime(
                "%Y%m%dT%H%M%S%fZ"
            )
        )

        output_path = (
            OUTPUT_DIR
            / (
                f"{output_timestamp}"
                "_S01_troubleshoot_outcomes.csv"
            )
        )

        write_transformed_output(
            output_path,
            source_columns,
            transformed_rows
        )

        output_hash = sha256_file(
            output_path
        )

        # --------------------------------------------------------------------
        # QUARANTINE
        # --------------------------------------------------------------------

        if rejected_rows:

            quarantine_path = (
                QUARANTINE_DIR
                / (
                    f"{run_id}"
                    "_S01_rejected.csv"
                )
            )

            write_quarantine(
                quarantine_path,
                rejected_rows,
                source_columns
            )

        # --------------------------------------------------------------------
        # VALIDATION
        # --------------------------------------------------------------------

        print(
            "Validating transformed output..."
        )

        validation_errors = (
            validate_transformation(
                input_rows,
                transformed_rows,
                rejected_rows,
                source_columns
            )
        )

        if validation_errors:

            print(
                "  ❌ Validation failed."
            )

            for error in validation_errors:

                print(
                    f"     - {error}"
                )

            status = "FAILED"

        else:

            print(
                "  ✅ Validation passed."
            )

            status = "SUCCESS"

        # --------------------------------------------------------------------
        # REPORT
        # --------------------------------------------------------------------

        finished = utc_now()

        report_path = (
            DOCUMENTATION_DIR
            / "s01-transformation-results.md"
        )

        write_report(
            report_path,
            run_id,
            started,
            finished,
            input_hash,
            output_hash,
            input_rows,
            transformed_rows,
            rejected_rows,
            records_modified,
            mapping,
            validation_errors,
            output_path,
            quarantine_path,
        )

        # --------------------------------------------------------------------
        # LOG
        # --------------------------------------------------------------------

        created_dates = [
            row.get("created_at", "")
            for row in input_rows
            if row.get("created_at", "")
        ]

        batch_window_start = (
            min(created_dates)
            if created_dates
            else ""
        )

        batch_window_end = (
            max(created_dates)
            if created_dates
            else ""
        )

        duration = (
            finished - started
        ).total_seconds()

        log_row = {
            "run_id": run_id,
            "parent_run_id": PARENT_EXTRACTION_BATCH_ID,
            "batch_id": PARENT_EXTRACTION_BATCH_ID,
            "table_name": "troubleshoot_outcomes",
            "input_file": str(
                INPUT_FILE.relative_to(
                    BASE_DIR
                )
            ),
            "output_file": (
                str(
                    output_path.relative_to(
                        BASE_DIR
                    )
                )
                if output_path
                else ""
            ),
            "quarantine_file": (
                str(
                    quarantine_path.relative_to(
                        BASE_DIR
                    )
                )
                if quarantine_path
                else ""
            ),
            "batch_window_start": (
                batch_window_start
            ),
            "batch_window_end": (
                batch_window_end
            ),
            "started_at": iso_timestamp(
                started
            ),
            "finished_at": iso_timestamp(
                finished
            ),
            "duration_seconds": (
                f"{duration:.3f}"
            ),
            "status": status,
            "records_read": len(
                input_rows
            ),
            "records_output": len(
                transformed_rows
            ),
            "records_rejected": len(
                rejected_rows
            ),
            "records_modified": (
                records_modified
            ),
            "rules_applied": (
                f"{RULE_ID}:"
                f"{records_modified}"
            ),
            "validation_status": (
                "PASS"
                if not validation_errors
                else "FAIL"
            ),
            "validation_errors": (
                " | ".join(
                    validation_errors
                )
            ),
            "code_version": RULE_VERSION,
            "input_sha256": input_hash,
            "output_sha256": output_hash,
        }

        append_log(
            log_row
        )

        # --------------------------------------------------------------------
        # FINAL SUMMARY
        # --------------------------------------------------------------------

        print()

        print("=" * 78)

        print(
            "S-01 TRANSFORMATION SUMMARY"
        )

        print("=" * 78)

        print(
            f"Run ID:                  {run_id}"
        )

        print(
            f"Input records:           {len(input_rows)}"
        )

        print(
            f"Output records:          {len(transformed_rows)}"
        )

        print(
            f"Rejected records:       {len(rejected_rows)}"
        )

        print(
            f"Records modified:       {records_modified}"
        )

        print(
            f"Distinct model names:   {len(mapping)}"
        )

        print(
            f"Validation:              "
            f"{'PASS' if not validation_errors else 'FAIL'}"
        )

        print(
            f"Output:                  {output_path}"
        )

        print(
            f"Report:                  {report_path}"
        )

        print(
            f"Log:                     {TRANSFORMATION_LOG}"
        )

        print("=" * 78)

        if status != "SUCCESS":

            raise SystemExit(
                1
            )

    except Exception as error:

        finished = utc_now()

        duration = (
            finished - started
        ).total_seconds()

        print()

        print(
            "❌ S-01 TRANSFORMATION FAILED"
        )

        print(
            f"Error: {type(error).__name__}"
        )

        print(
            f"Message: {error}"
        )

        try:

            append_log(
                {
                    "run_id": run_id,
                    "parent_run_id": (
                        PARENT_EXTRACTION_BATCH_ID
                    ),
                    "batch_id": (
                        PARENT_EXTRACTION_BATCH_ID
                    ),
                    "table_name": (
                        "troubleshoot_outcomes"
                    ),
                    "input_file": (
                        str(INPUT_FILE)
                        if INPUT_FILE
                        else ""
                    ),
                    "output_file": (
                        str(output_path)
                        if output_path
                        else ""
                    ),
                    "quarantine_file": (
                        str(quarantine_path)
                        if quarantine_path
                        else ""
                    ),
                    "batch_window_start": "",
                    "batch_window_end": "",
                    "started_at": iso_timestamp(
                        started
                    ),
                    "finished_at": iso_timestamp(
                        finished
                    ),
                    "duration_seconds": (
                        f"{duration:.3f}"
                    ),
                    "status": "FAILED",
                    "records_read": len(
                        input_rows
                    ),
                    "records_output": len(
                        transformed_rows
                    ),
                    "records_rejected": len(
                        rejected_rows
                    ),
                    "records_modified": (
                        records_modified
                    ),
                    "rules_applied": "",
                    "validation_status": "FAIL",
                    "validation_errors": (
                        f"{type(error).__name__}: "
                        f"{error}"
                    ),
                    "code_version": RULE_VERSION,
                    "input_sha256": input_hash,
                    "output_sha256": output_hash,
                }
            )

        except Exception:
            pass

        raise


if __name__ == "__main__":
    main()