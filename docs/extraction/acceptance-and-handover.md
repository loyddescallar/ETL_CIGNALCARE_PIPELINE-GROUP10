# CignalCare+ Extraction Acceptance and Handover

## Purpose

This document defines the acceptance criteria for the CignalCare+ Lab 3 extraction stage and the requirements for handing the extracted datasets to succeeding ETL stages.

## Extraction Acceptance Criteria

The extraction stage is acceptable when:

1. PostgreSQL/Supabase connectivity is successful.
2. All eight required source tables are available.
3. Required source columns are available.
4. Extracted columns match the defined extraction structure.
5. Source and extracted row counts reconcile for a full extraction.
6. Primary-key NULL checks pass.
7. Duplicate primary-key checks pass.
8. Watermark state is valid.
9. Required extraction outputs are generated.
10. Extraction execution information is logged.
11. No unresolved extraction failure remains.

## Acceptance Decision Rules

The extraction result is classified using the following decision rules:

| Overall Condition | Acceptance Decision | Pipeline Action | Decision Type | Responsible Role |
|---|---|---|---|---|
| All required validation checks PASS | APPROVED | Proceed to Transformation | Automatic | Extraction/ETL Lead |
| One or more non-critical WARNING conditions | MANUAL REVIEW | Hold dataset until reviewed | Manual | Extraction/ETL Lead |
| One or more critical validation checks FAIL | REJECTED | Stop affected pipeline stage and resolve/retry | Automatic stop + manual resolution | Extraction/ETL Lead |
| Validation passes and handover package is complete | HANDED OVER | Provide extracted datasets, metadata, logs, and validation results to Transformation | Automatic after acceptance | Extraction/ETL Lead |

### Automatic Approval

Automatic approval is permitted when:

- PostgreSQL/Supabase connection succeeds.
- All eight required tables are available.
- Required columns are present.
- Primary keys contain no NULL values.
- Primary keys are unique.
- Source and extracted row counts reconcile for the full extraction.
- Watermark validation passes.
- No critical extraction error is present.

### Manual Review

Manual review is required when:

- A non-critical warning is detected.
- An unexpected but explainable record-count difference occurs.
- A documented source limitation affects the extraction.
- A schema change requires confirmation.
- Additional investigation is required before handover.

The affected dataset must remain on hold until the Extraction/ETL Lead determines whether it can proceed.

### Rejection or Failure

The extraction must be rejected or stopped when:

- A required source table is unavailable.
- A required column is missing.
- A critical extraction error occurs.
- Primary-key validation fails.
- Duplicate primary keys are detected.
- Source and extracted records cannot be reconciled without explanation.
- Watermark state is invalid.
- Required extraction output is missing.

The affected extraction must be corrected and revalidated before proceeding.

## Handover Package

The following information is passed to the Transformation Stage:

- Validated extracted CSV datasets
- Extraction batch information
- Extraction log
- Watermark state
- Validation results
- Data contract
- Source schema documentation
- Known source limitations
- Problems and mitigation documentation

The handover confirms that the extraction stage has completed its responsibility without performing data cleaning, standardization, or business transformation.

## Validated Baseline

The completed full extraction produced:

| Source Table | Source Records | Extracted Records |
|---|---:|---:|
| `users` | 107 | 107 |
| `prepaid_plans` | 8 | 8 |
| `prepaid_transactions` | 110 | 110 |
| `load_requests` | 58 | 58 |
| `tickets` | 37 | 37 |
| `technician_requests` | 19 | 19 |
| `troubleshoot_outcomes` | 138 | 138 |
| `support_incidents` | 1 | 1 |
| **Total** | **478** | **478** |

The extraction validation resulted in:

- 8 tables passed
- 0 tables failed
- 478 source records
- 478 extracted records
- Overall validation status: PASS

## Incremental Acceptance

After the successful full extraction, an incremental extraction was executed without changing the source data.

Result:

- Tables processed: 8
- Incremental records extracted: 0

The zero-record result is expected because no qualifying source changes were present.

## Handover Criteria

The extraction datasets may be handed over to succeeding ETL stages when:

- Full extraction validation passes.
- Required source tables are available.
- Expected columns are preserved.
- Primary keys are preserved.
- Row counts reconcile.
- Watermark state is valid.
- Extraction metadata is available.
- No unresolved extraction errors remain.

## Handover Package

The extraction documentation package includes:

- Source and extraction scope
- Source schema
- Source value profiling
- Relationship validation
- Extraction validation plan
- Extraction validation results
- Incremental extraction documentation
- Metadata and logging documentation
- Data contract
- Acceptance and handover criteria
- Problems and mitigation procedures

## Downstream Boundary

The extraction stage provides source datasets for succeeding ETL stages.

The extraction stage does not perform final:

- Data transformation
- Business-rule processing
- Dimensional modeling
- Aggregation
- Analytics calculations

These activities are performed by succeeding ETL stages.

## Traceability

Each extraction run is associated with a unique batch identifier.

The extraction log records the batch identifier, source table, extraction mode, record count, timestamps, watermark information, status, and output file.

This provides traceability between an extraction run and its generated datasets.

## Security Requirements

The handover package must not contain:

- Database passwords
- Connection secrets
- Authentication credentials
- Unnecessary sensitive customer information

The `.env` file and generated runtime files remain outside source control.

## Final Acceptance

The CignalCare+ Lab 3 extraction stage is considered ready for handover when the defined acceptance criteria pass and the required documentation package is complete.