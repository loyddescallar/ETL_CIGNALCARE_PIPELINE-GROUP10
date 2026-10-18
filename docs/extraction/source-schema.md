# CignalCare+ Source Schema Profile

## 1. Overview

This document profiles the source database structure used for the CignalCare+ Daily Support and Transaction Analytics Batch Pipeline.

The source database is a Supabase-hosted PostgreSQL operational database using the `public` schema.

The Lab 3 extraction scope consists of eight required source tables:

- `users`
- `prepaid_plans`
- `prepaid_transactions`
- `load_requests`
- `tickets`
- `technician_requests`
- `troubleshoot_outcomes`
- `support_incidents`

The profile focuses on columns and structural details relevant to extraction, validation, relationships, and succeeding ETL stages.

---

## 2. Source Schema Summary

| Source Table | Total Columns | Primary Key | Declared Foreign Keys |
|---|---:|---|---|
| `users` | 31 | `id` | None |
| `prepaid_plans` | 13 | `id` | None |
| `prepaid_transactions` | 14 | `id` | `plan_id`, `user_id` |
| `load_requests` | 27 | `id` | `plan_id`, `user_id` |
| `tickets` | 9 | `id` | `user_id` |
| `technician_requests` | 20 | `id` | `user_id` |
| `troubleshoot_outcomes` | 17 | `id` | None |
| `support_incidents` | 16 | `id` | None |

---

## 3. Table Schema Profiles

### 3.1 `users`

**Primary Key:** `id` (`integer`, NOT NULL)

Important extraction-related columns:

| Column | Data Type | Nullable |
|---|---|---|
| `id` | integer | NO |
| `accountName` | character varying | NO |
| `accountNumber` | character varying | NO |
| `ccaNumber` | character varying | NO |
| `address` | character varying | NO |
| `location` | character varying | NO |
| `role` | character varying | NO |
| `status` | character varying | NO |
| `created_at` | timestamp with time zone | NO |
| `updated_at` | timestamp with time zone | YES |

The table also contains authentication, recovery, verification, and account-management fields. These fields are not reproduced in detail because they are not required for the analytics extraction scope.

**Declared Foreign Keys:** None.

**Relevant Timestamp Fields:**

- `created_at`
- `updated_at`

---

### 3.2 `prepaid_plans`

**Primary Key:** `id` (`integer`, NOT NULL)

Important extraction-related columns:

| Column | Data Type | Nullable |
|---|---|---|
| `id` | integer | NO |
| `plan_code` | character varying | NO |
| `plan_name` | character varying | NO |
| `amount` | numeric | NO |
| `validity_days` | integer | NO |
| `hd_channels` | integer | YES |
| `sd_channels` | integer | YES |
| `status` | character varying | NO |
| `created_at` | timestamp with time zone | NO |
| `updated_at` | timestamp with time zone | YES |

**Declared Foreign Keys:** None.

**Relevant Timestamp Fields:**

- `created_at`
- `updated_at`

**Structural Observation:**

`updated_at` is nullable and therefore requires consideration when used for incremental extraction or watermark handling.

---

### 3.3 `prepaid_transactions`

**Primary Key:** `id` (`integer`, NOT NULL)

Important extraction-related columns:

| Column | Data Type | Nullable |
|---|---|---|
| `id` | integer | NO |
| `reference_no` | character varying | NO |
| `user_id` | integer | YES |
| `account_number` | character varying | NO |
| `account_name` | character varying | NO |
| `plan_id` | integer | NO |
| `amount` | numeric | NO |
| `payment_method` | character varying | NO |
| `transaction_date` | timestamp without time zone | NO |
| `validity_days` | integer | NO |
| `expiry_date` | timestamp without time zone | NO |
| `status` | character varying | NO |
| `created_at` | timestamp with time zone | NO |

**Declared Foreign Keys:**

- `plan_id` → `prepaid_plans.id`
- `user_id` → `users.id`

**Relevant Timestamp Fields:**

- `transaction_date`
- `expiry_date`
- `created_at`

---

### 3.4 `load_requests`

**Primary Key:** `id` (`integer`, NOT NULL)

Important extraction-related columns:

| Column | Data Type | Nullable |
|---|---|---|
| `id` | integer | NO |
| `user_id` | integer | YES |
| `plan_id` | integer | YES |
| `account_number` | character varying | NO |
| `account_name` | character varying | NO |
| `plan_name` | character varying | NO |
| `amount` | numeric | NO |
| `payment_method` | character varying | NO |
| `payment_status` | character varying | NO |
| `reference_no` | character varying | NO |
| `payment_completed_at` | timestamp without time zone | YES |
| `fulfilled_at` | timestamp without time zone | YES |
| `diagnostic_result` | character varying | YES |
| `status` | character varying | NO |
| `location` | character varying | YES |
| `created_at` | timestamp with time zone | NO |
| `updated_at` | timestamp with time zone | YES |

