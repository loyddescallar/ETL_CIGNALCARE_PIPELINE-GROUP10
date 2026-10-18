# CignalCare+ Extraction Data Contract

## Purpose

This document defines the expected structure of the datasets produced by the CignalCare+ Lab 3 extraction stage.

The extraction contract ensures that the required source tables, identifiers, columns, and source values are preserved for succeeding ETL stages.

## Required Source Tables

The extraction process covers the following eight source tables:

- `users`
- `prepaid_plans`
- `prepaid_transactions`
- `load_requests`
- `tickets`
- `technician_requests`
- `troubleshoot_outcomes`
- `support_incidents`

## Source Column Structure

The extraction process uses an explicit list of approved source columns for each table.

The extracted output preserves the configured source column names.

The extraction stage does not rename columns for business or analytical purposes.

This keeps the extraction stage focused on obtaining the required source data.

## Identifiers and Primary Keys

The source primary key for each required table is:

| Table | Primary Key |
|---|---|
| `users` | `id` |
| `prepaid_plans` | `id` |
| `prepaid_transactions` | `id` |
| `load_requests` | `id` |
| `tickets` | `id` |
| `technician_requests` | `id` |
| `troubleshoot_outcomes` | `id` |
| `support_incidents` | `id` |

Primary-key values are preserved during extraction.

## Foreign Keys and Linkage Fields

Relevant source linkage fields include:

| Table | Field | Related Source |
|---|---|---|
| `prepaid_transactions` | `user_id` | `users.id` |
| `prepaid_transactions` | `plan_id` | `prepaid_plans.id` |
| `load_requests` | `user_id` | `users.id` |
| `load_requests` | `plan_id` | `prepaid_plans.id` |
| `tickets` | `user_id` | `users.id` |
| `technician_requests` | `user_id` | `users.id` |

Other source linkage fields such as `incident_id`, `issue_id`, and `issue_key` are preserved when included in the extraction configuration.

## Expected Data Types

The extraction follows the source database data types.

Expected data categories include:

- Integer identifiers
- Text and character fields
- Numeric values
- Date values
- Timestamp values
- Boolean or flag values

The extraction process converts database values into CSV-compatible representations while preserving their source meaning.

## Nullable Fields

Source NULL values are preserved as empty CSV values.

The extraction process does not replace NULL source values with artificial defaults.

Primary-key NULL values are treated as a validation failure.

## Timestamp Fields

Timestamp values are extracted from the source database without replacing them with extraction timestamps.

Extraction execution timestamps are recorded separately as metadata using UTC.

## Schema-Change Handling

The extraction process uses an explicit column configuration.

If a required source column is removed or renamed, the extraction configuration must be reviewed.

The following procedure should be followed:

1. Identify the schema change.
2. Compare the current source schema with the documented schema.
3. Determine the effect on the extraction contract.
4. Update the extraction configuration when appropriate.
5. Re-run extraction validation.
6. Document the approved schema change.

Unexpected schema changes must not be silently ignored.

## Output Naming

Extracted datasets use:

`<UTC timestamp>_<table_name>.csv`

Example:

`20261018T170820579959Z_prepaid_transactions.csv`

## Transformation Boundary

The extraction stage preserves the required source structure.

The following activities are outside the extraction stage:

- Business-rule transformation
- Data standardization
- Aggregation
- Dimension creation
- Fact-table creation
- Analytics calculations

These activities belong to succeeding ETL stages.

## Security Boundary

Database credentials are provided through environment variables and are not included in the extraction data contract.

Generated extraction files and runtime state are treated as local operational artifacts.