# CignalCare+ Extraction Problems and Mitigation

## Purpose

This document identifies common problems that may occur during the CignalCare+ Lab 3 extraction stage and defines the recommended mitigation actions.

## 1. Database Connection Failure

### Problem

The extraction process cannot connect to the PostgreSQL/Supabase source database.

### Possible Causes

- Incorrect database configuration
- Network connectivity issue
- Database availability issue
- Incorrect SSL configuration

### Mitigation

1. Verify the local `.env` configuration.
2. Confirm that the database is accessible.
3. Verify the SSL configuration.
4. Retry the extraction.
5. Review the extraction error and execution log.

Database credentials must not be placed in source-controlled files.

## 2. Missing Source Table

### Problem

A required source table is unavailable.

### Mitigation

1. Confirm that the table exists in the expected schema.
2. Verify database permissions.
3. Compare the current source structure with the documented source schema.
4. Do not accept the extraction batch until the issue is resolved or formally reviewed.

## 3. Missing or Renamed Column

### Problem

An expected source column is missing or has been renamed.

### Mitigation

1. Review the current source schema.
2. Compare it with the extraction data contract.
3. Determine whether the change is intentional.
4. Update the extraction configuration if approved.
5. Re-run extraction validation.
6. Document the schema change.

## 4. NULL Watermark

### Problem

The configured watermark expression produces a NULL value.

### Mitigation

Tables configured with:

`COALESCE(updated_at, created_at)`

use `created_at` when `updated_at` is NULL.

If the calculated watermark remains NULL, the extraction must fail rather than save an invalid watermark.

The affected source records should then be reviewed.

## 5. Invalid Watermark State

### Problem

The saved watermark does not represent the correct extraction position.

### Mitigation

1. Review `state/watermarks.json`.
2. Compare the saved watermark with the source.
3. Review `state/extraction_log.csv`.
4. Identify the cause of the invalid state.
5. Perform a controlled full extraction if a new baseline is required.
6. Re-run validation.

## 6. Record-Count Mismatch

### Problem

The source record count does not match the extracted record count.

### Mitigation

1. Identify the affected table.
2. Review the extraction log.
3. Verify that the correct output file was used.
4. Check whether the source changed during extraction.
5. Re-run the validation.
6. Do not hand over the affected dataset until the mismatch is explained.

## 7. Duplicate Primary Keys

### Problem

Duplicate primary-key values are found in the extracted dataset.

### Mitigation

1. Identify the affected records.
2. Check whether the duplication exists in the source.
3. Review the extraction process.
4. Correct the cause.
5. Re-run extraction validation.

## 8. NULL Primary Keys

### Problem

A primary-key field contains a NULL value.

### Mitigation

The dataset should fail validation.

The source table and extraction configuration must be reviewed to determine the cause.

## 9. Unexpected Incremental Records

### Problem

An incremental extraction returns records when no expected source changes were identified.

### Mitigation

1. Review the saved watermark.
2. Check source timestamps.
3. Check the primary-key tie-breaker.
4. Review the extraction log.
5. Determine whether the records were newly created or updated.

## 10. Zero Incremental Records

### Problem

An incremental extraction returns zero records.

### Interpretation

Zero records is not automatically an error.

If the source has not changed since the previous successful extraction, zero incremental records is the expected result.

The current unchanged-source test returned zero records across all eight required tables.

## 11. Missing Output File

### Problem

An expected extraction CSV file is missing.

### Mitigation

1. Review the extraction log.
2. Check `data/extracted/`.
3. Confirm whether the extraction completed successfully.
4. Re-run the affected extraction if necessary.
5. Re-run validation.

## 12. Schema Change

### Problem

The source database structure changes after the extraction contract has been established.

### Mitigation

1. Identify the changed table or column.
2. Compare the new structure with the documented schema.
3. Determine whether the change affects extraction.
4. Update the extraction configuration if approved.
5. Update the documentation.
6. Re-run extraction validation.

## 13. Credential Exposure

### Problem

Database credentials or sensitive configuration are accidentally placed in the repository.

### Mitigation

1. Remove the exposed credentials.
2. Ensure `.env` is ignored by Git.
3. Check whether the credentials were committed.
4. Rotate credentials when necessary.
5. Remove sensitive information from documentation and logs.

## 14. General Handover Rule

The extraction stage must not be handed over when there is an unresolved:

- Extraction failure
- Record-count mismatch
- Invalid watermark
- Missing required table
- Missing required column
- Primary-key integrity failure
- Security or credential exposure

All unresolved issues must be reviewed and resolved before succeeding ETL stages consume the affected dataset.