# CignalCare+ Lab 4 — Transformation Validation and Handover

## 7. Transformation Validation and Data Quality Checks

### 7.1 Validation Purpose

Validation is performed after transformation and before acceptance for the Load Stage. It verifies completeness, source-value preservation, rule conformance, uniqueness, deterministic canonicalization, and traceability.

### 7.2 Validation Check Matrix

| Check Name | Target | Purpose | Validation Criteria | Severity |
|---|---|---|---|---|
| Record reconciliation | Input/output/rejected counts | Detect loss or multiplication | `Input = Output + Rejected` | Critical |
| Required output columns | Transformed schema | Ensure the output contract exists | All 16 handover columns + 2 S-01 columns are present | Critical |
| Source-value preservation | Source fields | Prevent unintended source-data changes | Preserved source fields equal input values for matching IDs | Critical |
| Primary-key uniqueness | `id` | Prevent duplicate output records | No duplicate nonblank IDs | Critical |
| Required S-01 values | `standardized_model_name`, `canonical_model_id` | Ensure retained rows are usable | Both fields are nonblank on retained rows | Critical |
| Name → canonical ID | S-01 mapping | Ensure one canonical ID per standardized name | Each name has exactly one canonical ID | Critical |
| Canonical ID → name | S-01 mapping | Prevent canonical collisions | Each canonical ID maps to exactly one name | Critical |
| Canonical ID format | `canonical_model_id` | Enforce naming contract | Matches `model_<lowercase_alphanumeric_underscores>` | Major |
| Deterministic regeneration | S-01 canonicalization | Verify repeatability | Regenerated ID equals stored ID | Critical |
| Rejection accounting | Quarantine/rejection metadata | Prevent silent loss | Every rejection has rule, reason, run, and source-row reference | Critical |
| Schema/data-type conformance | Output fields | Preserve logical source types | Field names and logical types match Section 6 contract | Major |
| Referential integrity | Current S-01 output | Ensure no new invalid references | Source references remain unchanged; no new relationship is created | Major |
| Aggregate checks | Current S-01 | Determine whether aggregation altered totals | **N/A — S-01 performs no aggregation** | N/A |
| Business-rule checks | Current S-01 | Determine whether business calculations changed | **N/A — S-01 is standardization only** | N/A |

### 7.3 Completed S-01 Validation Evidence

| Validation Item | Result |
|---|---:|
| Input records | 138 |
| Output records | 138 |
| Rejected records | 0 |
| Reconciliation | **PASS** |
| Source values preserved | **PASS** |
| Output ID uniqueness | **PASS** |
| Required S-01 fields | **PASS** |
| Model name → canonical ID | **PASS** |
| Canonical ID → model name | **PASS** |
| Canonical ID format | **PASS** |
| Deterministic regeneration | **PASS** |
| Overall validation | **PASS** |

### 7.4 Rejection and Exception Handling

Rejected records are never silently deleted. A rejection must identify:

- Source record ID or source row number.
- Rule ID.
- Rejection reason.
- Transformation run ID.
- Input reference.

Rejection rate:

`Rejected Records ÷ Input Records × 100`

Completed S-01:

`0 ÷ 138 × 100 = 0%`

### 7.5 Validation Timing

Validation runs immediately after transformation and before acceptance. A failed critical check places the batch on hold and prevents Load handover.

### 7.6 Validation Evidence

Evidence consists of the transformed output, transformation log, input/output SHA-256 hashes, S-01 result report, and the rule/specification documents.

### 7.7 Manual Review

Manual review is required for failed checks, unexpected values, new rules, schema changes, business interpretation questions, or rejection patterns that require human investigation. Manual review does not replace automated checks.

### 7.8 Validation Decision

The batch can proceed only when all Critical checks pass, reconciliation succeeds, required metadata is present, and no unresolved Critical exception remains.

## 8. Transformation Metadata and Log Specification

### 8.1 Metadata Fields and Examples