Payment-provider fields such as checkout and payment identifiers exist in the source but are not required for the core extraction schema profile.

**Declared Foreign Keys:**

- `plan_id` → `prepaid_plans.id`
- `user_id` → `users.id`

**Relevant Timestamp Fields:**

- `payment_completed_at`
- `fulfilled_at`
- `created_at`
- `updated_at`

---

### 3.5 `tickets`

**Primary Key:** `id` (`integer`, NOT NULL)

Important extraction-related columns:

| Column | Data Type | Nullable |
|---|---|---|
| `id` | integer | NO |
| `user_id` | integer | NO |
| `category` | character varying | NO |
| `subject` | text | NO |
| `priority` | character varying | NO |
| `status` | character varying | NO |
| `created_at` | timestamp with time zone | NO |
| `updated_at` | timestamp with time zone | YES |
| `incident_id` | character varying | YES |

**Declared Foreign Keys:**

- `user_id` → `users.id`

**Relevant Timestamp Fields:**

- `created_at`
- `updated_at`

**Structural Observation:**

`incident_id` exists as an application-level linkage field, but it is not declared as a database foreign key to `support_incidents`.

---

### 3.6 `technician_requests`

**Primary Key:** `id` (`integer`, NOT NULL)

Important extraction-related columns:

| Column | Data Type | Nullable |
|---|---|---|
| `id` | integer | NO |
| `user_id` | integer | NO |
| `accountNumber` | character varying | NO |
| `issueDescription` | text | NO |
| `preferred_date` | date | YES |
| `preferred_time` | time without time zone | YES |
| `source` | character varying | YES |
| `screen_issue` | character varying | YES |
| `status` | character varying | NO |
| `created_at` | timestamp with time zone | NO |
| `updated_at` | timestamp with time zone | YES |
| `incident_id` | character varying | YES |
| `service_address` | text | YES |
| `latitude` | numeric | YES |
| `longitude` | numeric | YES |

Other contact and administrative fields exist in the source but are not required for the core extraction profile.

**Declared Foreign Keys:**

- `user_id` → `users.id`

**Relevant Date/Timestamp Fields:**

- `preferred_date`
- `preferred_time`
- `created_at`
- `updated_at`

**Structural Observation:**

`incident_id` is present but is not declared as a database foreign key.

---

### 3.7 `troubleshoot_outcomes`

**Primary Key:** `id` (`character varying`, NOT NULL)

Important extraction-related columns:

| Column | Data Type | Nullable |
|---|---|---|
| `id` | character varying | NO |
| `user_id` | integer | NO |
| `account_number` | character varying | YES |
| `location` | character varying | YES |
| `model_id` | character varying | NO |
| `model_name` | character varying | YES |
| `issue_id` | character varying | NO |
| `issue_label` | character varying | NO |
| `outcome` | character varying | NO |
| `created_at` | timestamp without time zone | NO |
| `session_id` | character varying | YES |
| `support_mode` | character varying | NO |
| `is_final` | integer | NO |
| `video_watched` | integer | NO |
| `steps_completed` | integer | NO |
| `total_steps` | integer | NO |
| `last_step_id` | character varying | YES |

**Declared Foreign Keys:** None.

**Relevant Timestamp Field:**

- `created_at`

**Structural Observation:**

`issue_id` is used for support-issue linkage but has no declared database foreign key to `support_incidents`.

---

### 3.8 `support_incidents`

**Primary Key:** `id` (`character varying`, NOT NULL)

Important extraction-related columns:

| Column | Data Type | Nullable |
|---|---|---|
| `id` | character varying | NO |
| `issue_key` | character varying | NO |
| `issue_label` | character varying | NO |
| `location` | character varying | NO |
| `status` | character varying | NO |
| `report_count` | integer | NO |
| `distinct_subscribers` | integer | NO |
| `first_reported_at` | timestamp without time zone | YES |
| `last_reported_at` | timestamp without time zone | YES |
| `confirmed_at` | timestamp without time zone | YES |
| `resolved_at` | timestamp without time zone | YES |
| `dismissed_at` | timestamp without time zone | YES |
| `confirmed_by` | integer | YES |
| `created_at` | timestamp without time zone | NO |
| `updated_at` | timestamp without time zone | YES |

**Declared Foreign Keys:** None.

**Relevant Timestamp Fields:**

- `first_reported_at`
- `last_reported_at`
- `confirmed_at`
- `resolved_at`
- `dismissed_at`
- `created_at`
- `updated_at`

**Structural Observation:**

