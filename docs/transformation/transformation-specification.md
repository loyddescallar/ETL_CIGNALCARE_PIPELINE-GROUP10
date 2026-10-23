# CignalCare+ Lab 4 — Data Transformation Specification

## 1. Transformation Input and Processing Specification

### 1.1 Input Source

The Transformation Stage receives the **validated handover produced by Lab 3**, not a new extraction from the operational database. The current documented handover is:

| Item | Value |
|---|---|
| Extraction Batch ID | `20261018T170820026121Z` |
| Extraction Mode | `full_initial` |
| Source tables | 8 |
| Handover records | 478 |
| Format | CSV |
| Handover location | `data/extracted/` |

The handover contains these eight datasets:

- `users`
- `prepaid_plans`
- `prepaid_transactions`
- `load_requests`
- `tickets`
- `technician_requests`
- `troubleshoot_outcomes`
- `support_incidents`

For the implemented S-01 rule, only `troubleshoot_outcomes` is transformed. Its handover input contains **138 records** in:

`data/extracted/20261018T170820768165Z_troubleshoot_outcomes.csv`

The Transformation Stage does not re-extract from PostgreSQL/Supabase and does not modify the Lab 3 extraction files.

### 1.2 Batch Processing Method

S-01 is implemented as a Python batch transformation in:

`pipeline/transformation/transform_s01.py`

The process is:

1. Read a validated Lab 3 CSV handover.
2. Validate the required input columns.
3. Profile the model-name values needed by S-01.
4. Build a deterministic model-name-to-canonical-ID mapping.
5. Add `standardized_model_name` and `canonical_model_id`.
6. Quarantine records that cannot safely produce a canonical ID.
7. Validate record reconciliation, source-value preservation, uniqueness, mapping consistency, ID format, and deterministic regeneration.
8. Write the transformed output and transformation metadata.

The pipeline design specifies a **daily 12:00 AM batch schedule**. The current implementation is a command-line Python batch and does not include an implemented Airflow DAG; therefore, the schedule is a pipeline design requirement, not a scheduler configuration in this repository.

### 1.3 Batch Size and Processing Window

The current S-01 run processes the complete 138-record `troubleshoot_outcomes` handover dataset. The processing window recorded in the transformation log is derived from the minimum and maximum `created_at` values in the input batch.

For future batches, the script accepts an explicit input file and parent extraction batch ID so that the same rule can be reused without changing the transformation source code.

### 1.4 Failed Batch Rerun and Idempotency

A failed batch is not accepted for Load. The same validated input is corrected or reprocessed after the cause is addressed.

S-01 is deterministic: the same standardized model name always produces the same canonical model ID. The reusable script also uses a stable default output name derived from the input dataset and rule, so rerunning the same input replaces the same transformed artifact instead of creating a new content-equivalent file with a different timestamp.

The transformation run ID remains unique per execution for audit purposes. Therefore:

- **Data-level idempotency:** PASS.
- **Default output-artifact idempotency:** PASS.
- **Execution-log uniqueness:** each run is separately recorded.

### 1.5 Dependencies and Assumptions

The Transformation Stage depends on:

- A validated Lab 3 extraction handover.
- The expected CSV schema being present.
- Stable source record identifiers.
- The `model_name` field being the authoritative descriptive value for S-01 canonicalization.
- Transformation rules being supported by profiling evidence.
- Required validation and metadata being available before handover.

The stage assumes that a missing business value must not be invented. When a required value cannot be safely transformed, the record is quarantined and the rejection is logged.

### 1.6 Transformation Boundary

The Transformation Stage begins with the validated extraction handover and ends with a validated transformed dataset. It includes profiling, cleaning where justified, standardization, validation, metadata, and handover preparation.

Loading the transformed data into the target analytics database is outside this stage.

## 2. Data Profiling and Issue Identification

### 2.1 Profiling Method

Profiling was completed before transformation rules were finalized. The profiling scripts are read-only and inspect the validated Lab 3 files.

Checks included:

- Table and record-count confirmation.
- Column structure and inferred data types.
- NULL/blank values.
- Primary-key NULL and duplicate checks.
- Cross-table relationship checks.
- Amount consistency.
- Payment and fulfillment timestamp consistency.
- Technician-request issue consistency.
- Troubleshooting model ID/name consistency.
- Troubleshooting issue ID/label consistency.
- Troubleshooting step consistency.
- Candidate anomaly investigation.

### 2.2 Issue Summary

