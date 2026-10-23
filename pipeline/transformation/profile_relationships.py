import csv
import os
from collections import Counter, defaultdict
from decimal import Decimal, InvalidOperation


# ============================================================
# CignalCare+ LAB 4
# DEEP INPUT / RELATIONSHIP PROFILER
#
# Purpose:
#   Analyze relationships and cross-field consistency in the
#   validated Lab 3 handover BEFORE transformation rules are
#   defined.
#
# IMPORTANT:
#   - Reads ONLY the official Lab 3 handover files.
#   - Does NOT connect to PostgreSQL/Supabase.
#   - Does NOT modify source files.
#   - Does NOT apply cleaning rules.
# ============================================================


BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.dirname(os.path.abspath(__file__))
    )
)

EXTRACTED_DIR = os.path.join(BASE_DIR, "data", "extracted")

EXPECTED_BATCH_ID = "20261018T170820026121Z"

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


# ============================================================
# HELPERS
# ============================================================

def is_blank(value):
    return value is None or value.strip() == ""


def load_csv(table_name, filename):
    path = os.path.join(EXTRACTED_DIR, filename)

    if not os.path.exists(path):
        raise FileNotFoundError(
            f"{table_name}: file not found: {path}"
        )

    with open(
        path,
        "r",
        encoding="utf-8-sig",
        newline=""
    ) as file:
        reader = csv.DictReader(file)
        rows = list(reader)

    return rows


def print_section(title):
    print()
    print("=" * 78)
    print(title)
    print("=" * 78)


def normalize_text(value):
    if value is None:
        return ""
    return value.strip()


def to_decimal(value):
    try:
        return Decimal(normalize_text(value))
    except (InvalidOperation, ValueError):
        return None


def build_lookup(rows, key):
    lookup = {}

    for row in rows:
        value = normalize_text(row.get(key, ""))

        if value != "":
            lookup[value] = row

    return lookup


def foreign_key_profile(
    child_rows,
    child_table,
    child_column,
    parent_rows,
    parent_table,
    parent_column="id"
):
    child_values = []

    for row in child_rows:
        value = normalize_text(row.get(child_column, ""))

        if value != "":
            child_values.append(value)

    parent_values = {
        normalize_text(row.get(parent_column, ""))
        for row in parent_rows
        if normalize_text(row.get(parent_column, "")) != ""
    }

    missing = [
        value
        for value in child_values
        if value not in parent_values
    ]

    print(
        f"{child_table}.{child_column}"
        f" -> "
        f"{parent_table}.{parent_column}"
    )

    print(f"  Child records with value: {len(child_values)}")
    print(f"  Distinct child values:     {len(set(child_values))}")
    print(f"  Parent values available:   {len(parent_values)}")
    print(f"  Missing parent references:  {len(missing)}")

    if missing:
        counts = Counter(missing)

        print("  Missing reference values:")

        for value, count in counts.most_common(20):
            print(f"    {value}: {count}")

    print()

    return {
        "child_table": child_table,
        "child_column": child_column,
        "parent_table": parent_table,
        "parent_column": parent_column,
        "child_values": len(child_values),
        "distinct_child_values": len(set(child_values)),
        "missing_references": len(missing),
    }


# ============================================================
# LOAD OFFICIAL HANDOVER
# ============================================================

print_section("CignalCare+ LAB 4 - DEEP INPUT PROFILING")

print(f"Expected Lab 3 handover batch: {EXPECTED_BATCH_ID}")
print(f"Input directory: {EXTRACTED_DIR}")

print()
print("This profiler reads ONLY the official Lab 3 handover.")
print("No PostgreSQL/Supabase connection is used.")
print("No source data is modified.")

tables = {}

for table_name, filename in HANDOVER_FILES.items():
    tables[table_name] = load_csv(table_name, filename)

print()
print("Official handover loaded successfully.")

for table_name, rows in tables.items():
    print(f"  {table_name:<25} {len(rows)} rows")


# ============================================================
# 1. FOREIGN KEY / RELATIONSHIP INTEGRITY
# ============================================================

