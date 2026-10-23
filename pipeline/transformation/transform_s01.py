"""CignalCare+ Lab 4 - S-01 transformation.

S-01 standardizes troubleshooting model references without overwriting the
original source values. The script is intentionally batch-oriented and does
not connect to the source database.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import re
import unicodedata
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path


RULE_ID = "S-01"
RULE_VERSION = "S-01-v1.0.0"
DEFAULT_PARENT_EXTRACTION_BATCH_ID = "20261018T170820026121Z"

BASE_DIR = Path(__file__).resolve().parents[2]
DEFAULT_INPUT_FILE = (
    BASE_DIR
    / "data"
    / "extracted"
    / "20261018T170820768165Z_troubleshoot_outcomes.csv"
)
DEFAULT_OUTPUT_DIR = BASE_DIR / "data" / "transformed"
DEFAULT_QUARANTINE_DIR = BASE_DIR / "data" / "quarantine" / "transformation"
DEFAULT_STATE_DIR = BASE_DIR / "state"
DEFAULT_LOG_FILE = DEFAULT_STATE_DIR / "transformation_log.csv"
DEFAULT_REPORT_FILE = BASE_DIR / "docs" / "transformation" / "s01-transformation-results.md"

REQUIRED_COLUMNS = [
    "id",
    "user_id",
    "location",
    "model_id",
    "model_name",
    "issue_id",
    "issue_label",
    "outcome",
    "created_at",
    "session_id",
    "support_mode",
    "is_final",
    "video_watched",
    "steps_completed",
    "total_steps",
    "last_step_id",
]

TRANSFORMED_COLUMNS = [
    "standardized_model_name",
    "canonical_model_id",
]

LOG_COLUMNS = [
    "run_id",
    "parent_run_id",
    "batch_id",
    "table_name",
    "input_file",
    "output_file",
    "quarantine_file",
    "batch_window_start",
    "batch_window_end",
    "started_at",
    "finished_at",
    "duration_seconds",
    "status",
    "records_read",
    "records_output",
    "records_rejected",
    "records_modified",
    "rules_applied",
    "validation_status",
    "validation_errors",
    "code_version",
    "input_sha256",
    "output_sha256",
]


# ---------------------------------------------------------------------------
# Utilities
# ---------------------------------------------------------------------------


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def iso_timestamp(value: datetime) -> str:
    return value.isoformat(timespec="milliseconds").replace("+00:00", "Z")


def generate_run_id() -> str:
    return "TRN-" + utc_now().strftime("%Y%m%dT%H%M%S%fZ")


def resolve_path(value: str | None, default: Path) -> Path:
    if not value:
        return default

    path = Path(value).expanduser()
    if not path.is_absolute():
        path = BASE_DIR / path
    return path.resolve()


def relative_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(BASE_DIR.resolve()).as_posix()
    except ValueError:
        return str(path.resolve())


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def normalize_model_name(value: object) -> str:
    """Apply the S-01 text-standardization rule."""
    if value is None:
        return ""

    value = unicodedata.normalize("NFKC", str(value))
    return " ".join(value.strip().split())


def canonical_model_id(standardized_name: str) -> str:
    """Generate a deterministic canonical ID from a standardized model name."""
    normalized = standardized_name.casefold()
    slug = re.sub(r"[^a-z0-9]+", "_", normalized).strip("_")

    if not slug:
        raise ValueError("Model name cannot produce a canonical identifier.")

    return f"model_{slug}"


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    if not path.exists():
        raise FileNotFoundError(f"Input file not found: {path}")

    with path.open("r", newline="", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)
        if reader.fieldnames is None:
            raise ValueError("Input CSV does not contain a header.")

        columns = list(reader.fieldnames)
        rows = list(reader)

    return columns, rows


# ---------------------------------------------------------------------------
# Mapping and transformation
# ---------------------------------------------------------------------------


def build_model_mapping(rows: list[dict[str, str]]) -> dict[str, dict[str, object]]:
    source_ids_by_name: dict[str, set[str]] = defaultdict(set)
    record_counts_by_name: Counter[str] = Counter()

    for row in rows:
        name = normalize_model_name(row.get("model_name", ""))
        if not name:
            continue

        source_ids_by_name[name].add((row.get("model_id") or "").strip())
        record_counts_by_name[name] += 1

    mapping: dict[str, dict[str, object]] = {}
    canonical_to_name: dict[str, str] = {}

    for name in sorted(source_ids_by_name):
        canonical = canonical_model_id(name)

        if canonical in canonical_to_name and canonical_to_name[canonical] != name:
            raise ValueError(
                "Canonical ID collision detected: "
                f"{canonical_to_name[canonical]!r} and {name!r} both produce {canonical!r}."
            )

        canonical_to_name[canonical] = name
        mapping[name] = {
            "canonical_model_id": canonical,
            "source_model_ids": sorted(source_ids_by_name[name]),
            "record_count": record_counts_by_name[name],
        }

    return mapping


def transform_rows(
    rows: list[dict[str, str]],
    mapping: dict[str, dict[str, object]],
    run_id: str,
) -> tuple[list[dict[str, str]], list[dict[str, str]], int]:
    transformed: list[dict[str, str]] = []
    rejected: list[dict[str, str]] = []
    records_modified = 0

    for source_row_number, row in enumerate(rows, start=2):
        standardized_name = normalize_model_name(row.get("model_name", ""))

        if not standardized_name:
            rejected_row = dict(row)
            rejected_row.update(
                {
                    "rejection_rule": RULE_ID,
                    "rejection_reason": (
                        "model_name is blank and a canonical model identifier "
                        "cannot be generated."
                    ),
                    "source_row_number": str(source_row_number),
                    "transformation_run_id": run_id,
                }
            )
            rejected.append(rejected_row)
            continue

        details = mapping.get(standardized_name)
        if details is None:
            raise ValueError(f"Internal mapping error for model name: {standardized_name}")

        output_row = dict(row)
        output_row["standardized_model_name"] = standardized_name
        output_row["canonical_model_id"] = str(details["canonical_model_id"])
        transformed.append(output_row)
        records_modified += 1

    return transformed, rejected, records_modified


# ---------------------------------------------------------------------------
# Output and validation
# ---------------------------------------------------------------------------


def write_csv(path: Path, columns: list[str], rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", newline="", encoding="utf-8-sig") as file:
        writer = csv.DictWriter(file, fieldnames=columns, extrasaction="raise")
        writer.writeheader()
        writer.writerows(rows)


def write_quarantine(path: Path, rows: list[dict[str, str]]) -> Path | None:
    if not rows:
        return None

    path.parent.mkdir(parents=True, exist_ok=True)
    columns = REQUIRED_COLUMNS + [
        "rejection_rule",
        "rejection_reason",
        "source_row_number",
        "transformation_run_id",
    ]
    write_csv(path, columns, rows)
    return path


def validate_transformation(
    input_rows: list[dict[str, str]],
    transformed_rows: list[dict[str, str]],
    rejected_rows: list[dict[str, str]],
    output_columns: list[str],
) -> list[str]:
    errors: list[str] = []

    input_count = len(input_rows)
    output_count = len(transformed_rows)
    rejected_count = len(rejected_rows)

    if input_count != output_count + rejected_count:
        errors.append(
            f"Record reconciliation failed: input={input_count}, "
            f"output={output_count}, rejected={rejected_count}"
        )

    expected_columns = REQUIRED_COLUMNS + TRANSFORMED_COLUMNS
    if output_columns != expected_columns:
        errors.append(
            "Output schema mismatch: expected "
            f"{expected_columns}, received {output_columns}"
        )

    for index, row in enumerate(transformed_rows, start=1):
        for column in expected_columns:
            if column not in row:
                errors.append(f"Output row {index} is missing column {column}.")
                break

        standardized_name = (row.get("standardized_model_name") or "").strip()
        canonical_id = (row.get("canonical_model_id") or "").strip()

        if not standardized_name:
            errors.append(f"Output row {index} has blank standardized_model_name.")
        if not canonical_id:
            errors.append(f"Output row {index} has blank canonical_model_id.")

    # Primary-key uniqueness.
    output_ids = [row.get("id", "") for row in transformed_rows]
    duplicate_ids = [
        value
        for value, count in Counter(output_ids).items()
        if value and count > 1
    ]
    if duplicate_ids:
        errors.append("Duplicate output IDs detected: " + ", ".join(duplicate_ids[:10]))

    # Source-value preservation.
    input_by_id = {
        row["id"]: row
        for row in input_rows
        if row.get("id")
    }
    for row in transformed_rows:
        row_id = row.get("id", "")
        original = input_by_id.get(row_id)
        if original is None:
            errors.append(f"Output record {row_id!r} does not exist in input.")
            continue

        for column in REQUIRED_COLUMNS:
            if row.get(column, "") != original.get(column, ""):
                errors.append(
                    f"Source value changed for id={row_id}, column={column}."
                )

    # One standardized name -> one canonical ID.
    name_to_canonical: dict[str, set[str]] = defaultdict(set)
    canonical_to_name: dict[str, set[str]] = defaultdict(set)

    for row in transformed_rows:
        name = row.get("standardized_model_name", "")
        canonical = row.get("canonical_model_id", "")
        name_to_canonical[name].add(canonical)
        canonical_to_name[canonical].add(name)

    for name, canonical_ids in name_to_canonical.items():
        if len(canonical_ids) != 1:
            errors.append(
                f"Model name {name!r} maps to multiple canonical IDs: "
                + ", ".join(sorted(canonical_ids))
            )

    for canonical, names in canonical_to_name.items():
        if len(names) != 1:
            errors.append(
                f"Canonical ID {canonical!r} maps to multiple model names: "
                + ", ".join(sorted(names))
            )

    # Canonical ID format and deterministic regeneration.
    canonical_pattern = re.compile(r"^model_[a-z0-9]+(?:_[a-z0-9]+)*$")
    for row in transformed_rows:
        canonical = row.get("canonical_model_id", "")
        name = row.get("standardized_model_name", "")

        if not canonical_pattern.fullmatch(canonical):
            errors.append(f"Invalid canonical model ID format: {canonical!r}")

        try:
            expected = canonical_model_id(name)
        except ValueError as exc:
            errors.append(f"Canonicalization failed for {name!r}: {exc}")
            continue

        if expected != canonical:
            errors.append(
                f"Non-deterministic canonical ID for {name!r}: "
                f"expected {expected!r}, received {canonical!r}"
            )

    # Rejected records must contain traceability metadata.
    for index, row in enumerate(rejected_rows, start=1):
        for field in (
            "rejection_rule",
            "rejection_reason",
            "source_row_number",
            "transformation_run_id",
        ):
            if not row.get(field):
                errors.append(f"Rejected row {index} is missing {field}.")

    return errors


def validate_output_file(path: Path, expected_columns: list[str]) -> list[str]:
    """Validate the generated CSV header and readability as a final file-level check."""
    errors: list[str] = []
    try:
        columns, _ = read_csv(path)
    except Exception as exc:  # pragma: no cover - defensive runtime path
        return [f"Unable to read generated output: {type(exc).__name__}: {exc}"]

    if columns != expected_columns:
        errors.append(
            "Generated output header does not match expected output contract."
        )
    return errors


# ---------------------------------------------------------------------------
# Logging and report
# ---------------------------------------------------------------------------


def append_log(path: Path, row: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    exists = path.exists()

    with path.open("a", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=LOG_COLUMNS)
        if not exists:
            writer.writeheader()
        writer.writerow(row)


def write_report(
    path: Path,
    *,
    run_id: str,
    parent_batch_id: str,
    input_path: Path,
    output_path: Path | None,
    quarantine_path: Path | None,
    input_hash: str,
    output_hash: str,
    started: datetime,
    finished: datetime,
    input_rows: list[dict[str, str]],
    transformed_rows: list[dict[str, str]],
    rejected_rows: list[dict[str, str]],
    mapping: dict[str, dict[str, object]],
    validation_errors: list[str],
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    input_count = len(input_rows)
    output_count = len(transformed_rows)
    rejected_count = len(rejected_rows)
    affected_count = sum(
        1 for row in input_rows if (row.get("model_id") or "").startswith("model_")
    )
    affected_pct = (affected_count / input_count * 100) if input_count else 0
    status = "PASS" if not validation_errors else "FAIL"
    duration = (finished - started).total_seconds()

    lines = [
        "# CignalCare+ Lab 4 — S-01 Transformation Results",
        "",
        "## Execution Summary",
        "",
        "| Item | Result |",
        "|---|---|",
        f"| Rule | `{RULE_ID}` |",
        f"| Rule Version | `{RULE_VERSION}` |",
        f"| Run ID | `{run_id}` |",
        f"| Parent Extraction Batch | `{parent_batch_id}` |",
        "| Input Table | `troubleshoot_outcomes` |",
        f"| Input Records | **{input_count}** |",
        f"| Output Records | **{output_count}** |",
        f"| Rejected Records | **{rejected_count}** |",
        f"| Issue-Affected Source Records | **{affected_count} ({affected_pct:.2f}%)** |",
        f"| Distinct Canonical Models | **{len(mapping)}** |",
        f"| Validation | **{status}** |",
        "",
        "## Input Artifact",
        "",
        f"- **Input file:** `{relative_path(input_path)}`",
        f"- **Input SHA-256:** `{input_hash}`",
        "- The input is a validated Lab 3 handover artifact and was not modified.",
        "",
        "## Model Standardization Mapping",
        "",
        "| Standardized Model Name | Canonical Model ID | Source Model IDs | Records |",
        "|---|---|---|---:|",
    ]

    for name in sorted(mapping):
        details = mapping[name]
        source_ids = ", ".join(str(x) for x in details["source_model_ids"])
        lines.append(
            f"| {name} | `{details['canonical_model_id']}` | {source_ids} | "
            f"{details['record_count']} |"
        )

    lines.extend(
        [
            "",
            "## Output Artifact",
            "",
            f"- **Output file:** `{relative_path(output_path) if output_path else 'None'}`",
            f"- **Output SHA-256:** `{output_hash or 'None'}`",
            f"- **Quarantine:** `{relative_path(quarantine_path)}`" if quarantine_path else "- **Quarantine:** None",
            "",
            "## Validation Results",
            "",
            f"- Record reconciliation: **{'PASS' if input_count == output_count + rejected_count else 'FAIL'}** — `{input_count} = {output_count} + {rejected_count}`",
            f"- Source values preserved: **{'PASS' if 'Source value changed' not in ' '.join(validation_errors) else 'FAIL'}**",
            f"- Output ID uniqueness: **{'PASS' if not any('Duplicate output IDs' in e for e in validation_errors) else 'FAIL'}**",
            f"- Model name → canonical ID: **{'PASS' if not any('maps to multiple canonical IDs' in e for e in validation_errors) else 'FAIL'}**",
            f"- Canonical ID → model name: **{'PASS' if not any('maps to multiple model names' in e for e in validation_errors) else 'FAIL'}**",
            f"- Deterministic canonicalization: **{'PASS' if not any('Non-deterministic canonical ID' in e for e in validation_errors) else 'FAIL'}**",
            f"- Generated file/header check: **{'PASS' if not any('Generated output header' in e or 'Unable to read generated output' in e for e in validation_errors) else 'FAIL'}**",
        ]
    )

    if validation_errors:
        lines.extend(["", "### Validation Errors", ""])
        lines.extend(f"- {error}" for error in validation_errors)

    lines.extend(
        [
            "",
            "## Execution Metadata",
            "",
            f"- **Started:** `{iso_timestamp(started)}`",
            f"- **Finished:** `{iso_timestamp(finished)}`",
            f"- **Duration:** `{duration:.3f} seconds`",
            f"- **Status:** `{status}`",
            "",
            "## Acceptance",
            "",
            f"The S-01 run has a rejection rate of **{(rejected_count / input_count * 100) if input_count else 0:.2f}%** and a validation status of **{status}**.",
            "",
        ]
    )

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run CignalCare+ Lab 4 S-01 model standardization."
    )
    parser.add_argument(
        "--input-file",
        default=str(DEFAULT_INPUT_FILE),
        help="Validated Lab 3 CSV input path (relative to repository root or absolute).",
    )
    parser.add_argument(
        "--parent-run-id",
        default=DEFAULT_PARENT_EXTRACTION_BATCH_ID,
        help="Lab 3 extraction batch/run identifier used for lineage.",
    )
    parser.add_argument(
        "--output-file",
        default=None,
        help="Optional output CSV path. Default is a stable S-01 path derived from the parent batch.",
    )
    parser.add_argument(
        "--quarantine-file",
        default=None,
        help="Optional quarantine CSV path. Default is generated per transformation run when needed.",
    )
    parser.add_argument(
        "--run-id",
        default=None,
        help="Optional controlled transformation run ID. Otherwise one is generated.",
    )
    parser.add_argument(
        "--log-file",
        default=str(DEFAULT_LOG_FILE),
        help="Transformation log CSV path.",
    )
    parser.add_argument(
        "--report-file",
        default=str(DEFAULT_REPORT_FILE),
        help="Current S-01 result report path.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    started = utc_now()
    run_id = args.run_id or generate_run_id()
    input_path = resolve_path(args.input_file, DEFAULT_INPUT_FILE)
    log_path = resolve_path(args.log_file, DEFAULT_LOG_FILE)
    report_path = resolve_path(args.report_file, DEFAULT_REPORT_FILE)

    if args.output_file:
        output_path = resolve_path(args.output_file, DEFAULT_OUTPUT_DIR / "S01_troubleshoot_outcomes.csv")
    else:
        output_path = (
            DEFAULT_OUTPUT_DIR
            / f"S01_troubleshoot_outcomes_{args.parent_run_id}.csv"
        )

    if args.quarantine_file:
        quarantine_path = resolve_path(args.quarantine_file, DEFAULT_QUARANTINE_DIR / f"{run_id}_S01_rejected.csv")
    else:
        quarantine_path = DEFAULT_QUARANTINE_DIR / f"{run_id}_S01_rejected.csv"

    input_hash = ""
    output_hash = ""
    source_columns: list[str] = []
    input_rows: list[dict[str, str]] = []
    transformed_rows: list[dict[str, str]] = []
    rejected_rows: list[dict[str, str]] = []
    mapping: dict[str, dict[str, object]] = {}
    validation_errors: list[str] = []
    status = "FAILED"
    actual_quarantine_path: Path | None = None

    print("=" * 78)
    print("CignalCare+ LAB 4 - S-01 TRANSFORMATION")
    print("=" * 78)
    print(f"Rule: {RULE_ID}")
    print(f"Rule version: {RULE_VERSION}")
    print(f"Run ID: {run_id}")
    print(f"Parent extraction batch: {args.parent_run_id}")
    print(f"Input: {input_path}")
    print()

    try:
        source_columns, input_rows = read_csv(input_path)
        input_hash = sha256_file(input_path)

        missing_columns = [column for column in REQUIRED_COLUMNS if column not in source_columns]
        if missing_columns:
            raise ValueError("Missing required columns: " + ", ".join(missing_columns))

        mapping = build_model_mapping(input_rows)
        transformed_rows, rejected_rows, records_modified = transform_rows(
            input_rows,
            mapping,
            run_id,
        )

        output_columns = list(source_columns) + TRANSFORMED_COLUMNS
        write_csv(output_path, output_columns, transformed_rows)
        output_hash = sha256_file(output_path)

        if rejected_rows:
            actual_quarantine_path = write_quarantine(quarantine_path, rejected_rows)

        validation_errors.extend(
            validate_transformation(
                input_rows,
                transformed_rows,
                rejected_rows,
                output_columns,
            )
        )
        validation_errors.extend(
            validate_output_file(output_path, output_columns)
        )

        status = "SUCCESS" if not validation_errors else "FAILED"
        finished = utc_now()

        write_report(
            report_path,
            run_id=run_id,
            parent_batch_id=args.parent_run_id,
            input_path=input_path,
            output_path=output_path,
            quarantine_path=actual_quarantine_path,
            input_hash=input_hash,
            output_hash=output_hash,
            started=started,
            finished=finished,
            input_rows=input_rows,
            transformed_rows=transformed_rows,
            rejected_rows=rejected_rows,
            mapping=mapping,
            validation_errors=validation_errors,
        )

        created_dates = [row.get("created_at", "") for row in input_rows if row.get("created_at", "")]
        batch_window_start = min(created_dates) if created_dates else ""
        batch_window_end = max(created_dates) if created_dates else ""
        duration = (finished - started).total_seconds()

        append_log(
            log_path,
            {
                "run_id": run_id,
                "parent_run_id": args.parent_run_id,
                "batch_id": args.parent_run_id,
                "table_name": "troubleshoot_outcomes",
                "input_file": relative_path(input_path),
                "output_file": relative_path(output_path),
                "quarantine_file": relative_path(actual_quarantine_path) if actual_quarantine_path else "",
                "batch_window_start": batch_window_start,
                "batch_window_end": batch_window_end,
                "started_at": iso_timestamp(started),
                "finished_at": iso_timestamp(finished),
                "duration_seconds": f"{duration:.3f}",
                "status": status,
                "records_read": len(input_rows),
                "records_output": len(transformed_rows),
                "records_rejected": len(rejected_rows),
                "records_modified": records_modified,
                "rules_applied": f"{RULE_ID}:{records_modified}",
                "validation_status": "PASS" if not validation_errors else "FAIL",
                "validation_errors": " | ".join(validation_errors),
                "code_version": RULE_VERSION,
                "input_sha256": input_hash,
                "output_sha256": output_hash,
            },
        )

        print(f"Records read:       {len(input_rows)}")
        print(f"Records output:     {len(transformed_rows)}")
        print(f"Records rejected:   {len(rejected_rows)}")
        print(f"Canonical models:   {len(mapping)}")
        print(f"Validation:         {'PASS' if not validation_errors else 'FAIL'}")
        print(f"Output:             {output_path}")
        print(f"Report:             {report_path}")
        print(f"Log:                {log_path}")

        if validation_errors:
            print("\nValidation errors:")
            for error in validation_errors:
                print(f"- {error}")
            return 1

        print("\nS-01 transformation completed successfully.")
        return 0

    except Exception as error:
        finished = utc_now()
        error_message = f"{type(error).__name__}: {error}"
        validation_errors.append(error_message)

        duration = (finished - started).total_seconds()
        append_log(
            log_path,
            {
                "run_id": run_id,
                "parent_run_id": args.parent_run_id,
                "batch_id": args.parent_run_id,
                "table_name": "troubleshoot_outcomes",
                "input_file": relative_path(input_path),
                "output_file": relative_path(output_path) if output_path else "",
                "quarantine_file": relative_path(actual_quarantine_path) if actual_quarantine_path else "",
                "batch_window_start": "",
                "batch_window_end": "",
                "started_at": iso_timestamp(started),
                "finished_at": iso_timestamp(finished),
                "duration_seconds": f"{duration:.3f}",
                "status": "FAILED",
                "records_read": len(input_rows),
                "records_output": len(transformed_rows),
                "records_rejected": len(rejected_rows),
                "records_modified": len(transformed_rows),
                "rules_applied": "",
                "validation_status": "FAIL",
                "validation_errors": error_message,
                "code_version": RULE_VERSION,
                "input_sha256": input_hash,
                "output_sha256": output_hash,
            },
        )
        print(f"\nS-01 transformation failed: {error_message}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
