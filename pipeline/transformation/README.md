# Transformation Pipeline

## Current Rule

`S-01` standardizes troubleshooting model references in `troubleshoot_outcomes`. It derives `canonical_model_id` from `model_name` while preserving the source `model_id` and `model_name`.

## Recommended Future Workflow

1. Receive a validated Lab 3 extraction handover.
2. Place the handover CSVs under `data/extracted/`.
3. Profile the batch before writing a new rule.
4. Document the issue and assign a rule ID/version.
5. Run the transformation with an explicit parent extraction batch ID.
6. Validate the output.
7. Review the log and hashes.
8. Complete acceptance/handover documentation.

## S-01 Usage

From the repository root:

```powershell
python pipeline/transformation/transform_s01.py --input-file data/extracted/20261018T170820768165Z_troubleshoot_outcomes.csv --parent-run-id 20261018T170820026121Z
```

Optional arguments:

- `--output-file` — override the default stable output path.
- `--quarantine-file` — override the quarantine path.
- `--run-id` — supply a controlled run ID; otherwise one is generated.
- `--log-file` — override the transformation log path.
- `--report-file` — override the S-01 result report path.

The default output path is deterministic for the same input dataset and parent batch. This makes repeated runs data-idempotent while still recording a unique run ID in the log.

## Safety Rules

- Do not connect the Transformation Stage directly to the source database.
- Do not modify files under `data/extracted/`.
- Do not commit `.env` or real credentials.
- Do not invent missing business values.
- Do not hand over an output that fails a Critical validation check.
