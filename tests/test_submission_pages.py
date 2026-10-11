"""Submission page security and staging checks."""
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

class TestSubmissionPages(unittest.TestCase):
    def test_redacted_pages(self):
        for section in ("research", "business"):
            with self.subTest(section=section):
                path = ROOT / "docs" / section / "index.html"
                text = path.read_text(encoding="utf-8")
                self.assertIn("Publication boundary:", text)
                self.assertIn('name="robots" content="index,follow"', text)
                self.assertIn("nuclear_fusion/" + section + "/", text)
                for forbidden in ("review-ledger.sqlite3", "outputs/phase-2-1", "mailto:", "github_pat_"):
                    self.assertNotIn(forbidden, text)
    def test_assets_and_staging(self):
        subprocess.run([sys.executable, "scripts/build_site.py"], cwd=ROOT, check=True, capture_output=True)
        for relative in ("research/index.html", "business/index.html", "assets/submission.css", "assets/submission.js"):
            self.assertTrue((ROOT / "build" / "site" / relative).is_file(), relative)

if __name__ == "__main__":
    unittest.main()
