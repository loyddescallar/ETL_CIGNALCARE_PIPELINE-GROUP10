# CignalCare+ Extraction Validation Results

## 1. Validation Summary

The extracted CignalCare+ datasets were validated against the PostgreSQL/Supabase source using the validation criteria defined for Lab 3.

| Metric | Result |
|---|---:|
| Tables validated | 8 |
| Tables passed | 8 |
| Tables failed | 0 |
| Source records | 478 |
| Extracted records | 478 |
| Overall validation | **PASS** |

## 2. Table-Level Results

| Table | Source Rows | Extracted Rows | Columns | PK NULL | Duplicate PK | Watermark | Completeness | Status |
|---|---:|---:|---|---|---|---|---|---|
| users | 107 | 107 | PASS | PASS | PASS | PASS | PASS | **PASS** |
| prepaid_plans | 8 | 8 | PASS | PASS | PASS | PASS | PASS | **PASS** |
| prepaid_transactions | 110 | 110 | PASS | PASS | PASS | PASS | PASS | **PASS** |
| load_requests | 58 | 58 | PASS | PASS | PASS | PASS | PASS | **PASS** |
| tickets | 37 | 37 | PASS | PASS | PASS | PASS | PASS | **PASS** |
| technician_requests | 19 | 19 | PASS | PASS | PASS | PASS | PASS | **PASS** |
| troubleshoot_outcomes | 138 | 138 | PASS | PASS | PASS | PASS | PASS | **PASS** |
| support_incidents | 1 | 1 | PASS | PASS | PASS | PASS | PASS | **PASS** |

## 3. Validation Criteria

### Source-to-Extracted Row Counts

The source row count must match the corresponding full extraction output row count.

### Column Structure

The extracted CSV header must match the approved column structure defined for the source table.

### Primary-Key Integrity

Primary-key values must not be NULL or duplicated in the extracted output.

### Watermark State

The persisted watermark and record identifier must match the latest watermark position identified in the source table.

### Completeness

A table is complete when its full extraction row count reconciles with the source and its required schema and primary-key checks pass.

## 4. Validation Notes

### `users`
- All expected source columns are available.
- Extracted column structure matches the expected extraction structure.
- No NULL primary-key values detected.
- No duplicate primary-key values detected.
- Saved watermark matches the latest source watermark.

### `prepaid_plans`
- All expected source columns are available.
- Extracted column structure matches the expected extraction structure.
- No NULL primary-key values detected.
- No duplicate primary-key values detected.
- Saved watermark matches the latest source watermark.

### `prepaid_transactions`
- All expected source columns are available.
- Extracted column structure matches the expected extraction structure.
- No NULL primary-key values detected.
- No duplicate primary-key values detected.
- Saved watermark matches the latest source watermark.

### `load_requests`
- All expected source columns are available.
- Extracted column structure matches the expected extraction structure.
- No NULL primary-key values detected.
- No duplicate primary-key values detected.
- Saved watermark matches the latest source watermark.

### `tickets`
- All expected source columns are available.
- Extracted column structure matches the expected extraction structure.
- No NULL primary-key values detected.
- No duplicate primary-key values detected.
- Saved watermark matches the latest source watermark.

### `technician_requests`
- All expected source columns are available.
- Extracted column structure matches the expected extraction structure.
- No NULL primary-key values detected.
- No duplicate primary-key values detected.
- Saved watermark matches the latest source watermark.

### `troubleshoot_outcomes`
- All expected source columns are available.
- Extracted column structure matches the expected extraction structure.
- No NULL primary-key values detected.
- No duplicate primary-key values detected.
- Saved watermark matches the latest source watermark.

### `support_incidents`
- All expected source columns are available.
- Extracted column structure matches the expected extraction structure.
- No NULL primary-key values detected.
- No duplicate primary-key values detected.
- Saved watermark matches the latest source watermark.

## 5. Incremental Extraction Evidence

A subsequent incremental extraction was executed after the full extraction without changing the source data.

| Result | Value |
|---|---:|
| Tables processed | 8 |
| Incremental records extracted | 0 |
| Unchanged-source validation | **PASS** |

The zero-record result confirms that unchanged source records were not unnecessarily re-extracted during the tested incremental run.

## 6. PASS, WARNING, and Failure Conditions

- **PASS** — The required validation condition is satisfied.
- **WARNING** — A non-critical condition may require documentation or review.
- **FAIL** — A required validation condition is not satisfied.

No source records, database credentials, or other sensitive information are included in this validation report.

## 7. Conclusion

The extraction validation completed with an overall status of **PASS**. The results provide evidence that the extracted datasets can be evaluated against the defined Lab 3 extraction requirements before proceeding to succeeding ETL stages.
