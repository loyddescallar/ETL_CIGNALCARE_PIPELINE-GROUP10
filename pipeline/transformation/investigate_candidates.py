import csv
import os
from collections import Counter, defaultdict


# ============================================================
# CignalCare+ LAB 4
# CANDIDATE ISSUE INVESTIGATION
#
# PURPOSE:
# Investigate the candidate anomalies found during deep
# profiling before any transformation rules are created.
#
# IMPORTANT:
# - READ ONLY
# - NO DATABASE CONNECTION
# - NO DATA MODIFICATION
# - NO TRANSFORMATION
# ============================================================


BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.dirname(os.path.abspath(__file__))
    )
)

EXTRACTED_DIR = os.path.join(
    BASE_DIR,
    "data",
    "extracted"
)


FILES = {
    "prepaid_plans":
        "20261018T170820529585Z_prepaid_plans.csv",

    "technician_requests":
        "20261018T170820721949Z_technician_requests.csv",

    "troubleshoot_outcomes":
        "20261018T170820768165Z_troubleshoot_outcomes.csv",
}


def load_csv(filename):
    path = os.path.join(EXTRACTED_DIR, filename)

    with open(
        path,
        "r",
        encoding="utf-8-sig",
        newline=""
    ) as file:
        return list(csv.DictReader(file))


def show_row(row, fields):
    return {
        field: row.get(field, "")
        for field in fields
    }


# ============================================================
# LOAD
# ============================================================

plans = load_csv(
    FILES["prepaid_plans"]
)

technician_requests = load_csv(
    FILES["technician_requests"]
)

troubleshoot = load_csv(
    FILES["troubleshoot_outcomes"]
)


# ============================================================
# 1. UNUSED / SUSPICIOUS PREPAID PLAN
# ============================================================

print("=" * 78)
print("1. PREPAID PLAN CANDIDATE")
print("=" * 78)

print("All prepaid plans:")
print()

for row in plans:
    print(
        f"id={row.get('id')} | "
        f"plan_code={row.get('plan_code')} | "
        f"plan_name={row.get('plan_name')} | "
        f"amount={row.get('amount')} | "
        f"status={row.get('status')}"
    )

print()
print("Candidate:")
print()

for row in plans:
    if row.get("id") == "8":
        print(show_row(
            row,
            [
                "id",
                "plan_code",
                "plan_name",
                "amount",
                "status",
                "created_at",
                "updated_at"
            ]
        ))


# ============================================================
# 2. TECHNICIAN REQUEST CANDIDATE
# ============================================================

print()
print("=" * 78)
print("2. TECHNICIAN REQUEST CANDIDATE")
print("=" * 78)

for row in technician_requests:
    if row.get("id") == "1":
        print()
        print("Full record:")
        print()

        for key, value in row.items():
            print(f"{key}: {value!r}")


# ============================================================
# 3. MODEL ID -> MODEL NAME MAPPING
# ============================================================

print()
print("=" * 78)
print("3. MODEL ID / MODEL NAME MAPPING")
print("=" * 78)

mapping = defaultdict(Counter)

for row in troubleshoot:
    model_id = row.get(
        "model_id",
        ""
    ).strip()

    model_name = row.get(
        "model_name",
        ""
    ).strip()

    mapping[model_id][model_name] += 1


for model_id in sorted(mapping.keys()):

    print()
    print(f"{model_id}")

    for model_name, count in mapping[model_id].most_common():

        print(
            f"  {model_name!r:<40} "
            f"{count}"
        )


# ============================================================
# 4. FULL RECORDS FOR MODEL CONFLICTS
# ============================================================

print()
print("=" * 78)
print("4. MODEL CONFLICT EXAMPLES")
print("=" * 78)

conflict_ids = {
    model_id
    for model_id, names in mapping.items()
    if len(names) > 1
}

for model_id in sorted(conflict_ids):

    print()
    print(f"MODEL ID: {model_id}")

    shown = 0

    for row in troubleshoot:

        if row.get("model_id") != model_id:
            continue

        print(
            f"  id={row.get('id')} | "
            f"model_name={row.get('model_name')!r} | "
            f"user_id={row.get('user_id')} | "
            f"issue_id={row.get('issue_id')} | "
            f"outcome={row.get('outcome')}"
        )

        shown += 1

        if shown >= 15:
            print("  ... additional records omitted")
            break


# ============================================================
# 5. FINAL BUT NOT COMPLETE
# ============================================================

print()
print("=" * 78)
print("5. FINAL BUT NOT COMPLETE")
print("=" * 78)

final_incomplete = []

for row in troubleshoot:

    try:
        steps_completed = int(
            row.get("steps_completed", "")
        )

        total_steps = int(
            row.get("total_steps", "")
        )

    except ValueError:
        continue

    is_final = row.get(
        "is_final",
        ""
    ).strip()

    if (
        is_final == "1"
        and total_steps > 0
        and steps_completed != total_steps
    ):
        final_incomplete.append(row)


print(
    f"Total final-but-incomplete records: "
    f"{len(final_incomplete)}"
)

print()

for row in final_incomplete:

    print(
        f"id={row.get('id')} | "
        f"model_id={row.get('model_id')} | "
        f"model_name={row.get('model_name')} | "
        f"issue_id={row.get('issue_id')} | "
        f"steps={row.get('steps_completed')}/"
        f"{row.get('total_steps')} | "
        f"last_step={row.get('last_step_id')!r} | "
        f"outcome={row.get('outcome')!r} | "
        f"session_id={row.get('session_id')!r}"
    )


# ============================================================
# 6. ZERO TOTAL STEPS
# ============================================================

print()
print("=" * 78)
print("6. ZERO TOTAL STEPS")
print("=" * 78)

for row in troubleshoot:

    if row.get("total_steps") == "0":

        print()

        for key, value in row.items():
            print(f"{key}: {value!r}")


# ============================================================
# 7. MODEL NAME -> MODEL ID MAPPING
# ============================================================

print()
print("=" * 78)
print("7. MODEL NAME / MODEL ID MAPPING")
print("=" * 78)

reverse_mapping = defaultdict(Counter)

for row in troubleshoot:

    model_id = row.get(
        "model_id",
        ""
    ).strip()

    model_name = row.get(
        "model_name",
        ""
    ).strip()

    reverse_mapping[model_name][model_id] += 1


for model_name in sorted(reverse_mapping.keys()):

    print()
    print(f"{model_name}")

    for model_id, count in reverse_mapping[
        model_name
    ].most_common():

        print(
            f"  {model_id:<15} "
            f"{count}"
        )


# ============================================================
# COMPLETE
# ============================================================

print()
print("=" * 78)
print("CANDIDATE INVESTIGATION COMPLETE")
print("=" * 78)

print()
print("NO TRANSFORMATION WAS APPLIED.")
print("NO SOURCE DATA WAS MODIFIED.")
print()