print_section("1. FOREIGN KEY / RELATIONSHIP INTEGRITY")

relationship_results = []

relationship_results.append(
    foreign_key_profile(
        tables["prepaid_transactions"],
        "prepaid_transactions",
        "user_id",
        tables["users"],
        "users"
    )
)

relationship_results.append(
    foreign_key_profile(
        tables["prepaid_transactions"],
        "prepaid_transactions",
        "plan_id",
        tables["prepaid_plans"],
        "prepaid_plans"
    )
)

relationship_results.append(
    foreign_key_profile(
        tables["load_requests"],
        "load_requests",
        "user_id",
        tables["users"],
        "users"
    )
)

relationship_results.append(
    foreign_key_profile(
        tables["load_requests"],
        "load_requests",
        "plan_id",
        tables["prepaid_plans"],
        "prepaid_plans"
    )
)

relationship_results.append(
    foreign_key_profile(
        tables["tickets"],
        "tickets",
        "user_id",
        tables["users"],
        "users"
    )
)

relationship_results.append(
    foreign_key_profile(
        tables["technician_requests"],
        "technician_requests",
        "user_id",
        tables["users"],
        "users"
    )
)

relationship_results.append(
    foreign_key_profile(
        tables["troubleshoot_outcomes"],
        "troubleshoot_outcomes",
        "user_id",
        tables["users"],
        "users"
    )
)


# ============================================================
# 2. PLAN / AMOUNT CONSISTENCY
# ============================================================

print_section("2. PLAN / AMOUNT CONSISTENCY")

plans = build_lookup(
    tables["prepaid_plans"],
    "id"
)

def check_plan_amount(
    table_name,
    rows
):
    mismatches = []

    for row in rows:
        plan_id = normalize_text(row.get("plan_id", ""))
        row_amount = to_decimal(row.get("amount", ""))

        if plan_id == "":
            continue

        plan = plans.get(plan_id)

        if plan is None:
            continue

        plan_amount = to_decimal(
            plan.get("amount", "")
        )

        if (
            row_amount is not None
            and plan_amount is not None
            and row_amount != plan_amount
        ):
            mismatches.append({
                "id": row.get("id", ""),
                "plan_id": plan_id,
                "row_amount": str(row_amount),
                "plan_amount": str(plan_amount),
            })

    print(f"Table: {table_name}")
    print(f"  Records checked: {len(rows)}")
    print(f"  Amount mismatches: {len(mismatches)}")

    if mismatches:
        print("  Examples:")

        for item in mismatches[:20]:
            print(
                f"    id={item['id']} "
                f"plan_id={item['plan_id']} "
                f"record_amount={item['row_amount']} "
                f"plan_amount={item['plan_amount']}"
            )

    print()

    return mismatches


transaction_amount_mismatches = check_plan_amount(
    "prepaid_transactions",
    tables["prepaid_transactions"]
)

load_amount_mismatches = check_plan_amount(
    "load_requests",
    tables["load_requests"]
)


# ============================================================
# 3. UNUSED PLAN ANALYSIS
# ============================================================

print_section("3. PLAN USAGE COVERAGE")

all_plan_ids = {
    normalize_text(row.get("id", ""))
    for row in tables["prepaid_plans"]
}

transaction_plan_ids = {
    normalize_text(row.get("plan_id", ""))
    for row in tables["prepaid_transactions"]
    if normalize_text(row.get("plan_id", "")) != ""
}

load_request_plan_ids = {
    normalize_text(row.get("plan_id", ""))
    for row in tables["load_requests"]
    if normalize_text(row.get("plan_id", "")) != ""
}

used_plan_ids = (
    transaction_plan_ids
    | load_request_plan_ids
)

unused_plan_ids = all_plan_ids - used_plan_ids

print(f"Total prepaid plans:       {len(all_plan_ids)}")
print(f"Plans used by transactions: {len(transaction_plan_ids)}")
print(f"Plans used by load requests:{len(load_request_plan_ids)}")
print(f"Plans used anywhere:        {len(used_plan_ids)}")
print(f"Unused plan IDs:            {len(unused_plan_ids)}")