`confirmed_by` contains a user identifier, but no declared foreign-key relationship to `users.id` exists in the inspected schema.

---

## 4. Declared Foreign-Key Relationships

The following database-level foreign-key relationships were identified:

| Source Table | Source Column | Referenced Table | Referenced Column |
|---|---|---|---|
| `prepaid_transactions` | `plan_id` | `prepaid_plans` | `id` |
| `prepaid_transactions` | `user_id` | `users` | `id` |
| `load_requests` | `plan_id` | `prepaid_plans` | `id` |
| `load_requests` | `user_id` | `users` | `id` |
| `tickets` | `user_id` | `users` | `id` |
| `technician_requests` | `user_id` | `users` | `id` |

No declared foreign keys were identified for:

- `users`
- `prepaid_plans`
- `troubleshoot_outcomes`
- `support_incidents`

Application-level relationships are documented separately in the relationship-validation documentation.

---

## 5. Relevant Timestamp and Date Fields

| Source Table | Relevant Fields |
|---|---|
| `users` | `created_at`, `updated_at` |
| `prepaid_plans` | `created_at`, `updated_at` |
| `prepaid_transactions` | `transaction_date`, `expiry_date`, `created_at` |
| `load_requests` | `payment_completed_at`, `fulfilled_at`, `created_at`, `updated_at` |
| `tickets` | `created_at`, `updated_at` |
| `technician_requests` | `preferred_date`, `preferred_time`, `created_at`, `updated_at` |
| `troubleshoot_outcomes` | `created_at` |
| `support_incidents` | `first_reported_at`, `last_reported_at`, `confirmed_at`, `resolved_at`, `dismissed_at`, `created_at`, `updated_at` |

The source contains both `timestamp with time zone` and `timestamp without time zone` fields. The extraction process must preserve these source types correctly.

---

## 6. Relevant Nullable Fields

Several extraction-relevant fields are nullable, including:

- `users.updated_at`
- `prepaid_plans.updated_at`
- `prepaid_transactions.user_id`
- `load_requests.user_id`
- `load_requests.plan_id`
- `load_requests.payment_completed_at`
- `load_requests.fulfilled_at`
- `load_requests.location`
- `load_requests.updated_at`
- `tickets.updated_at`
- `tickets.incident_id`
- `technician_requests.preferred_date`
- `technician_requests.preferred_time`
- `technician_requests.source`
- `technician_requests.screen_issue`
- `technician_requests.updated_at`
- `technician_requests.incident_id`
- `technician_requests.service_address`
- `technician_requests.latitude`
- `technician_requests.longitude`
- `troubleshoot_outcomes.account_number`
- `troubleshoot_outcomes.location`
- `troubleshoot_outcomes.model_name`
- `troubleshoot_outcomes.session_id`
- `troubleshoot_outcomes.last_step_id`
- `support_incidents.first_reported_at`
- `support_incidents.last_reported_at`
- `support_incidents.confirmed_at`
- `support_incidents.resolved_at`
- `support_incidents.dismissed_at`
- `support_incidents.confirmed_by`
- `support_incidents.notes`
- `support_incidents.updated_at`

Nullable fields must be handled appropriately during extraction and validation.

---

## 7. Structural Characteristics Affecting Extraction

### 7.1 Different Naming Conventions

The source uses different naming conventions for account identifiers, including:

- `accountNumber`
- `account_number`

The extraction stage should preserve the source structure. Standardization can be performed during a succeeding transformation stage.

### 7.2 Nullable Watermark Fields

Some source tables contain nullable `updated_at` fields. These fields cannot automatically be assumed to provide a valid watermark for every source record.

### 7.3 Mixed Timestamp Types

The source contains both timezone-aware and timezone-naive timestamp fields. These differences must be considered during extraction and downstream processing.

### 7.4 Application-Level Relationships

Some relationships are represented by fields such as:

- `incident_id`
- `issue_id`
- `issue_key`
- account identifiers

These relationships are not always enforced through database foreign keys and therefore require separate validation.

### 7.5 Sensitive Fields

The source contains authentication, recovery, payment-provider, and contact-related fields.

Only fields relevant to the extraction and analytics pipeline are included in this schema profile. Sensitive credentials and unnecessary personal information must not be exposed in source-controlled documentation.

---

## 8. Schema Profile Conclusion

The source-schema inspection established the structure of the eight required CignalCare+ source tables.

The profile identifies:

- Required source tables
- Primary keys
- Extraction-relevant columns
- Relevant data types
- Nullable fields
- Timestamp and date fields
- Declared foreign-key relationships
- Structural characteristics affecting extraction

This document provides the structural reference for the succeeding source-value profiling, relationship validation, extraction implementation, and extraction validation activities.