| Issue | Table | Column(s) | Type | Affected | Treatment |
|---|---|---|---|---:|---|
| I-01 | `troubleshoot_outcomes` | `model_id`, `model_name` | Inconsistent mapping | 137/138 records use ambiguous `model_*` IDs (99.28%) | **S-01** |
| I-02 | `prepaid_plans` | `id`, `plan_code` | Unused active plan | 1 plan | Retain |
| I-03 | `technician_requests` | `issueDescription`, `screen_issue` | False-positive mismatch | 1 request | Retain |
| I-04 | `troubleshoot_outcomes` | `is_final`, `steps_completed`, `total_steps`, `outcome` | Final/incomplete-step observation | 15 records | Retain |
| I-05 | `troubleshoot_outcomes` | step/session fields | Zero-step unresolved observation | 1 record | Retain |

### 2.3 Confirmed Issue I-01

There are **9 distinct source model IDs**. Eight `model_*` IDs have multiple associated model names, while `changhong-silver-hd` has one associated name. There are **6 distinct model names**, and each model name is associated with multiple source IDs.

The source `model_id` therefore cannot safely serve as the unique analytical model identifier. S-01 uses the standardized `model_name` as the canonicalization basis.

### 2.4 Findings Not Transformed

I-02 through I-05 are preserved because the profiling evidence does not justify changing the business meaning of the source records.

## 3. Data Cleaning Rules

### 3.1 Cleaning Policy

Cleaning is conservative. The Transformation Stage does not delete, invent, or manually correct business values unless a documented rule is supported by profiling evidence.

### 3.2 Duplicate Records

Duplicate primary-key values and duplicate complete rows were checked. No duplicate primary-key violation was found in the handover. No duplicate-removal rule is applied.

### 3.3 Missing and Blank Values

Blank values are preserved unless a documented derivation is safe. For S-01, a blank `model_name` cannot produce a valid canonical model ID; such a record is quarantined rather than assigned an assumed model name.

### 3.4 Referential Integrity

The applicable Lab 3 relationship checks reported zero missing references. No referential-integrity cleaning rule is required for the current batch.

### 3.5 Cross-Field Consistency

The profiling reported zero amount mismatches and zero payment/fulfillment timestamp consistency violations in the checked fields. No cross-field correction is applied.

### 3.6 Investigated Observations

The unused plan, false-positive technician mismatch, final-but-incomplete troubleshooting records, and zero-step unresolved record remain unchanged.

### 3.7 Cleaning Principle

**Do not invent data.** Every cleaning action must have an explicit rule, reason, validation method, and traceability path.

## 4. Standardization and Data Type Rules

### 4.1 S-01 Rule Definition

| Item | Specification |
|---|---|
| Rule ID | `S-01` |
| Version | `S-01-v1.0.0` |
| Type | Standardization |
| Input table | `troubleshoot_outcomes` |
| Input fields | `model_id`, `model_name` |
| Output fields | `standardized_model_name`, `canonical_model_id` |
| Basis | Standardized `model_name` |
| Rejection condition | Blank `model_name` or invalid canonicalization |

### 4.2 Model Name Standardization

S-01 applies:

1. Unicode NFKC normalization.
2. Leading/trailing whitespace removal.
3. Internal whitespace collapse.

The rule does not manually rename models or map `model_1`, `model_2`, etc. to a guessed receiver model.

### 4.3 Canonical ID Generation

The standardized name is case-folded, non-alphanumeric runs are replaced with underscores, surrounding underscores are removed, and `model_` is prefixed.

Examples:

| Standardized model name | Canonical model ID |
|---|---|
| Arion HD Cardless Zapper | `model_arion_hd_cardless_zapper` |
| Changhong Silver HD | `model_changhong_silver_hd` |
| GIEC HD | `model_giec_hd` |
| Humax HD | `model_humax_hd` |
| Pace HD | `model_pace_hd` |
| Samsung HD | `model_samsung_hd` |

### 4.4 Source-Value Preservation

The original `model_id` and `model_name` are preserved. S-01 adds canonical fields instead of overwriting the source identifiers.

### 4.5 Logical Data Types

The CSV representation is text, but the logical types follow the source contract:

| Field | Logical Type | Handling |
|---|---|---|
| `id` | character varying | Preserve |
| `user_id` | integer | Preserve |
| `location` | character varying | Preserve |
| `model_id` | character varying | Preserve |
| `model_name` | character varying | Preserve |
| `issue_id` | character varying | Preserve |
| `issue_label` | character varying | Preserve |
| `outcome` | character varying | Preserve |
| `created_at` | timestamp without time zone | Preserve |
| `session_id` | character varying | Preserve |
| `support_mode` | character varying | Preserve |
| `is_final` | integer | Preserve |
| `video_watched` | integer | Preserve |
| `steps_completed` | integer | Preserve |
| `total_steps` | integer | Preserve |
| `last_step_id` | character varying | Preserve |
| `standardized_model_name` | character varying | Add |
| `canonical_model_id` | character varying | Add |