if unused_plan_ids:
    print()
    print("Unused plan IDs:")

    for plan_id in sorted(
        unused_plan_ids,
        key=lambda value: int(value)
        if value.isdigit()
        else value
    ):
        plan = plans.get(plan_id)

        if plan:
            print(
                f"  id={plan_id} "
                f"code={plan.get('plan_code', '')} "
                f"name={plan.get('plan_name', '')}"
            )


# ============================================================
# 4. LOAD REQUEST PAYMENT TIMESTAMP CONSISTENCY
# ============================================================

print_section("4. LOAD REQUEST PAYMENT CONSISTENCY")

load_requests = tables["load_requests"]

paid_without_payment_date = []
unpaid_with_payment_date = []

for row in load_requests:
    payment_status = normalize_text(
        row.get("payment_status", "")
    )

    payment_completed_at = normalize_text(
        row.get("payment_completed_at", "")
    )

    if payment_status == "paid" and payment_completed_at == "":
        paid_without_payment_date.append(row)

    if payment_status != "paid" and payment_completed_at != "":
        unpaid_with_payment_date.append(row)


print(
    "Paid records without payment_completed_at:",
    len(paid_without_payment_date)
)

print(
    "Non-paid records with payment_completed_at:",
    len(unpaid_with_payment_date)
)


# ============================================================
# 5. LOAD REQUEST FULFILLMENT CONSISTENCY
# ============================================================

print_section("5. LOAD REQUEST FULFILLMENT CONSISTENCY")

completed_without_fulfilled_at = []
non_completed_with_fulfilled_at = []

for row in load_requests:
    status = normalize_text(
        row.get("status", "")
    )

    fulfilled_at = normalize_text(
        row.get("fulfilled_at", "")
    )

    if status == "Completed" and fulfilled_at == "":
        completed_without_fulfilled_at.append(row)

    if status != "Completed" and fulfilled_at != "":
        non_completed_with_fulfilled_at.append(row)


print(
    "Completed records without fulfilled_at:",
    len(completed_without_fulfilled_at)
)

print(
    "Non-completed records with fulfilled_at:",
    len(non_completed_with_fulfilled_at)
)


# ============================================================
# 6. PAYMENT STATUS VS REQUEST STATUS
# ============================================================

print_section("6. PAYMENT STATUS VS REQUEST STATUS")

status_pairs = Counter()

for row in load_requests:
    payment_status = normalize_text(
        row.get("payment_status", "")
    )

    status = normalize_text(
        row.get("status", "")
    )

    status_pairs[
        (payment_status, status)
    ] += 1

for (payment_status, status), count in sorted(
    status_pairs.items()
):
    print(
        f"payment_status={payment_status!r:<18} "
        f"status={status!r:<22} "
        f"count={count}"
    )


# ============================================================
# 7. TECHNICIAN REQUEST ISSUE CONSISTENCY
# ============================================================

print_section("7. TECHNICIAN REQUEST ISSUE CONSISTENCY")

technician_requests = tables["technician_requests"]

description_issue_mismatches = []

for row in technician_requests:
    description = normalize_text(
        row.get("issueDescription", "")
    )

    screen_issue = normalize_text(
        row.get("screen_issue", "")
    )

    extracted_issue = ""

    if description.startswith("["):
        closing_bracket = description.find("]")

        if closing_bracket > 1:
            extracted_issue = description[
                1:closing_bracket
            ].strip()

    if (
        extracted_issue != ""
        and screen_issue != ""
        and extracted_issue != screen_issue
    ):
        description_issue_mismatches.append({
            "id": row.get("id", ""),
            "description_issue": extracted_issue,
            "screen_issue": screen_issue,
        })


print(
    f"Technician requests checked: {len(technician_requests)}"
)

print(
    f"Description/screen_issue mismatches: "
    f"{len(description_issue_mismatches)}"
)

