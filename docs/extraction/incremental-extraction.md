# CignalCare+ Incremental Extraction and Watermark Handling

## 1. Overview

The CignalCare+ extraction process supports incremental extraction to avoid reprocessing the complete source dataset on every pipeline run.

After an initial full extraction, the pipeline stores a watermark for each source table. Subsequent runs use the saved watermark to identify records that are newly created or updated.

---

## 2. Watermark Strategy

The extraction uses the following watermark fields:

| Source Table | Watermark Strategy |
|---|---|
| `users` | `COALESCE(updated_at, created_at)` |
| `prepaid_plans` | `COALESCE(updated_at, created_at)` |
| `prepaid_transactions` | `created_at` |
| `load_requests` | `COALESCE(updated_at, created_at)` |
| `tickets` | `COALESCE(updated_at, created_at)` |
| `technician_requests` | `COALESCE(updated_at, created_at)` |
| `troubleshoot_outcomes` | `created_at` |
| `support_incidents` | `COALESCE(updated_at, created_at)` |

The `COALESCE(updated_at, created_at)` strategy allows tables with nullable update timestamps to use the creation timestamp when an update timestamp is unavailable.

---

## 3. Initial Full Extraction

The first extraction run is performed using:

```powershell
python .\pipeline\extraction\extract_incremental.py --full