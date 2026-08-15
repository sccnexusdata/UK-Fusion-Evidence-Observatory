#!/usr/bin/env python3
"""Independent, dependency-free validator for the public repository."""

from __future__ import annotations

from datetime import date, datetime
import hashlib
import json
from pathlib import Path
import re
import sys
from typing import Any
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/current"
SCHEMA_VERSION = "1.0.0"
PUBLIC_FIELDS = {
    "record_id", "title", "summary", "evidence_type", "geography",
    "published_date", "source_url", "source_publisher", "source_class",
    "licence", "retrieved_at", "verification_status",
    "corroborating_sources", "confidence_class", "limitations",
}
RECORD_ID = re.compile(r"^EVD-[0-9]{6}$")
SENSITIVE_KEY = re.compile(
    r"(^|_)(password|passwd|secret|token|api_key|private_key|reviewer_notes|internal_notes)($|_)",
    re.IGNORECASE,
)


class PublicValidationError(ValueError):
    pass


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise PublicValidationError(f"Cannot read {path.relative_to(ROOT)}: {exc}") from exc


def require_date(value: Any, label: str) -> None:
    if not isinstance(value, str):
        raise PublicValidationError(f"{label} must be a date string")
    try:
        date.fromisoformat(value)
    except ValueError as exc:
        raise PublicValidationError(f"{label} must use YYYY-MM-DD") from exc


def require_timestamp(value: Any, label: str) -> None:
    if not isinstance(value, str) or not value.endswith("Z"):
        raise PublicValidationError(f"{label} must be a UTC timestamp ending in Z")
    try:
        datetime.fromisoformat(value[:-1] + "+00:00")
    except ValueError as exc:
        raise PublicValidationError(f"{label} is not a valid ISO 8601 timestamp") from exc


def require_https(value: Any, label: str) -> None:
    if not isinstance(value, str):
        raise PublicValidationError(f"{label} must be text")
    parsed = urlparse(value)
    if parsed.scheme != "https" or not parsed.netloc:
        raise PublicValidationError(f"{label} must use HTTPS and include a host")


def scan_sensitive_keys(value: Any, path: str = "$") -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            if SENSITIVE_KEY.search(str(key)):
                raise PublicValidationError(f"Sensitive or internal field at {path}.{key}")
            scan_sensitive_keys(child, f"{path}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            scan_sensitive_keys(child, f"{path}[{index}]")


def validate_record(record: Any) -> None:
    if not isinstance(record, dict):
        raise PublicValidationError("Every evidence record must be an object")
    missing = sorted(PUBLIC_FIELDS - set(record))
    extra = sorted(set(record) - PUBLIC_FIELDS)
    label = record.get("record_id", "<unknown>")
    if missing:
        raise PublicValidationError(f"{label}: missing fields: {', '.join(missing)}")
    if extra:
        raise PublicValidationError(f"{label}: non-public fields: {', '.join(extra)}")
    if not isinstance(label, str) or not RECORD_ID.fullmatch(label):
        raise PublicValidationError(f"{label}: invalid record identifier")
    for field, minimum in (("title", 5), ("summary", 20), ("evidence_type", 3), ("geography", 2)):
        if not isinstance(record[field], str) or len(record[field].strip()) < minimum:
            raise PublicValidationError(f"{label}: invalid {field}")
    require_date(record["published_date"], f"{label}.published_date")
    require_date(record["retrieved_at"], f"{label}.retrieved_at")
    require_https(record["source_url"], f"{label}.source_url")
    if record["verification_status"] not in {"source-verified", "corroborated"}:
        raise PublicValidationError(f"{label}: invalid verification_status")
    if record["confidence_class"] not in {"high", "moderate", "low"}:
        raise PublicValidationError(f"{label}: invalid confidence_class")
    if not isinstance(record["corroborating_sources"], list):
        raise PublicValidationError(f"{label}: corroborating_sources must be a list")
    for position, url in enumerate(record["corroborating_sources"]):
        require_https(url, f"{label}.corroborating_sources[{position}]")
    limitations = record["limitations"]
    if not isinstance(limitations, list) or not limitations:
        raise PublicValidationError(f"{label}: at least one limitation is required")
    if any(not isinstance(item, str) or len(item.strip()) < 8 for item in limitations):
        raise PublicValidationError(f"{label}: invalid limitation")
    scan_sensitive_keys(record)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate_repository(data_dir: Path = DATA) -> dict[str, Any]:
    evidence_path = data_dir / "evidence.json"
    sources_path = data_dir / "sources.json"
    manifest_path = data_dir / "release-manifest.json"
    evidence = load_json(evidence_path)
    sources = load_json(sources_path)
    manifest = load_json(manifest_path)

    for name, document in (("evidence", evidence), ("sources", sources), ("manifest", manifest)):
        if not isinstance(document, dict) or document.get("schema_version") != SCHEMA_VERSION:
            raise PublicValidationError(f"{name}: schema_version must be {SCHEMA_VERSION}")
        require_timestamp(document.get("generated_at"), f"{name}.generated_at")
    if len({evidence["generated_at"], sources["generated_at"], manifest["generated_at"]}) != 1:
        raise PublicValidationError("Generation timestamps do not agree")

    records = evidence.get("records")
    if not isinstance(records, list):
        raise PublicValidationError("evidence.records must be a list")
    seen: set[str] = set()
    for record in records:
        validate_record(record)
        if record["record_id"] in seen:
            raise PublicValidationError(f"Duplicate record_id: {record['record_id']}")
        seen.add(record["record_id"])
    if manifest.get("record_count") != len(records):
        raise PublicValidationError("Manifest record_count does not match evidence.json")

    source_list = sources.get("sources")
    if not isinstance(source_list, list):
        raise PublicValidationError("sources.sources must be a list")
    source_urls = set()
    for source in source_list:
        if not isinstance(source, dict):
            raise PublicValidationError("Every source must be an object")
        require_https(source.get("source_url"), "sources.source_url")
        require_date(source.get("retrieved_at"), "sources.retrieved_at")
        source_urls.add(source["source_url"])
    missing_sources = sorted({record["source_url"] for record in records} - source_urls)
    if missing_sources:
        raise PublicValidationError(f"Source register is missing {len(missing_sources)} evidence source(s)")

    expected_files = {"evidence.json": evidence_path, "sources.json": sources_path}
    files = manifest.get("files")
    if not isinstance(files, dict) or set(files) != set(expected_files):
        raise PublicValidationError("Manifest must list exactly evidence.json and sources.json")
    for name, path in expected_files.items():
        expected_hash = files[name].get("sha256") if isinstance(files[name], dict) else None
        if expected_hash != sha256(path):
            raise PublicValidationError(f"SHA-256 mismatch for {name}")

    scan_sensitive_keys(evidence)
    scan_sensitive_keys(sources)
    return {"status": "valid", "record_count": len(records), "source_count": len(source_list)}


def main() -> int:
    try:
        result = validate_repository()
    except PublicValidationError as exc:
        print(f"PUBLIC VALIDATION FAILED: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