**Important:** The source database profile contains 17 columns, including `account_number`. The validated Lab 3 handover used by S-01 contains 16 columns because `account_number` was not part of the extracted handover. S-01 therefore retains the **16-column handover schema** and adds two output fields; it does not claim to reconstruct the omitted source column.

### 4.6 Blank Model Name

A blank `model_name` is a rejection condition for S-01. The record is written to transformation quarantine with the rule ID, reason, run ID, and source row reference.

### 4.7 Standardization Validation

The rule must satisfy:

- Every retained record has both S-01 output fields.
- Source values are unchanged.
- Output record IDs remain unique.
- One standardized name maps to one canonical ID.
- One canonical ID maps to one standardized name.
- Canonical IDs match the defined format.
- Re-running canonicalization produces the same ID.
- Input = output + rejected.

## 5. Business Transformation Rules

### 5.1 Current Scope

No separate aggregation, derived metric, financial calculation, or business categorization is implemented in the current Lab 4 transformation. S-01 is a standardization rule.

### 5.2 Business Purpose

S-01 creates a stable model reference for downstream grouping and analysis while avoiding unsupported guesses about the ambiguous source `model_id`.

### 5.3 Business Values Preserved

S-01 does not alter troubleshooting outcome, issue, user, location, session, support-mode, step, or timestamp values.

### 5.4 Future Business Transformations

Any future business transformation must define a rule ID/version, source-to-target mapping, business justification, validation criteria, reconciliation method, and rejected-record handling before implementation.

## 6. Transformed Data Contract and Naming Convention

### 6.1 Output Dataset

S-01 produces a transformed `troubleshoot_outcomes` CSV containing the 16 source-handover columns plus:

- `standardized_model_name`
- `canonical_model_id`

The current validated output contains **18 columns** and **138 records**.

### 6.2 Output Field Contract

| Field | Origin | Logical Type | Required in Output | Description |
|---|---|---|---|---|
| `id` | Source | character varying | Yes | Troubleshooting record identifier |
| `user_id` | Source | integer | Yes | Associated user ID |
| `location` | Source | character varying | Yes | Recorded location |
| `model_id` | Source | character varying | Yes | Original source model identifier |
| `model_name` | Source | character varying | Yes/nullable by source contract | Original source model name |
| `issue_id` | Source | character varying | Yes | Issue identifier |
| `issue_label` | Source | character varying | Yes | Issue label |
| `outcome` | Source | character varying | Yes | Troubleshooting outcome |
| `created_at` | Source | timestamp without time zone | Yes | Record creation timestamp |
| `session_id` | Source | character varying | Nullable | Troubleshooting session ID |
| `support_mode` | Source | character varying | Yes | Support mode |
| `is_final` | Source | integer | Yes | Final-record flag |
| `video_watched` | Source | integer | Yes | Video-watched flag |
| `steps_completed` | Source | integer | Yes | Completed step count |
| `total_steps` | Source | integer | Yes | Total step count |
| `last_step_id` | Source | character varying | Nullable | Last troubleshooting step |
| `standardized_model_name` | Derived | character varying | Yes for retained rows | S-01 standardized model name |
| `canonical_model_id` | Derived | character varying | Yes for retained rows | Deterministic analytical model ID |

### 6.3 Naming Convention

New fields use descriptive `snake_case` names. Existing source field names are retained. Source identifiers are not overwritten.

### 6.4 Output File Naming

The reusable S-01 implementation uses:

`S01_<table_name>_<parent_batch_id>.csv`

for its default output artifact. An explicit output path may be supplied for controlled handover naming.

The historical completed run is preserved as:

`20261023T055811218622Z_S01_troubleshoot_outcomes.csv`

### 6.5 Traceability

Every accepted output must be traceable to:

- Parent extraction batch ID.
- Input file.
- Transformation run ID.
- Rule ID/version.
- Output file.
- Validation result.
- Input and output SHA-256 hashes.

### 6.6 Output Record Contract

For the completed S-01 batch:

- Input: **138** records.
- Output: **138** records.
- Rejected: **0** records.
- Canonical models: **6**.
- Reconciliation: **PASS**.

## 7. Document Control

This specification is the baseline Lab 4 Transformation document for future transformation work. New rules should be added as separate versioned rules without rewriting historical results.
