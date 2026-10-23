import csv
import os
from collections import Counter
from datetime import datetime


# ============================================================
# CignalCare+ LAB 4
# TRANSFORMATION INPUT PROFILER
#
# Purpose:
# Profile the exact validated Lab 3 handover batch before
# defining any cleaning, standardization, or transformation
# rules.
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.dirname(os.path.abspath(__file__))
    )
)

EXTRACTED_DIR = os.path.join(BASE_DIR, "data", "extracted")

HANDOVER_FILES = {
    "users": "20261018T170820480125Z_users.csv",
    "prepaid_plans": "20261018T170820529585Z_prepaid_plans.csv",
    "prepaid_transactions": "20261018T170820579959Z_prepaid_transactions.csv",
    "load_requests": "20261018T170820632050Z_load_requests.csv",
    "tickets": "20261018T170820680479Z_tickets.csv",
    "technician_requests": "20261018T170820721949Z_technician_requests.csv",
    "troubleshoot_outcomes": "20261018T170820768165Z_troubleshoot_outcomes.csv",
    "support_incidents": "20261018T170820809640Z_support_incidents.csv",
}

EXPECTED_BATCH_ID = "20261018T170820026121Z"


def is_blank(value):
    return value is None or value.strip() == ""


def looks_like_datetime(value):
    if not value:
        return False

    value = value.strip()

    formats = [
        "%Y-%m-%d",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %H:%M:%S.%f",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%dT%H:%M:%S.%f",
        "%Y-%m-%dT%H:%M:%S%z",
        "%Y-%m-%dT%H:%M:%S.%f%z",
    ]

    for fmt in formats:
        try:
            datetime.strptime(value, fmt)
            return True
        except ValueError:
            continue

    return False


def looks_like_integer(value):
    try:
        int(value)
        return True
    except (ValueError, TypeError):
        return False


def looks_like_float(value):
    try:
        float(value)
        return True
    except (ValueError, TypeError):
        return False


def infer_type(values):
    values = [v.strip() for v in values if not is_blank(v)]

    if not values:
        return "EMPTY / ALL NULL"

    if all(looks_like_integer(v) for v in values):
        return "INTEGER"

    if all(looks_like_float(v) for v in values):
        return "NUMERIC"

    if all(looks_like_datetime(v) for v in values):
        return "DATE / DATETIME"

    return "TEXT"


def profile_table(table_name, filename):
    path = os.path.join(EXTRACTED_DIR, filename)

    print("=" * 78)
    print(f"TABLE: {table_name}")
    print("=" * 78)
    print(f"File: {filename}")

    if not os.path.exists(path):
        print("❌ FILE NOT FOUND")
        print()
        return None

    with open(path, "r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)

        columns = reader.fieldnames or []
        rows = list(reader)

    print(f"Columns: {len(columns)}")
    print(f"Rows: {len(rows)}")
    print()

    if not columns:
        print("❌ No columns detected.")
        print()
        return None

    print("COLUMN PROFILE")
    print("-" * 78)

    duplicate_rows = 0

    row_signatures = Counter(
        tuple(row.get(column, "") for column in columns)
        for row in rows
    )

    duplicate_rows = sum(
        count - 1
        for count in row_signatures.values()
        if count > 1
    )

    duplicate_groups = sum(
        1
        for count in row_signatures.values()
        if count > 1
    )

    primary_key_column = "id" if "id" in columns else None

    duplicate_primary_keys = 0
    null_primary_keys = 0

    if primary_key_column:
        primary_keys = [
            row.get(primary_key_column, "").strip()
            for row in rows
        ]

        null_primary_keys = sum(
            1 for value in primary_keys if value == ""
        )

        pk_counts = Counter(
            value for value in primary_keys if value != ""
        )

        duplicate_primary_keys = sum(
            count - 1
            for count in pk_counts.values()
            if count > 1
        )

    column_profiles = {}

    for column in columns:
        values = [
            row.get(column, "")
            for row in rows
        ]

        non_null_values = [
            value.strip()
            for value in values
            if not is_blank(value)
        ]

        null_count = sum(
            1 for value in values
            if is_blank(value)
        )

        blank_count = sum(
            1
            for value in values
            if value is not None and value.strip() == ""
        )

        unique_values = Counter(non_null_values)

        inferred_type = infer_type(values)

        column_profiles[column] = {
            "type": inferred_type,
            "null_count": null_count,
            "blank_count": blank_count,
            "unique_count": len(unique_values),
            "values": unique_values,
        }

        print(f"\n{column}")
        print(f"  Type:              {inferred_type}")
        print(f"  NULL/blank:        {null_count}")
        print(f"  Unique values:     {len(unique_values)}")

        # Show values only when the number of unique values is
        # reasonably small. This helps identify categorical
        # inconsistencies without dumping huge columns.
        if 0 < len(unique_values) <= 20:
            print("  Observed values:")

            for value, count in unique_values.most_common():
                print(f"    {value!r}: {count}")

    print()
    print("ROW INTEGRITY")
    print("-" * 78)
    print(f"Duplicate complete rows:       {duplicate_rows}")
    print(f"Duplicate row groups:          {duplicate_groups}")

    if primary_key_column:
        print(f"Primary key column:             {primary_key_column}")
        print(f"NULL primary keys:              {null_primary_keys}")
        print(f"Duplicate primary keys:         {duplicate_primary_keys}")
    else:
        print("Primary key column:             id not present")

    print()

    return {
        "table": table_name,
        "file": filename,
        "rows": len(rows),
        "columns": len(columns),
        "column_names": columns,
        "duplicate_rows": duplicate_rows,
        "duplicate_primary_keys": duplicate_primary_keys,
        "null_primary_keys": null_primary_keys,
        "column_profiles": column_profiles,
    }


def main():
    print("=" * 78)
    print("CignalCare+ LAB 4 - TRANSFORMATION INPUT PROFILING")
    print("=" * 78)
    print(f"Expected Lab 3 handover batch: {EXPECTED_BATCH_ID}")
    print(f"Input directory: {EXTRACTED_DIR}")
    print()
    print("IMPORTANT:")
    print("This profiler reads ONLY the validated Lab 3 handover files.")
    print("No PostgreSQL/Supabase connection is used.")
    print()

    results = []

    for table_name, filename in HANDOVER_FILES.items():
        result = profile_table(table_name, filename)

        if result:
            results.append(result)

    print("=" * 78)
    print("PROFILE SUMMARY")
    print("=" * 78)

    total_rows = 0
    total_columns = 0

    for result in results:
        total_rows += result["rows"]
        total_columns += result["columns"]

        print(
            f"{result['table']:<25} "
            f"rows={result['rows']:<5} "
            f"columns={result['columns']:<3} "
            f"duplicate_rows={result['duplicate_rows']:<3} "
            f"duplicate_ids={result['duplicate_primary_keys']:<3} "
            f"null_ids={result['null_primary_keys']:<3}"
        )

    print()
    print(f"Tables profiled: {len(results)}")
    print(f"Total records profiled: {total_rows}")
    print(f"Total columns profiled: {total_columns}")
    print()

    if len(results) == 8 and total_rows == 478:
        print("✅ EXPECTED HANDOVER BASELINE CONFIRMED")
        print("8 tables and 478 records were profiled.")
    else:
        print("⚠️ HANDOVER BASELINE DOES NOT MATCH EXPECTED VALUES")
        print("Do not continue to transformation rules until reviewed.")

    print()
    print("=" * 78)
    print("PROFILE COMPLETE")
    print("=" * 78)


if __name__ == "__main__":
    main()