if description_issue_mismatches:
    print("Examples:")

    for item in description_issue_mismatches[:20]:
        print(
            f"  id={item['id']} "
            f"description={item['description_issue']!r} "
            f"screen_issue={item['screen_issue']!r}"
        )


# ============================================================
# 8. TECHNICIAN REQUEST SOURCE DISTRIBUTION
# ============================================================

print_section("8. TECHNICIAN REQUEST SOURCE DISTRIBUTION")

source_counts = Counter(
    normalize_text(row.get("source", ""))
    for row in technician_requests
)

for source, count in source_counts.most_common():
    print(f"{source!r:<35} {count}")


# ============================================================
# 9. TROUBLESHOOTING MODEL CONSISTENCY
# ============================================================

print_section("9. TROUBLESHOOTING MODEL CONSISTENCY")

troubleshoot = tables["troubleshoot_outcomes"]

model_id_to_names = defaultdict(set)
model_name_to_ids = defaultdict(set)

for row in troubleshoot:
    model_id = normalize_text(
        row.get("model_id", "")
    )

    model_name = normalize_text(
        row.get("model_name", "")
    )

    if model_id and model_name:
        model_id_to_names[model_id].add(model_name)
        model_name_to_ids[model_name].add(model_id)


model_id_multiple_names = {
    key: values
    for key, values in model_id_to_names.items()
    if len(values) > 1
}

model_name_multiple_ids = {
    key: values
    for key, values in model_name_to_ids.items()
    if len(values) > 1
}


print(
    "Model IDs with multiple model names:",
    len(model_id_multiple_names)
)

print(
    "Model names with multiple model IDs:",
    len(model_name_multiple_ids)
)

if model_id_multiple_names:
    print()
    print("Model ID conflicts:")

    for model_id, names in model_id_multiple_names.items():
        print(
            f"  {model_id}: "
            f"{sorted(names)}"
        )


# ============================================================
# 10. TROUBLESHOOTING ISSUE CONSISTENCY
# ============================================================

print_section("10. TROUBLESHOOTING ISSUE CONSISTENCY")

issue_id_to_labels = defaultdict(set)
issue_label_to_ids = defaultdict(set)

for row in troubleshoot:
    issue_id = normalize_text(
        row.get("issue_id", "")
    )

    issue_label = normalize_text(
        row.get("issue_label", "")
    )

    if issue_id and issue_label:
        issue_id_to_labels[issue_id].add(issue_label)
        issue_label_to_ids[issue_label].add(issue_id)


issue_id_multiple_labels = {
    key: values
    for key, values in issue_id_to_labels.items()
    if len(values) > 1
}

issue_label_multiple_ids = {
    key: values
    for key, values in issue_label_to_ids.items()
    if len(values) > 1
}


print(
    "Issue IDs with multiple labels:",
    len(issue_id_multiple_labels)
)

print(
    "Issue labels with multiple IDs:",
    len(issue_label_multiple_ids)
)

if issue_id_multiple_labels:
    print()
    print("Issue ID conflicts:")

    for issue_id, labels in issue_id_multiple_labels.items():
        print(
            f"  {issue_id}: "
            f"{sorted(labels)}"
        )


# ============================================================
# 11. TROUBLESHOOTING STEPS CONSISTENCY
# ============================================================

print_section("11. TROUBLESHOOTING STEPS CONSISTENCY")

steps_over_total = []
zero_total_steps = []
final_not_complete = []

for row in troubleshoot:
    try:
        steps_completed = int(
            normalize_text(
                row.get("steps_completed", "0")
            )
        )
    except ValueError:
        continue

    try:
        total_steps = int(
            normalize_text(
                row.get("total_steps", "0")
            )
        )
    except ValueError:
        continue

    is_final = normalize_text(
        row.get("is_final", "")
    )

    if steps_completed > total_steps:
        steps_over_total.append(row)

    if total_steps == 0:
        zero_total_steps.append(row)

    if (
        is_final == "1"
        and total_steps > 0
        and steps_completed != total_steps
    ):
        final_not_complete.append(row)


