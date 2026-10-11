# CignalCare+ Source System and Extraction Scope

## 1. Source System

CignalCare+ is a Subscriber Support, Transaction, and Records Management System for Descallar Satellite Services. It stores operational records generated from different system functions, including subscriber accounts, prepaid transactions, load requests, support tickets, technician requests, troubleshooting outcomes, and support incidents.

These operational records serve as the source data for the CignalCare+ Daily Support and Transaction Analytics Batch Pipeline. The extracted data will be used as input for the succeeding stages of the ETL process.

---

## 2. Source Database

The source system uses a Supabase-hosted PostgreSQL operational database.

The required source tables are located under the `public` schema.

The extraction process reads the required operational records from the source database. The operational source records are not modified during extraction.

The proposed analytics environment is separate from the operational source database. This separation allows the extracted and processed information to be used for analytics without replacing or modifying the original operational records.

---

## 3. Required Source Tables

The Lab 3 extraction scope consists of the following eight source tables:

| Source Table | Purpose |
|---|---|
| `users` | Stores subscriber and account information used to associate operational records. |
| `prepaid_plans` | Stores available prepaid plan information. |
| `prepaid_transactions` | Stores prepaid transaction records. |
| `load_requests` | Stores subscriber load-request and payment-related activity. |
| `tickets` | Stores customer support ticket records. |
| `technician_requests` | Stores requests for technician assistance and service coordination. |
| `troubleshoot_outcomes` | Stores troubleshooting activity and outcome records. |
| `support_incidents` | Stores identified support incident information. |

These eight tables were identified as the operational source tables for the CignalCare+ analytics pipeline. :chatgpt-content-reference{index="1"}

---

## 4. Purpose of the Extraction Stage

The purpose of the extraction stage is to retrieve the operational records required by the CignalCare+ analytics pipeline.

The extracted data will provide the source input needed for succeeding validation, transformation, joining, and analytics processes.

The extracted information can support analysis of:

- Prepaid transaction activity
- Load-request activity and status
- Customer support tickets
- Resolved and pending support concerns
- Technician requests
- Troubleshooting activity
- Recurring service issues
- Support incident information
- Daily transaction and support indicators

The extraction stage focuses on obtaining the required source records. Data transformation and analytics calculations are performed in later stages of the ETL pipeline.

---

## 5. Extraction Scope

The extraction scope is limited to the eight required operational tables under the `public` schema:

1. `users`
2. `prepaid_plans`
3. `prepaid_transactions`
4. `load_requests`
5. `tickets`
6. `technician_requests`
7. `troubleshoot_outcomes`
8. `support_incidents`

The extraction includes the source fields and records required for downstream validation, relationship analysis, transformation, and analytics processing.

Source identifiers and relevant timestamp fields are retained where applicable so that extracted records can be tracked and validated.

---

## 6. Extraction Boundaries

The extraction stage is responsible for retrieving source data from the CignalCare+ operational database.

The extraction stage does not include the final:

- Data transformation
- Dimensional modeling
- Business KPI computation
- Daily aggregation
- Analytics dashboard generation

These activities belong to succeeding ETL stages.

The extraction process also does not modify, delete, or replace records in the CignalCare+ operational database.

The source database remains the operational system of record.

---

## 7. Extraction Approach

The extraction workflow supports both an initial full extraction and subsequent incremental extraction.

### Initial Full Extraction

The initial extraction retrieves the required records from all eight source tables to establish the baseline dataset.

### Incremental Extraction

After the baseline extraction, subsequent runs use timestamp-based watermark information to identify records that qualify for incremental extraction.

The watermark state is maintained separately from the source records and is used to determine the point from which succeeding extraction runs should retrieve data.

---

## 8. Assumptions

The extraction process is based on the following assumptions:

- The CignalCare+ PostgreSQL source database is available to the extraction process.
- The eight required source tables are available under the `public` schema.
- The extraction process has read access to the required source tables.
- Source primary keys are available for record identification.
- Relevant timestamp fields are available for incremental extraction where applicable.
- The operational database remains the source of record.
- Source records are not modified as part of the extraction process.

---

## 9. Source Limitations

The source tables do not have identical structures or timestamp fields.

Some source fields may contain NULL values. During initial extraction testing, a NULL watermark condition was encountered in `prepaid_plans`. This demonstrates that incremental extraction requires appropriate handling of source timestamp or watermark fields before an incremental batch can be considered valid.

The source database also contains relationships that are represented through both declared foreign keys and application-level references. These relationships require separate validation before the data is used for downstream processing.

The source data may also contain operational information that should not be unnecessarily exposed in documentation or source-controlled files.

---

## 10. Access and Security Considerations

Access to the CignalCare+ source database requires valid database credentials.

Database passwords, API keys, and other sensitive credentials must not be stored directly in source code or committed to the GitHub repository.

Environment variables should be used to provide database connection credentials to the extraction process.

The extraction process should use the minimum database permissions required to read the source tables.

Extracted datasets and execution logs must also be handled carefully because the source records may contain subscriber-related information.

Documentation and source-controlled files should not contain passwords, credentials, or unnecessary personally identifiable information.

---

## 11. Extraction Scope Summary

The defined Lab 3 extraction scope is:

CignalCare+ Operational System
→ Supabase-hosted PostgreSQL
→ `public` schema
→ Eight required source tables
→ Source Extraction
→ Validation
→ Succeeding ETL Stages

The extraction stage provides the controlled source datasets required for the succeeding validation, transformation, and analytics processes.