| Metadata Field | Purpose | Example |
|---|---|---|
| `run_id` | Identifies one transformation execution | `TRN-20261023T055811210068Z` |
| `parent_run_id` | Links to Lab 3 extraction execution | `20261018T170820026121Z` |
| `batch_id` | Identifies the processed handover | `20261018T170820026121Z` |
| `table_name` | Identifies the transformed dataset | `troubleshoot_outcomes` |
| `input_file` | Identifies the input artifact | `data/extracted/..._troubleshoot_outcomes.csv` |
| `output_file` | Identifies the transformed artifact | `data/transformed/S01_troubleshoot_outcomes_20261018T170820026121Z.csv` |
| `quarantine_file` | Identifies rejected-record storage | `data/quarantine/transformation/TRN-..._S01_rejected.csv` |
| `batch_window_start` | Start of source-record window | `2026-08-27T19:29:47.448000` |
| `batch_window_end` | End of source-record window | `2026-09-16T22:13:44.728000` |
| `started_at` | Transformation start | `2026-10-23T05:58:11.210Z` |
| `finished_at` | Transformation end | `2026-10-23T05:58:11.250Z` |
| `duration_seconds` | Execution duration | `0.040` |
| `status` | Execution result | `SUCCESS` |
| `records_read` | Input count | `138` |
| `records_output` | Retained output count | `138` |
| `records_rejected` | Rejected count | `0` |
| `records_modified` | Records receiving S-01 output fields | `138` |
| `rules_applied` | Rule/count summary | `S-01:138` |
| `validation_status` | Validation result | `PASS` |
| `validation_errors` | Validation failure detail | blank when none |
| `code_version` | Rule version | `S-01-v1.0.0` |
| `input_sha256` | Input integrity hash | `ad6dda69cd0f5904ca7fc964090005aadf7e5a19f7154f4b8274cf960fec0085` |
| `output_sha256` | Output integrity hash | `f97776d421369b28c4af56859dda9ff9a714491b8d25e459bcc9d486ef66ea32` |

### 8.2 Transformation Log Location

The execution log is maintained at:

`state/transformation_log.csv`

This is operational state and is intentionally excluded from version control by `.gitignore`. A handover should preserve the relevant log row or export it as controlled evidence.

### 8.3 Logging for Monitoring, Troubleshooting, and Audit

The log supports:

- **Monitoring:** status, duration, record counts, and validation status show whether a batch completed successfully.
- **Troubleshooting:** input/output references, errors, rule version, and quarantine path identify where a failure occurred.
- **Audit:** run IDs, parent batch IDs, rule versions, and hashes connect the output to its source and processing decision.
- **Recovery:** the same parent batch and input reference can be rerun after correction.

### 8.4 Hash and Lineage Control

Input and output SHA-256 hashes are recorded for accepted runs. The hashes verify that the artifacts referenced by the transformation log match the artifacts that were processed and generated.

## 9. Log Retention, Rejected Data, and Access

### 9.1 Transformation Log Retention

Transformation execution logs should be retained for **at least one academic/project cycle and not less than 12 months** from the processing date, unless the project or institutional policy requires a longer period.

Operational logs are stored under `state/`. For formal handover or audit, the required log records should be copied into the controlled project evidence repository.

### 9.2 Rejected/Quarantined Data

Rejected records are stored separately under:

`data/quarantine/transformation/`

Quarantine records must include the source values needed for investigation plus rejection rule, reason, run ID, and source row number. Quarantine data must never be merged into the accepted transformed dataset without a documented reprocessing decision.

### 9.3 Access Control

Access to transformation logs and quarantine data should be limited to authorized ETL team members and reviewers. The repository must not contain database passwords, connection strings containing real credentials, or unnecessary raw sensitive customer information.

The `.env` file is local-only and must never be committed. `.env.example` contains placeholders only.

### 9.4 Archiving

After the active retention period, transformation logs and quarantine artifacts may be archived in the project-approved storage location when they are still required for audit or reproducibility. Archived artifacts must retain their original run IDs and hashes.

### 9.5 Deletion

Deletion may occur after the retention requirement has expired and there is no outstanding audit, academic requirement, or reprocessing need. Deletion must be documented so that the absence of the artifact does not appear to be an unexplained pipeline failure.

## 10. Transformation Acceptance and Handover Rules

### 10.1 Acceptance Purpose

Acceptance determines whether the transformed dataset is safe, complete, traceable, and ready for the Load Stage.

### 10.2 Rejection-Rate Threshold and Justification

The project uses a **1% rejection-rate threshold** as an operational review trigger, not as permission to silently accept bad records.

Rationale:

- A small number of isolated, explicitly quarantined records can be reviewed without automatically blocking an otherwise valid batch.
- A rate above 1% is treated as a signal that the issue may be systematic rather than isolated.
- Any Critical validation failure still blocks acceptance regardless of the percentage.

### 10.3 Acceptance Decision Matrix

