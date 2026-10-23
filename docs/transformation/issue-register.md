# CignalCare+ Lab 4 — Transformation Issue Register

## 1. Profiling Baseline

The Transformation Stage receives the validated Lab 3 extraction handover identified by:

- **Extraction Batch ID:** `20261018T170820026121Z`
- **Extraction Mode:** `full_initial`
- **Tables:** 8
- **Total Records:** 478

The transformation profiling was performed only against the eight CSV files belonging to this handover batch. No source-system re-extraction or modification was performed.

---

## 2. Confirmed Data-Quality Issue

### I-01 — Inconsistent Troubleshooting Model Identifiers

| Field | Finding |
|---|---|
| **Table** | `troubleshoot_outcomes` |
| **Columns** | `model_id`, `model_name` |
| **Issue Type** | Inconsistent identifier-to-description mapping |
| **Affected Records** | Model mapping conflict exists across the 138 troubleshooting records |
| **Evidence** | All 8 observed `model_id` values are associated with multiple `model_name` values |
| **Additional Evidence** | 6 observed `model_name` values are associated with multiple `model_id` values |
| **Example** | `model_1` is associated with `Changhong Silver HD`, `Humax HD`, `GIEC HD`, and `Arion HD Cardless Zapper` |
| **Impact** | Using `model_id` as a reliable business identifier can group different receiver models together and produce incorrect analysis or joins |
| **Planned Treatment** | Proposed Standardization Rule S-01: establish a canonical model reference using the reliable model description and prevent the ambiguous source `model_id` from being treated as a unique business model identifier |
| **Assignment** | Pending issuer decision |
| **Status** | CONFIRMED TRANSFORMATION CANDIDATE |

---

## 3. Investigated Findings That Do Not Currently Justify Transformation

### I-02 — Unused Active Prepaid Plan

The profiling identified one active prepaid plan that is not referenced by the observed transactions or load requests:

- `id = 8`
- `plan_code = hehe420`
- `plan_name = LOAD420`
- `amount = 420.00`
- `status = active`

The plan is unusual compared with the other observed plan-code pattern, but the profiling evidence does not establish that the record is invalid. It is therefore **not removed, renamed, or modified** at this stage.

**Decision:** Retain the record and document it as an investigated observation.

**Status:** INVESTIGATED — NO TRANSFORMATION CURRENTLY JUSTIFIED.

---

### I-03 — Technician Request Description Mismatch False Positive

The initial deep profiler reported one mismatch for technician request `id = 1`.

Further investigation showed:

- `screen_issue = Black Screen`
- The full `issueDescription` explicitly describes the selected issue as `Black Screen`.

The apparent mismatch resulted from incorrect parsing of the free-text description rather than an actual disagreement between source fields.

**Decision:** No transformation is required.

**Status:** FALSE POSITIVE — NO TRANSFORMATION.

---

### I-04 — Final Troubleshooting Records With Incomplete Steps

Fifteen troubleshooting records have:

- `is_final = 1`
- `steps_completed = 3`
- `total_steps = 4`
- `outcome = unresolved`

These records may represent a legitimate final unresolved troubleshooting state. The current profiling evidence does not justify changing `steps_completed` to `4` or changing the outcome.

**Decision:** Preserve the source values until a documented business rule establishes otherwise.

**Status:** INVESTIGATED — NO TRANSFORMATION CURRENTLY JUSTIFIED.

---

### I-05 — Zero-Step Unresolved Troubleshooting Record

One troubleshooting record has:

- `steps_completed = 0`
- `total_steps = 0`
- `last_step_id = NULL`
- `outcome = unresolved`
- `session_id = NULL`

This may represent a troubleshooting attempt that was recorded before any steps were started. There is insufficient evidence to replace the values with assumed defaults.

**Decision:** Preserve the source values and do not fabricate missing step information.

**Status:** INVESTIGATED — NO TRANSFORMATION CURRENTLY JUSTIFIED.

---

## 4. Profiling Findings With No Data-Quality Violation

The following checks produced no violations in the Lab 3 handover:

- Foreign-key relationship checks: **0 missing references**
- Prepaid transaction amount versus plan amount: **0 mismatches**
- Load request amount versus plan amount: **0 mismatches**
- Paid records without payment completion timestamp: **0**
- Non-paid records with payment completion timestamp: **0**
- Completed records without fulfillment timestamp: **0**
- Non-completed records with fulfillment timestamp: **0**
- Issue ID versus issue label conflicts: **0**
- Troubleshooting user references missing from `users`: **0**
- Troubleshooting location versus user location mismatches: **0**
- `steps_completed > total_steps`: **0**
- Duplicate complete rows: **0**
- Duplicate primary-key values: **0**

These findings should not be converted into unnecessary transformation rules.

---

## 5. Current Transformation Decision

At the current stage, the only confirmed transformation candidate is:

**I-01 — Inconsistent Troubleshooting Model Identifiers**

The remaining investigated findings are retained as source observations because the available evidence does not justify modifying the records.

The actual implementation rule, target output structure, and assignment will be finalized before transformation code is written.

---

## 6. Issue Assignment

| Issue | Issuer | Assignee | Status |
|---|---|---|---|
| I-01 — Inconsistent Troubleshooting Model Identifiers | John Mark / John Paul | Pending decision between Loyd and Maricar | Pending |

John Mark and John Paul will act as the issuers for the Lab 4 issue assignment. The assignee will be determined by the issuers according to the team's agreed workflow.

---

## 7. Evidence Sources

The issue register is based on:

1. Lab 3 extraction handover batch `20261018T170820026121Z`.
2. Basic transformation input profiling.
3. Deep relationship and consistency profiling.
4. Candidate issue investigation.

No transformation has been applied to the source handover files at the time of this register.