print(
    "Records where steps_completed > total_steps:",
    len(steps_over_total)
)

print(
    "Records with total_steps = 0:",
    len(zero_total_steps)
)

print(
    "Records marked final but not at total_steps:",
    len(final_not_complete)
)

if zero_total_steps:
    print()
    print("Records with total_steps = 0:")

    for row in zero_total_steps[:20]:
        print(
            f"  id={row.get('id', '')} "
            f"steps_completed={row.get('steps_completed', '')} "
            f"outcome={row.get('outcome', '')} "
            f"last_step_id={row.get('last_step_id', '')!r}"
        )


# ============================================================
# 12. TROUBLESHOOTING NULL CONTEXT
# ============================================================

print_section("12. TROUBLESHOOTING NULL CONTEXT")

session_null_by_outcome = Counter()
last_step_null_by_outcome = Counter()
session_null_by_steps = Counter()
last_step_null_by_steps = Counter()

for row in troubleshoot:
    outcome = normalize_text(
        row.get("outcome", "")
    )

    steps_completed = normalize_text(
        row.get("steps_completed", "")
    )

    session_id = normalize_text(
        row.get("session_id", "")
    )

    last_step_id = normalize_text(
        row.get("last_step_id", "")
    )

    if session_id == "":
        session_null_by_outcome[outcome] += 1
        session_null_by_steps[steps_completed] += 1

    if last_step_id == "":
        last_step_null_by_outcome[outcome] += 1
        last_step_null_by_steps[steps_completed] += 1


print("NULL session_id by outcome:")

for outcome, count in session_null_by_outcome.most_common():
    print(
        f"  {outcome!r:<20} {count}"
    )

print()
print("NULL last_step_id by outcome:")

for outcome, count in last_step_null_by_outcome.most_common():
    print(
        f"  {outcome!r:<20} {count}"
    )

print()
print("NULL session_id by steps_completed:")

for steps, count in sorted(
    session_null_by_steps.items()
):
    print(
        f"  steps_completed={steps:<5} {count}"
    )

print()
print("NULL last_step_id by steps_completed:")

for steps, count in sorted(
    last_step_null_by_steps.items()
):
    print(
        f"  steps_completed={steps:<5} {count}"
    )


# ============================================================
# 13. TROUBLESHOOTING LOCATION VS USER LOCATION
# ============================================================

print_section("13. TROUBLESHOOTING LOCATION VS USER LOCATION")

users = build_lookup(
    tables["users"],
    "id"
)

location_mismatches = []
missing_users = []

for row in troubleshoot:
    user_id = normalize_text(
        row.get("user_id", "")
    )

    outcome_location = normalize_text(
        row.get("location", "")
    )

    user = users.get(user_id)

    if user is None:
        missing_users.append(row)
        continue

    user_location = normalize_text(
        user.get("location", "")
    )

    if (
        outcome_location != ""
        and user_location != ""
        and outcome_location != user_location
    ):
        location_mismatches.append({
            "id": row.get("id", ""),
            "user_id": user_id,
            "outcome_location": outcome_location,
            "user_location": user_location,
        })


print(
    "Troubleshoot records checked:",
    len(troubleshoot)
)

print(
    "Missing user references:",
    len(missing_users)
)

print(
    "Location mismatches:",
    len(location_mismatches)
)

if location_mismatches:
    print()
    print("Examples:")

    for item in location_mismatches[:20]:
        print(
            f"  id={item['id']} "
            f"user_id={item['user_id']} "
            f"outcome_location={item['outcome_location']!r} "
            f"user_location={item['user_location']!r}"
        )


# ============================================================
# 14. SUPPORT INCIDENT RELATIONSHIP COVERAGE
# ============================================================

print_section("14. SUPPORT INCIDENT RELATIONSHIP COVERAGE")

support_incidents = tables["support_incidents"]

support_incident_ids = {
    normalize_text(row.get("id", ""))
    for row in support_incidents
    if normalize_text(row.get("id", ""))
}