| Condition | Decision | Action |
|---|---|---|
| All Critical checks PASS; rejection rate ≤ 1%; metadata complete; documentation complete | **APPROVED** | Prepare handover |
| Automated checks pass but a non-critical warning, unexpected value, or review-trigger condition exists | **MANUAL REVIEW** | Hold until review decision is documented |
| Any Critical validation failure; reconciliation failure; missing required metadata; unresolved canonicalization failure | **REJECTED** | Stop handover and correct/reprocess |
| Approved batch with complete handover package and downstream receipt | **HANDED OVER** | Release to Load Stage |

### 10.4 Automatic Approval

Automatic approval requires:

1. All Critical checks pass.
2. Record reconciliation passes.
3. Rejection rate is ≤ 1%.
4. No unresolved Critical issue remains.
5. Metadata and hashes are complete.
6. Required documentation is complete.
7. The output artifact exists and matches the recorded contract.

### 10.5 Manual Review

Manual review is required when a non-critical exception, unexpected value, new rule, schema change, or business interpretation requires human decision. The review outcome must be recorded before handover.

### 10.6 Rejection

Reject the batch when a Critical validation check fails, reconciliation fails, required output fields are missing, canonical mappings are inconsistent, required lineage is missing, or the batch cannot be reliably reproduced. A rejection rate above 1% is a review/rejection trigger until investigated; it is not accepted automatically.

### 10.7 Completed S-01 Acceptance Result

| Item | Result |
|---|---:|
| Input | 138 |
| Output | 138 |
| Rejected | 0 |
| Rejection rate | 0% |
| Validation | PASS |
| Metadata | Complete for recorded run |
| Decision | **APPROVED** |

### 10.8 Handover Package

The Transformation Stage hands over:

- Approved transformed dataset.
- Parent extraction batch ID.
- Transformation run ID.
- Rule ID and version.
- Transformation log entry.
- Validation results.
- Input/output hashes.
- Quarantine information, when applicable.
- Transformation specification.
- Problem/mitigation documentation.

### 10.9 Handover Responsibility

The Transformation Stage is responsible for producing a validated, documented, traceable output. The Load Stage is responsible for receiving the approved artifact and performing the next ETL stage.

### 10.10 Handover Status

A batch is **HANDED OVER** only after the approved package is complete and the downstream Load Stage can identify the exact output artifact. The current S-01 batch is **VALIDATED — PASS** and **APPROVED**; final `HANDED OVER` status is a downstream receipt state, not merely a transformation-run status.

## 11. Common Transformation Problems and Mitigation

| Problem | Possible Cause | Impact | Mitigation |
|---|---|---|---|
| Inconsistent source identifiers | Multiple source IDs represent the same model | Incorrect grouping and reporting | Apply S-01; validate both mapping directions |
| Blank required transformation value | Missing `model_name` | Cannot safely create canonical ID | Quarantine; record rule/reason/run/source row |
| Canonical ID collision | Different names produce the same slug | Incorrect entity merging | Fail validation and correct canonicalization rule |
| Record-count reconciliation failure | Dropped/duplicated rows | Incomplete or inflated output | Hold batch; investigate and rerun |
| Rejection rate above 1% | Systematic source or rule issue | Batch quality may be degraded | Manual review; correct cause; reprocess |
| Transformation rule failure | Unexpected value or implementation error | Incomplete/invalid output | Stop acceptance; fix rule; rerun validation |
| Duplicate output IDs | Transformation duplication | Downstream load/reporting errors | Reject until uniqueness is restored |
| Unexpected business value | Unseen source value | Unsupported standardized value | Investigate; do not invent a value |
| Source schema change | Added/removed/renamed field | Contract or transformation failure | Compare schema, update approved contract/rule, reprofile |
| Metadata/lineage failure | Missing run, batch, or hash information | Output cannot be audited | Hold acceptance until lineage is complete |
| Quarantine failure | Rejected rows not stored or traceable | Silent data loss | Restore quarantine record and audit trail |
| Output corruption | Incomplete or malformed CSV | Load cannot safely consume output | Recreate output and rerun validation |

### 11.1 General Problem-Handling Rule

Problems affecting completeness, correctness, traceability, or downstream loading must not be silently ignored. Critical failures block handover; non-critical issues require documented review.

### 11.2 Final Mitigation Principle

1. Preserve the Lab 3 handover.
2. Apply only documented transformation rules.
3. Do not invent business values.
4. Validate before acceptance.
5. Quarantine rejected records.
6. Maintain lineage and hashes.
7. Stop Load handover on Critical failure.
8. Record manual-review decisions.
