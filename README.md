# Data Extraction Documentation

## 1. Data Source and Extraction Specification

### Source System Name

**CignalCare+: A Subscriber Support, Transaction, and Records Management System for Descallar Satellite Services**

CignalCare+ is the operational system that records subscriber accounts, prepaid transactions, load requests, support tickets, technician requests, troubleshooting outcomes, and support incidents. These operational records provide the source data required for the CignalCare+ Daily Support and Transaction Analytics Batch Pipeline.

The purpose of the extraction stage is to retrieve the required operational records from the CignalCare+ source database and prepare them as controlled input for the succeeding ETL stages.

### Source Database / Database Management System

The extraction source is a **Supabase-hosted PostgreSQL operational database** using the `public` schema.

The selected source tables are:

- `users`
- `prepaid_plans`
- `prepaid_transactions`
- `load_requests`
- `tickets`
- `technician_requests`
- `troubleshoot_outcomes`
- `support_incidents`

The source database remains the operational system of record. The extraction process is intended to retrieve source records without modifying the operational tables.

### Extraction Method

The pipeline uses a **full extraction for initial loading and incremental extraction for succeeding runs**.

For the initial extraction, the required source tables are retrieved in full so that a complete baseline dataset is available for validation and succeeding pipeline stages.

For subsequent extraction runs, the pipeline uses timestamp-based watermarks to identify records that have changed or were added after the previous successful extraction. This reduces unnecessary re-extraction of records that have already been processed.

The extraction process records the latest successful watermark for each applicable source table. The watermark is used as the reference point for the next incremental extraction.

### Initial Extraction Baseline

The initial source profiling identified the following records:

| Source Table | Records |
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

The baseline extraction was validated against the source database and produced **478 extracted records** across the eight required source tables.

### Extraction Schedule

The proposed CignalCare+ batch pipeline is designed for **daily processing at 12:00 AM**.

Apache Airflow is identified in the Lab 2 pipeline design as the orchestration tool responsible for scheduling and coordinating the batch process. The extraction specification documented here defines the source and extraction requirements that the orchestration layer will execute.

### Extraction Scope

The extraction stage is limited to the operational records required by the CignalCare+ analytics pipeline.

The extraction scope covers:

- Subscriber account information required for analytics
- Prepaid plan information
- Prepaid transaction records
- Load request records
- Customer support ticket records
- Technician request records
- Troubleshooting outcome records
- Support incident records

The extraction stage does not perform the final business transformations or analytics aggregation. Those activities belong to the succeeding stages of the ETL pipeline.

### Extraction Requirements

The extraction process must:

1. Connect to the CignalCare+ PostgreSQL source database.
2. Read the required tables from the `public` schema.
3. Preserve the source records and source identifiers needed for downstream processing.
4. Support an initial full extraction.
5. Support succeeding incremental extractions using applicable watermarks.
6. Record extraction execution information.
7. Validate the extracted datasets against the source structure and record counts.
8. Prevent credentials and sensitive source information from being committed to version control.

### Current Extraction Findings

Initial source profiling and validation identified the following conditions:

- All eight required source tables are available.
- Primary keys were present and contained no NULL values in the profiled tables.
- No duplicate primary-key rows were found in the profiled tables.
- Declared foreign-key relationships in the transaction, load-request, ticket, and technician-request tables did not contain orphan references.
- The initial full extraction successfully retrieved all **478 source records**.
- Extraction validation confirmed matching source and extracted record counts.
- A succeeding incremental extraction returned zero new records when no qualifying source changes were present.
- The extraction process maintains watermark information for succeeding runs.

### Extraction Limitation

The extraction stage is responsible for retrieving and validating source data. Data standardization, business transformations, dimensional modeling, aggregation, and analytics calculations are outside the extraction stage and will be addressed in the succeeding ETL stages.

---

## 2. Source Tables and Column Specification

The CignalCare+ extraction scope consists of eight operational source tables located in the PostgreSQL `public` schema.

Detailed column definitions, data types, source identifiers, timestamps, and extraction relevance will be documented under:

`docs/extraction/source-schema.md`

---

## 3. Extraction Validation and Data Quality Checks

The extraction process must verify that the extracted datasets preserve the expected source structure and required records.

Validation includes:

- Column structure validation
- Source-to-extracted record count comparison
- Primary-key duplicate checking
- Primary-key NULL checking
- Watermark validation
- Required source table verification
- Relationship and linkage checks where applicable

The detailed validation rules and results will be documented under:

`docs/extraction/validation.md`

---

## 4. Extraction Metadata and Log Specification

Each extraction execution must produce traceable execution information, including:

- Batch identifier
- Source table
- Extraction timestamp
- Extraction mode
- Number of records extracted
- Output location
- Watermark information
- Execution status
- Error information when applicable

Detailed metadata and logging specifications will be documented under:

`docs/extraction/metadata-and-logs.md`

---

## 5. Log Retention and Access

Extraction logs and metadata must be retained sufficiently to support:

- Pipeline monitoring
- Extraction verification
- Error investigation
- Reconciliation
- Audit and traceability

Credentials, passwords, and other sensitive configuration values must not be stored in source-controlled documentation or extraction logs.

The detailed retention and access rules will be documented under:

`docs/extraction/log-retention-and-access.md`

---

## 6. Extraction Data Contract and Naming Convention

The extraction data contract defines the expected structure of extracted datasets, including:

- Source table identification
- Required columns
- Primary-key preservation
- Timestamp handling
- Output file naming
- Batch identification
- Extraction mode identification

The detailed extraction data contract and naming conventions will be documented under:

`docs/extraction/data-contract.md`

---

## 7. Extraction Acceptance and Handover Rules

An extraction batch is considered acceptable when:

1. All required source tables are successfully processed.
2. The extracted structure matches the expected source structure.
3. Required primary keys are preserved.
4. Duplicate primary keys are not introduced.
5. Extracted record counts reconcile with the source for the applicable extraction scope.
6. Watermark information is valid for incremental processing.
7. Execution status and metadata are recorded.
8. No unresolved extraction error prevents downstream processing.

The detailed acceptance and handover rules will be documented under:

`docs/extraction/acceptance-and-handover.md`

---

## 8. Common Extraction Problems and Mitigation

Common extraction problems may include:

- Database connection failure
- Authentication failure
- Missing source tables
- Schema or column changes
- NULL timestamp/watermark values
- Duplicate source identifiers
- Record-count mismatch
- Invalid incremental watermark state
- Network or database availability problems

Extraction errors must be recorded and investigated before an affected batch is accepted for downstream processing.

Detailed problem scenarios and mitigation procedures will be documented under:

`docs/extraction/problems-and-mitigation.md`