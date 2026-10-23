# CignalCare+ Lab 4 — Transformation Documentation Package

This directory is the maintained documentation baseline for Stage 2: Data Transformation.

| File | Purpose |
|---|---|
| `issue-register.md` | Profiling findings, issue decisions, and transformation prioritization |
| `transformation-specification.md` | Sections 1–6: input, profiling, cleaning, standardization, business transformation, and data contract |
| `transformation-validation-and-handover.md` | Sections 7–11: validation, metadata/logs, retention/access, acceptance/handover, and mitigation |
| `s01-transformation-results.md` | Evidence from the completed S-01 run |

## Rule-Versioning Practice

Use a new rule version when the behavior of an existing transformation changes. Preserve historical result reports rather than rewriting them to match later code.

## Future Rule Template

Every new transformation rule should document:

- Rule ID and version.
- Source table and fields.
- Issue that justified the rule.
- Exact transformation logic.
- Source-value preservation requirements.
- Rejection/quarantine behavior.
- Validation criteria and severity.
- Metadata and lineage fields.
- Acceptance and handover result.