ticket_incident_values = [
    normalize_text(row.get("incident_id", ""))
    for row in tables["tickets"]
    if normalize_text(row.get("incident_id", ""))
]

technician_incident_values = [
    normalize_text(row.get("incident_id", ""))
    for row in technician_requests
    if normalize_text(row.get("incident_id", ""))
]


print(f"Support incidents available: {len(support_incident_ids)}")

print(
    "Tickets with populated incident_id:",
    len(ticket_incident_values)
)

print(
    "Technician requests with populated incident_id:",
    len(technician_incident_values)
)

ticket_orphans = [
    value
    for value in ticket_incident_values
    if value not in support_incident_ids
]

technician_orphans = [
    value
    for value in technician_incident_values
    if value not in support_incident_ids
]

print(
    "Ticket incident references missing from support_incidents:",
    len(ticket_orphans)
)

print(
    "Technician incident references missing from support_incidents:",
    len(technician_orphans)
)


# ============================================================
# 15. SUPPORT INCIDENT STATE CONSISTENCY
# ============================================================

print_section("15. SUPPORT INCIDENT STATE CONSISTENCY")

for row in support_incidents:
    status = normalize_text(
        row.get("status", "")
    )

    confirmed_at = normalize_text(
        row.get("confirmed_at", "")
    )

    resolved_at = normalize_text(
        row.get("resolved_at", "")
    )

    dismissed_at = normalize_text(
        row.get("dismissed_at", "")
    )

    print(
        f"Incident ID: {row.get('id', '')}"
    )
    print(
        f"  Status:        {status}"
    )
    print(
        f"  confirmed_at:  "
        f"{confirmed_at if confirmed_at else 'NULL'}"
    )
    print(
        f"  resolved_at:   "
        f"{resolved_at if resolved_at else 'NULL'}"
    )
    print(
        f"  dismissed_at:  "
        f"{dismissed_at if dismissed_at else 'NULL'}"
    )


# ============================================================
# FINAL SUMMARY
# ============================================================

print_section("DEEP PROFILE SUMMARY")

total_relationship_missing = sum(
    result["missing_references"]
    for result in relationship_results
)

print(
    f"Foreign-key missing references: "
    f"{total_relationship_missing}"
)

print(
    f"Prepaid transaction amount mismatches: "
    f"{len(transaction_amount_mismatches)}"
)

print(
    f"Load request amount mismatches: "
    f"{len(load_amount_mismatches)}"
)

print(
    f"Paid records without payment timestamp: "
    f"{len(paid_without_payment_date)}"
)

print(
    f"Non-paid records with payment timestamp: "
    f"{len(unpaid_with_payment_date)}"
)

print(
    f"Completed records without fulfilled timestamp: "
    f"{len(completed_without_fulfilled_at)}"
)

print(
    f"Non-completed records with fulfilled timestamp: "
    f"{len(non_completed_with_fulfilled_at)}"
)

print(
    f"Technician issue-description mismatches: "
    f"{len(description_issue_mismatches)}"
)

print(
    f"Model ID/name conflicts: "
    f"{len(model_id_multiple_names)}"
)

print(
    f"Issue ID/label conflicts: "
    f"{len(issue_id_multiple_labels)}"
)

print(
    f"steps_completed > total_steps: "
    f"{len(steps_over_total)}"
)

print(
    f"total_steps = 0: "
    f"{len(zero_total_steps)}"
)

print(
    f"Final but not complete: "
    f"{len(final_not_complete)}"
)

print(
    f"Troubleshoot location mismatches: "
    f"{len(location_mismatches)}"
)

print(
    f"Unused prepaid plans: "
    f"{len(unused_plan_ids)}"
)

print()
print("=" * 78)
print("DEEP PROFILING COMPLETE")
print("=" * 78)

print()
print("IMPORTANT:")
print("These results are observations only.")
print("No transformation or cleaning rule has been applied.")
print("Review the evidence before defining Lab 4 rules.")
print()