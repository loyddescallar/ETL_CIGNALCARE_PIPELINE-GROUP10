# CignalCare+ Source Value Profile

## 1. Overview

This document summarizes the observed source values and data-quality characteristics of the eight required CignalCare+ source tables.

The profiling was performed against the CignalCare+ PostgreSQL/Supabase source database. The purpose of the profiling activity was to establish the current source-data baseline and identify characteristics that may affect extraction, validation, and succeeding ETL stages.

No raw customer information, credentials, or actual issue descriptions are included in this document.

---

## 2. Current Source Row Counts

The following record counts were observed during source value profiling:

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

These values represent the source-data baseline observed during the profiling run.

---

## 3. Categorical and Status Value Profiles

### 3.1 `users`

**Field:** `status`

| Value | Count |
|---|---:|
| active | 107 |

All 107 observed user records had the `active` status.

---

### 3.2 `prepaid_plans`

**Field:** `status`

| Value | Count |
|---|---:|
| active | 8 |

All 8 observed prepaid-plan records had the `active` status.

---

### 3.3 `prepaid_transactions`

**Field:** `status`

| Value | Count |
|---|---:|
| completed | 110 |

All 110 observed prepaid transactions had the `completed` status.

---

### 3.4 `load_requests`

**Field:** `payment_status`

| Value | Count |
|---|---:|
| paid | 45 |
| pending | 12 |
| manual_review | 1 |

**Field:** `status`

| Value | Count |
|---|---:|
| Completed | 45 |
| Received | 6 |
| Rejected | 6 |
| Under Review | 1 |

The source contains multiple payment and request-status categories. These fields should be preserved during extraction because they represent different operational states.

---

### 3.5 `tickets`

**Field:** `category`

| Value | Count |
|---|---:|
| Technical Problem | 16 |
| Connection Issue | 11 |
| Device Concern | 5 |
| Channel Concern | 4 |
| Other | 1 |

**Field:** `priority`

| Value | Count |
|---|---:|
| Normal | 22 |
| High | 11 |
| Urgent | 4 |

**Field:** `status`

| Value | Count |
|---|---:|
| Resolved | 19 |
| Under Review | 8 |
| Submitted | 6 |
| Job Order Assigned | 4 |

The ticket source contains multiple categories, priorities, and operational states that may be used for succeeding support analytics.

---

### 3.6 `technician_requests`

**Field:** `screen_issue`

| Value | Count |
|---|---:|
| Black Screen | 5 |
| Missing / No Channels | 5 |
| No Signal | 5 |
| Weak / Pixelated Signal | 4 |

**Field:** `source`

| Value | Count |
|---|---:|
| demo_seed | 18 |
| load_request_signal_check | 1 |

**Field:** `status`

| Value | Count |
|---|---:|
| Completed | 7 |
| Scheduled | 6 |
| Submitted | 3 |
| Under Review | 3 |

The `source` field contains two observed values, with most records originating from `demo_seed`.

---

### 3.7 `troubleshoot_outcomes`

**Field:** `issue_id`

| Value | Count |
|---|---:|
| weak_signal | 30 |
| missing_channels | 24 |
| receiver_error | 23 |
| black_screen | 21 |
| remote_issue | 20 |
| no_signal | 19 |
| e1-e2-e11 | 1 |

**Field:** `issue_label`

| Value | Count |
|---|---:|
| Weak / Pixelated Signal | 30 |
| Missing / No Channels | 24 |
| Receiver Error | 23 |
| Black Screen | 21 |
| Remote Control Issue | 20 |
| No Signal | 19 |
| E1 / E2 / E11 | 1 |

**Field:** `outcome`

| Value | Count |
|---|---:|
| started | 55 |
| resolved | 40 |
| unresolved | 16 |
| viewed | 13 |
| ticket | 10 |
| technician | 4 |

**Field:** `support_mode`

| Value | Count |
|---|---:|
| video | 41 |
| full | 36 |
| quick_restart | 31 |
| factory_reset | 30 |

The troubleshooting data contains several issue types, outcomes, and support modes. The low-frequency `e1-e2-e11` issue value is noteworthy because it occurs only once in the profiled source.

---

### 3.8 `support_incidents`

**Field:** `issue_key`

| Value | Count |
|---|---:|
| weak_signal | 1 |

**Field:** `issue_label`

| Value | Count |
|---|---:|
| Weak / Pixelated Signal | 1 |

**Field:** `status`

| Value | Count |
|---|---:|
| candidate | 1 |

Only one support-incident record was present during the profiling run. This is a source-data observation and should be considered when interpreting incident-related analytics.

---

## 4. NULL and Missing-Value Observations

The profiling process specifically checked the technician-request description field.

