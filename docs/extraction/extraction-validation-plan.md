# CignalCare+ Extraction Validation Plan

## 1. Overview

This document defines the validation checks that will be used to determine whether extracted CignalCare+ datasets are complete, structurally correct, and suitable for the succeeding ETL stages.

The validation process will compare the extracted datasets against the source database and verify table structure, record counts, primary-key integrity, completeness, and incremental extraction behavior.

The validation process must not modify source records or expose credentials and unnecessary sensitive customer information.

---

## 2. Validation Scope

The validation plan applies to the eight required source tables:

- `users`
- `prepaid_plans`
- `prepaid_transactions`
- `load_requests`
- `tickets`
- `technician_requests`
- `troubleshoot_outcomes`
- `support_incidents`

The checks will be applied to both full extraction and incremental extraction activities where applicable.

---

## 3. Validation Checks

### 3.1 Source Connectivity

The extraction process must successfully connect to the CignalCare+ PostgreSQL/Supabase source database.

**PASS:**
- Database connection succeeds.
- Required schema is accessible.

**FAIL:**
- Connection cannot be established.
- Required source schema cannot be accessed.

---

### 3.2 Required Table Check

All eight required source tables must be available before extraction.

**PASS:**
- All required tables exist and are accessible.

**FAIL:**
- One or more required tables are missing or inaccessible.

---

### 3.3 Column Structure Check

The extracted dataset must contain the expected columns for its corresponding source table.

**PASS:**
- Expected columns are present.
- No required extraction column is missing.

**WARNING:**
- A non-critical additional column is detected.

**FAIL:**
- A required column is missing or the extracted structure does not match the expected source structure.

---

### 3.4 Source-to-Extracted Row-Count Reconciliation

The number of extracted records will be compared with the source record count.

For a full extraction:

**PASS:**
- Extracted row count equals the current source row count.

**WARNING:**
- A difference is identified and has an explainable incremental or timing-related cause.

**FAIL:**
- The extracted count is lower or otherwise inconsistent without an identified explanation.

The current source baseline contains 478 records across the eight required tables:

| Source Table | Current Baseline |
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

These values represent the profiling baseline and may change as the source database is updated.

---

### 3.5 Primary-Key NULL Check

Each extracted table must be checked for NULL values in its primary-key column.

**PASS:**
- No primary-key values are NULL.

**FAIL:**
- One or more records contain a NULL primary key.

A NULL primary key indicates an invalid or incomplete extracted record and requires review.

---

### 3.6 Duplicate Primary-Key Check

Each extracted table must be checked for duplicate primary-key values.

**PASS:**
- No duplicate primary-key values are found.

**FAIL:**
- One or more duplicate primary-key values are detected.

Duplicate primary keys may indicate duplicate extraction, incorrect processing, or source-data issues and must be investigated before the dataset proceeds.

---

### 3.7 Completeness Check

The extracted dataset must contain all required records and expected structural information.

Completeness checks include:

- Required tables are present.
- Required columns are present.
- Primary keys are populated.
- Primary keys are unique.
- Full-extraction row counts reconcile with the source.
- Extracted files are generated for the expected datasets.

**PASS:**
- All required completeness checks are satisfied.

**WARNING:**
- A non-critical discrepancy is identified and documented.

**FAIL:**
- Required records, columns, or identifiers are missing.

---

### 3.8 Incremental Extraction Validation

Incremental extraction must be validated using the configured watermark for each applicable source table.

The validation must confirm that:

- A valid previous watermark exists when required.
- The watermark is based on an appropriate source timestamp.
- Records outside the incremental extraction window are not unnecessarily re-extracted.
- New or updated records after the previous watermark are captured.
- NULL watermark conditions are detected and handled instead of silently producing an invalid incremental result.

**PASS:**
- Watermark state is valid and incremental extraction behavior is consistent with the configured rules.

**WARNING:**
- A table requires special handling because its watermark field contains NULL values or other documented limitations.

**FAIL:**
- Watermark state is invalid or incremental extraction cannot reliably determine the required source changes.

---

### 3.9 Extraction Error and Review Conditions

An extraction run must be reviewed when any of the following occurs:

- Database connection failure
- Missing required source table
- Unexpected column structure
- Source/extracted row-count mismatch without explanation
- NULL primary key
- Duplicate primary key
- Invalid or missing watermark
- Unexpected extraction exception
- Missing output file

Errors must be recorded in the extraction log and investigated before the affected dataset is accepted.

---

## 4. Validation Status Rules

| Status | Meaning |
|---|---|
| **PASS** | The validation requirement is satisfied and the dataset can proceed. |
| **WARNING** | A non-critical condition exists and has been documented for review. |
| **FAIL** | A required validation condition is not satisfied and the dataset must not proceed without resolution. |

A dataset should be considered acceptable for the succeeding ETL stage only when all required checks pass and no unresolved failure condition remains.

---

## 5. Validation Evidence

Each extraction validation run should retain sufficient evidence to support the result, including:

- Extraction batch identifier
- Source table name
- Source row count
- Extracted row count
- Expected column structure
- Primary-key validation result
- Duplicate check result
- Watermark state where applicable
- Validation status
- Error or warning information when applicable

Raw customer records and credentials must not be included as validation evidence.

---

## 6. Acceptance Criteria

An extracted dataset is accepted when:

1. The source connection succeeds.
2. All required source tables are available.
3. The extracted column structure matches the expected structure.
4. Source and extracted row counts reconcile for a full extraction.
5. Primary-key NULL checks pass.
6. Duplicate primary-key checks pass.
7. Required completeness checks pass.
8. Incremental extraction and watermark checks pass where applicable.
9. No unresolved extraction failure is present.

---

## 7. Validation Conclusion

This validation plan establishes the acceptance checks for the CignalCare+ extraction stage.

The plan provides a consistent method for verifying source connectivity, required tables, schema structure, record completeness, primary-key integrity, incremental extraction behavior, and extraction errors.

The defined PASS, WARNING, and FAIL conditions will be used during the actual extraction implementation and validation stages.