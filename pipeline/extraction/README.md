# CignalCare+ Source Extraction

## Purpose

This module performs controlled source extraction from the CignalCare+ PostgreSQL/Supabase database for Lab 3.

The extraction process supports full extraction and incremental extraction using saved watermarks.

## Required Source Tables

The extraction process includes:

- `users`
- `prepaid_plans`
- `prepaid_transactions`
- `load_requests`
- `tickets`
- `technician_requests`
- `troubleshoot_outcomes`
- `support_incidents`

## Configuration

Database credentials are loaded through environment variables.

Create a local `.env` file in the repository root:

```text
DATABASE_URL=your_database_connection_string
DB_SSLMODE=require