| Field | Total Records | Non-null | NULL |
|---|---:|---:|---:|
| `technician_requests.issueDescription` | 19 | 19 | 0 |

All 19 technician-request records contained a non-null `issueDescription`.

The actual descriptions were not displayed or reproduced in this documentation to avoid unnecessary exposure of source information.

Other nullable fields identified during schema profiling are documented in the source-schema documentation. A categorical value not appearing in the profiling output should not automatically be interpreted as NULL unless an explicit NULL check was performed.

---

## 5. Primary-Key Duplicate Check

The source profiling identified no duplicate primary-key rows in the eight required source tables.

| Source Table | Duplicate Primary-Key Rows |
|---|---:|
| `users` | 0 |
| `prepaid_plans` | 0 |
| `prepaid_transactions` | 0 |
| `load_requests` | 0 |
| `tickets` | 0 |
| `technician_requests` | 0 |
| `troubleshoot_outcomes` | 0 |
| `support_incidents` | 0 |

The primary-key duplicate check therefore passed for the current source baseline.

---

## 6. Noteworthy Source Values

The following observations were identified from the profiling results:

1. `users.status` contained only `active`.
2. `prepaid_plans.status` contained only `active`.
3. `prepaid_transactions.status` contained only `completed`.
4. `load_requests` contained multiple payment and request-status values.
5. `tickets` contained multiple categories and priority levels.
6. `technician_requests.source` was predominantly `demo_seed`.
7. `troubleshoot_outcomes.issue_id` contained several issue types with different frequencies.
8. The `e1-e2-e11` troubleshooting issue occurred only once.
9. `support_incidents` contained only one record during the profiling run.
10. All 19 technician-request descriptions were non-null, although their actual contents were intentionally not displayed.

These are observations from the current source snapshot and should not automatically be interpreted as long-term production distributions.

---

## 7. Data-Quality Concerns

### 7.1 Limited Support-Incident Volume

Only one `support_incidents` record was present during the profiling run. This limits the amount of incident data available for analysis in the current source snapshot.

### 7.2 Demo-Seeding in Technician Requests

Eighteen of the 19 technician-request records had `demo_seed` as their source value. This indicates that the current dataset contains a substantial amount of demonstration or seeded data.

This should be considered when interpreting the dataset as representative operational activity.

### 7.3 Low-Frequency Values

Some source values occur only once, such as:

- `e1-e2-e11` in `troubleshoot_outcomes.issue_id`
- `E1 / E2 / E11` in `troubleshoot_outcomes.issue_label`
- `manual_review` in `load_requests.payment_status`
- `Other` in `tickets.category`

Low-frequency values should not be removed during extraction merely because they occur infrequently.

### 7.4 Nullable Source Fields

The source schema contains nullable fields, including timestamp and relationship-related fields.

These fields require appropriate handling during extraction and validation.

### 7.5 Watermark Consideration

The `prepaid_plans.updated_at` field is nullable. A previous incremental extraction test encountered a NULL watermark condition for this table.

Therefore, nullable timestamp fields must be handled explicitly when used for incremental extraction.

---

## 8. Observed Facts vs. Assumptions

### Observed Facts

The following statements are directly supported by the profiling results:

- The eight required source tables currently contain a combined 478 records.
- No duplicate primary-key rows were observed.
- All 19 technician-request descriptions were non-null.
- `support_incidents` contained one record during profiling.
- Eighteen technician requests had `demo_seed` as their source.
- The listed categorical values and counts were observed during the profiling run.

### Assumptions

The following are treated as assumptions rather than observed source facts:

- The current source distribution represents future production activity.
- Low-frequency values represent rare real-world events.
- `demo_seed` records represent production-like operational activity.
- Current row counts will remain unchanged.

These assumptions should not be used as validation rules unless confirmed by later requirements.

---

## 9. Data Handling and Privacy

The profiling process is designed to summarize source characteristics without exposing raw customer information.

The following are not included in this document:

- Database passwords
- API keys
- Authentication credentials
- Raw customer records
- Actual technician-request descriptions
- Unnecessary personally identifiable information

Only aggregate counts, categories, and structural observations relevant to the extraction process are documented.

---

## 10. Profiling Conclusion

The source value profiling established the current data baseline for the eight required CignalCare+ source tables.

The profiling confirmed:

- 478 total source records across the required tables.
- No duplicate primary-key rows.
- Multiple operational status, category, priority, issue, outcome, and support-mode values.
- 19 non-null technician-request descriptions.
- A single current support-incident record.
- A substantial presence of `demo_seed` technician-request records.
- Several low-frequency source values.
- Nullable fields that require attention during extraction.

These observations provide the data-quality reference for succeeding relationship validation, extraction implementation, and extraction-output validation activities.