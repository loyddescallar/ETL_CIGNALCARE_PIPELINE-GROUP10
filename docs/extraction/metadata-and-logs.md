# CignalCare+ Extraction Metadata and Logging

## Purpose

This document defines the metadata and logging information recorded during the CignalCare+ Lab 3 extraction process.

The metadata provides traceability for each extraction run and supports monitoring, validation, troubleshooting, and handover.

## Batch and Run Identifiers

Each extraction run is assigned a unique batch identifier based on the UTC timestamp.

Example:

`20261018T170820026121Z`

The batch identifier is recorded in the extraction execution log and identifies the extraction run across the processed source tables.

## Extraction Timestamps

The extraction process records timestamps using UTC.

The following timestamps are recorded:

- Extraction start time
- Extraction completion time
- Watermark update time

Source timestamps remain unchanged and are extracted as source values.

## Records Read, Extracted, and Rejected

The extraction process records the number of records successfully extracted from each source table.

The validated full-extraction baseline was:

| Source Table | Records Extracted |
|---|---:|
| `users` | 107 |
| `prepaid_plans` | 8 |
| `prepaid_transactions` | 110 |
| `load_requests` | 58 |
| `tickets` | 37 |
| `technician_requests` | 19 |
| `troubleshoot_outcomes` | 138 |
| `support_incidents` | 1 |
| **Total** | **478** |

The current extraction process does not implement a separate rejected-record dataset. If an extraction operation fails, the affected table is logged as failed rather than silently rejecting individual records.

## Metadata Field Specification

The extraction metadata is defined to provide traceability for every extraction run.

| Metadata Field | Purpose | Example / Format |
|---|---|---|
| `batch_id` | Unique identifier for the extraction run | `20261018T170820026121Z` |
| `table_name` | Identifies the processed source table | `users` |
| `mode` | Identifies the extraction type | `full_initial` / `incremental` |
| `started_at` | Records extraction start time | ISO 8601 UTC timestamp |
| `finished_at` | Records extraction completion time | ISO 8601 UTC timestamp |
| `extracted_rows` | Number of records written to the extraction output | `107` |
| `records_read` | Number of records returned from the source query | `107` |
| `records_rejected` | Number of records rejected during extraction | `0` for successful extraction |
| `extraction_window` | Identifies the source time range used by the extraction | Watermark expression and saved watermark |
| `watermark_expression` | Identifies the source field or expression used for incremental extraction | `COALESCE(updated_at, created_at)` |
| `new_watermark` | Records the latest successful watermark | ISO 8601 timestamp |
| `new_watermark_id` | Records the primary-key tie-breaker associated with the watermark | `107` |
| `status` | Identifies whether the table extraction succeeded or failed | `SUCCESS` / `FAILED` |
| `validation_result` | Records the result of extraction validation | `PASS` / `WARNING` / `FAIL` |
| `error_code` | Identifies the error type when an extraction fails | Python exception type |
| `error_message` | Describes the extraction failure | Error message text |
| `extraction_duration` | Measures the elapsed time of the extraction | Derived from `started_at` and `finished_at` |

For the current implementation, `records_read` corresponds to the number of rows returned by the source query and therefore equals `extracted_rows` when no row-level rejection occurs.

The current extraction log stores the operational run information in `state/extraction_log.csv`. Validation results are produced separately by the extraction validation process.

## Metadata and Log Usage

The metadata and logs are used for:

- **Monitoring** — Determine whether an extraction run completed successfully.
- **Troubleshooting** — Identify the affected table, extraction mode, and error information.
- **Auditing** — Trace which batch processed which source table and when it occurred.
- **Recovery** — Determine the last successful watermark and identify the correct point for a controlled rerun.
- **Reconciliation** — Compare extracted record counts with source record counts.

## Extraction Windows

The initial extraction uses a full extraction window covering the available source records.

Subsequent runs use the saved watermark for each table.

Records are selected when their watermark is newer than the saved watermark. When multiple records have the same watermark value, the primary-key value is used as a deterministic tie-breaker.

## Logging

Execution information is stored in:

`state/extraction_log.csv`

The log contains:

- Batch identifier
- Table name
- Extraction mode
- Number of extracted records
- Start timestamp
- Completion timestamp
- Watermark expression
- New watermark
- New watermark record identifier
- Execution status
- Output file

## Watermark State

Watermark information is stored in:

`state/watermarks.json`

The state records the latest successful watermark and corresponding record identifier for each source table.

Watermark state is updated only after the extraction output has been successfully generated.

## Naming Convention

Extracted files follow this format:

`<UTC timestamp>_<table_name>.csv`

Example:

`20261018T170820480125Z_users.csv`

This naming convention provides unique and traceable extraction output files.

## Log Retention and Access

### Retention Period

For the Lab 3 project, operational extraction logs and watermark metadata should be retained for **90 days**.

The 90-day period provides sufficient history for:

- Troubleshooting extraction failures
- Comparing extraction runs
- Reviewing incremental extraction behavior
- Supporting validation and reconciliation
- Maintaining an operational audit trail

Logs associated with an unresolved incident, validation failure, or investigation must be retained until the issue is resolved even when the normal retention period has elapsed.

### Storage Location

Operational extraction logs are stored locally in:

`state/extraction_log.csv`

Watermark state is stored in:

`state/watermarks.json`

Generated extraction datasets are stored in:

`data/extracted/`

### Access Permissions

Access should be limited to authorized members responsible for the ETL pipeline.

The following information must not be exposed through logs:

- Database passwords
- API keys
- Authentication tokens
- Unnecessary personally identifiable information

### Archiving

Logs required beyond the normal operational retention period may be archived to an approved project storage location.

Archived files must retain their original batch identifiers and timestamps to preserve traceability.

### Deletion

Operational logs may be deleted only after:

1. The 90-day retention period has expired.
2. There are no unresolved extraction or validation issues requiring the logs.
3. The logs are no longer required for project auditing or recovery.

Deletion should be performed as part of a controlled maintenance process by the person responsible for ETL operations.

Logs must not be deleted while they are required for troubleshooting, auditing, or recovery.

## Security

The extraction logs must not contain database passwords or connection secrets.

The `.env` file, generated extraction outputs, and runtime state are excluded from source control.