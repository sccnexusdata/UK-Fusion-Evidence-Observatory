from __future__ import annotations

import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPOSITORY_ROOT))

from scripts.validate_public_repo import PublicValidationError, ROOT, validate_repository  # noqa: E402


class PublicRepositoryTests(unittest.TestCase):
    def test_supplied_repository_is_valid(self) -> None:
        result = validate_repository()
        self.assertEqual(result["status"], "valid")
        self.assertGreaterEqual(result["record_count"], 1)

    def _copy_data(self, destination: Path) -> None:
        for name in ("evidence.json", "sources.json", "release-manifest.json"):
            shutil.copy2(ROOT / "data/current" / name, destination / name)

    def test_internal_field_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            data_dir = Path(temporary)
            self._copy_data(data_dir)
            evidence_path = data_dir / "evidence.json"
            evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
            evidence["records"][0]["reviewer_notes"] = "must remain private"
            evidence_path.write_text(json.dumps(evidence), encoding="utf-8")
            with self.assertRaises(PublicValidationError):
                validate_repository(data_dir)

    def test_modified_file_without_manifest_update_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            data_dir = Path(temporary)
            self._copy_data(data_dir)
            evidence_path = data_dir / "evidence.json"
            evidence_path.write_bytes(evidence_path.read_bytes() + b"\n")
            with self.assertRaises(PublicValidationError):
                validate_repository(data_dir)


if __name__ == "__main__":
    unittest.main()
