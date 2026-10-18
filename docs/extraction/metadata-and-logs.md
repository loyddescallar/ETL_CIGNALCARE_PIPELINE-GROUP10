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

## Retention

Extraction logs and metadata should be retained for the period required by the project to support:

- Reconciliation
- Troubleshooting
- Auditability
- Extraction monitoring
- ETL handover

The current implementation stores logs locally. Automated archival and deletion are not currently implemented.

## Security

The extraction logs must not contain database passwords or connection secrets.

The `.env` file, generated extraction outputs, and runtime state are excluded from source control.