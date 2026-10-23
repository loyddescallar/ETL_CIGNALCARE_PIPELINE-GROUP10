# CignalCare+ Lab 4 — Transformation Issue Register

## 1. Profiling Baseline

The Transformation Stage receives the validated Lab 3 Extraction Stage handover. The documented baseline for the handover processed for this Lab 4 work is:

| Item | Value |
|---|---|
| Extraction Batch ID | `20261018T170820026121Z` |
| Extraction Mode | `full_initial` |
| Tables | 8 |
| Total Records | 478 |
| Transformation focus | `troubleshoot_outcomes` |
| Transformation input records | 138 |

Profiling was performed against the validated extraction files only. No source-system re-extraction and no modification of the Lab 3 extraction files were performed.

## 2. Data-Quality Issues and Candidate Findings

The profiling and candidate investigation produced the following findings.

| Issue | Table/File | Column(s) | Issue Type | Example | Affected | Planned Treatment / Decision |
|---|---|---|---|---|---:|---|
| **I-01** | `troubleshoot_outcomes` | `model_id`, `model_name` | Inconsistent identifier-to-description mapping | `model_1` is associated with multiple receiver models | **137/138 (99.28%)** source records use ambiguous `model_*` identifiers | Apply **S-01**; derive canonical ID from standardized `model_name` and preserve source fields |
| **I-02** | `prepaid_plans` | `id`, `plan_code` | Unused active plan / unusual value | `id=8`, `plan_code=hehe420`, `plan_name=LOAD420` | **1 plan** | Retain; evidence does not establish invalidity |
| **I-03** | `technician_requests` | `issueDescription`, `screen_issue` | Candidate mismatch / false positive | `id=1`; description and `screen_issue` both indicate Black Screen | **1 request** | No transformation; profiling parser was corrected |
| **I-04** | `troubleshoot_outcomes` | `is_final`, `steps_completed`, `total_steps`, `outcome` | Final records with incomplete steps | `is_final=1`, `steps_completed=3`, `total_steps=4`, `outcome=unresolved` | **15 records** | Preserve; no rule justifies changing the values |
| **I-05** | `troubleshoot_outcomes` | `steps_completed`, `total_steps`, `last_step_id`, `session_id`, `outcome` | Zero-step unresolved record | `0/0`, `last_step_id=NULL`, `session_id=NULL`, `outcome=unresolved` | **1 record** | Preserve; do not invent missing information |

### I-01 — Inconsistent Troubleshooting Model Identifiers

The profiling found **9 distinct source `model_id` values** in the 138 troubleshooting records. Of these, **8 identifiers (`model_1` through `model_8`) are associated with multiple model names**. The remaining source identifier, `changhong-silver-hd`, is associated with `Changhong Silver HD`.

The reverse relationship also contains **6 model names associated with multiple source model IDs**. For example, `model_1` is associated with `Arion HD Cardless Zapper`, `Changhong Silver HD`, `GIEC HD`, and `Humax HD`.

Across the 138 records, **137 records (99.28%)** use an ambiguous `model_*` identifier. This makes the source `model_id` unsuitable as the unique analytical model identifier for this transformation.

**Decision:** Apply S-01. The canonical identifier is derived from the standardized model description rather than guessing which source `model_id` is correct.

**Status:** CONFIRMED — TRANSFORMATION REQUIRED.

### I-02 — Unused Active Prepaid Plan

The profiling identified one active plan that is not referenced by the observed prepaid transactions or load requests:

- `id = 8`
- `plan_code = hehe420`
- `plan_name = LOAD420`
- `amount = 420.00`
- `status = active`

The evidence does not establish that the record is invalid.

**Decision:** Retain without modification.

**Status:** INVESTIGATED — NO TRANSFORMATION JUSTIFIED.

### I-03 — Technician Request Description Mismatch False Positive

One technician request initially appeared to contain a mismatch between `screen_issue` and the issue stated in `issueDescription`. Further investigation showed that the full description explicitly identifies the selected issue as `Black Screen`. The apparent mismatch came from the initial parsing approach.

**Decision:** No transformation.

**Status:** FALSE POSITIVE — NO TRANSFORMATION.

### I-04 — Final Troubleshooting Records With Incomplete Steps

Fifteen troubleshooting records contain `is_final=1`, `steps_completed=3`, `total_steps=4`, and `outcome=unresolved`. The available evidence does not prove that these records are erroneous.

**Decision:** Preserve the source values.

**Status:** INVESTIGATED — NO TRANSFORMATION JUSTIFIED.

### I-05 — Zero-Step Unresolved Troubleshooting Record

One record contains `steps_completed=0`, `total_steps=0`, `last_step_id=NULL`, `outcome=unresolved`, and `session_id=NULL`. The evidence does not establish what the missing values should be.

**Decision:** Preserve the source values and do not fabricate step information.

**Status:** INVESTIGATED — NO TRANSFORMATION JUSTIFIED.

## 3. Profiling Checks With No Data-Quality Violation

The following checks produced no violations in the validated Lab 3 handover:

- Foreign-key relationship checks: **0 missing references**.
- Prepaid transaction amount versus plan amount: **0 mismatches**.
- Load request amount versus plan amount: **0 mismatches**.
- Paid records without payment completion timestamp: **0**.
- Non-paid records with payment completion timestamp: **0**.
- Completed records without fulfillment timestamp: **0**.
- Non-completed records with fulfillment timestamp: **0**.
- Issue ID versus issue label conflicts: **0**.
- Troubleshooting user references missing from `users`: **0**.
- Troubleshooting location versus user location mismatches: **0**.
- `steps_completed > total_steps`: **0**.
- Duplicate complete rows: **0**.
- Duplicate primary-key values: **0**.

These observations are evidence that the corresponding fields do not require unnecessary transformation rules for this batch.

## 4. Transformation Prioritization

| Priority | Issue | Reason |
|---|---|---|
| **P1** | I-01 | Directly affects model identity and downstream analytical grouping |
| **P2** | I-02 | Investigated observation; no evidence supports modification |
| **P2** | I-03 | False positive; no source-data conflict remains |
| **P2** | I-04 | Potentially valid unresolved final state |
| **P2** | I-05 | Insufficient evidence to infer missing troubleshooting state |

## 5. Transformation Decision

The only confirmed transformation candidate for the current Lab 4 implementation is **I-01**, treated by **S-01**. I-02 through I-05 remain source observations and are not altered.

## 6. Issue Assignment

| Issue | Issuer | Assignee | Status |
|---|---|---|---|
| I-01 — Inconsistent Troubleshooting Model Identifiers | John Mark / John Paul | Loyd / team-assigned transformation owner | Completed |

The completed S-01 implementation and validation evidence are recorded in `docs/transformation/s01-transformation-results.md`.

## 7. Evidence Sources

1. Lab 3 extraction handover batch `20261018T170820026121Z`.
2. `pipeline/transformation/profile_input.py`.
3. `pipeline/transformation/profile_relationships.py`.
4. `pipeline/transformation/investigate_candidates.py`.
5. S-01 transformation and validation results.

No raw extraction file is modified by the Transformation Stage.
