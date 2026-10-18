# CignalCare+ Relationship and Linkage Validation

## 1. Overview

This document summarizes the relationship and linkage validation performed on the CignalCare+ source datasets. The validation focused on determining whether related records can be connected using reference numbers, account information, issue identifiers, and other available relationship fields.

The results provide a baseline for determining which relationships can be reliably used during succeeding ETL stages.

No source records were modified, and no raw customer information or credentials were displayed.

---

## 2. Prepaid Transaction ↔ Load Request Linkage

The `prepaid_transactions` and `load_requests` tables were compared using their reference numbers.

| Metric | Result |
|---|---:|
| Prepaid transactions | 110 |
| Load requests | 58 |
| Shared reference numbers | 45 |
| Transaction-reference coverage | 40.91% |
| Load-request-reference coverage | 77.59% |

The 45 shared references were further checked for consistency.

| Match Check | Matching Rows |
|---|---:|
| Same account | 45 |
| Same plan | 45 |
| Same amount | 45 |
| Same payment method | 45 |
| Same account + amount | 45 |

All 45 matched references had consistent account, plan, amount, and payment-method values.

### Reference Cardinality

| Cardinality Result | Count |
|---|---:|
| One transaction ↔ one load request | 45 |
| References requiring review | 0 |

The results indicate that the shared reference numbers provide a consistent linkage between the currently matched prepaid transactions and load requests.

---

## 3. Troubleshoot Outcome ↔ Support Incident Linkage

The `troubleshoot_outcomes.issue_id` field was compared with `support_incidents.issue_key`.

| Metric | Result |
|---|---:|
| Total troubleshoot outcomes | 138 |
| Matched issue IDs | 30 |
| Issue IDs without current incident match | 108 |
| Incident linkage coverage | 21.74% |

Only one distinct troubleshoot issue ID and one support incident were represented among the matched records.

This indicates that the current source provides only partial linkage between troubleshooting outcomes and support incidents.

---

## 4. Issue Label Consistency

The issue labels of the matched troubleshoot and support-incident records were compared.

| Metric | Result |
|---|---:|
| Matched rows with same issue label | 30 |
| Matched rows checked | 30 |
| Issue-label consistency | 100.00% |

All 30 matched records had consistent issue labels, supporting the reliability of the current issue-based linkage for the records that successfully matched.

---

## 5. Incident Location Consistency

Location values were compared for the matched troubleshoot and support-incident records.

| Metric | Result |
|---|---:|
| Matched rows with same location | 5 |
| Comparable locations | 30 |
| Location consistency | 16.67% |

The low location consistency indicates that location values should not currently be treated as an exact linkage key without additional normalization or business rules.

---

## 6. Key Findings

- The transaction-to-load-request relationship has **45 shared reference numbers**.
- All 45 matched references had consistent account, plan, amount, and payment-method values.
- No shared references required cardinality review.
- **30 of 138 troubleshoot outcomes** currently have a matching support incident.
- Issue-label consistency for matched records is **100.00%**.
- Location consistency is considerably lower at **16.67%**.
- The current support-incident data provides limited coverage for troubleshooting records.

---

## 7. Linkage Limitations

The validation identified several limitations that must be considered during ETL development:

1. Not all prepaid transactions have a corresponding load request reference.
2. Not all load requests have a corresponding prepaid transaction reference.
3. Most troubleshoot issue IDs currently have no matching support incident.
4. Location values are not sufficiently consistent for exact matching.
5. Application-level linkage fields should be validated carefully before being used for joins.

These limitations do not prevent extraction, but they should be considered when designing transformation and validation rules.

---

## 8. Conclusion

The relationship validation confirms that several source relationships can be used for reliable linkage, particularly the shared reference numbers between prepaid transactions and load requests.

The troubleshoot-to-support-incident relationship is usable for the currently matched records but has limited coverage. Issue labels are fully consistent among matched records, while location values require additional consideration.

These findings establish the relationship and linkage baseline for the succeeding ETL extraction and validation stages.