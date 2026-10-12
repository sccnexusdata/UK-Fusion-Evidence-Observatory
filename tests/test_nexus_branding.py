"""Corporate branding, navigation and release-access checks for the SCC Fusion publication."""
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BRANDED = (
    "index.html",
    "explore.html",
    "methodology.html",
    "limitations.html",
    "research/index.html",
    "business/index.html",
)

class NexusBrandTests(unittest.TestCase):
    def test_branded_pages_and_publication_separation(self):
        for name in BRANDED:
            with self.subTest(page=name):
                page=(ROOT / "docs" / name).read_text(encoding="utf-8")
                self.assertIn("SCC Nexus",page)
                self.assertIn('nexus',page.lower())
                self.assertNotIn("PRIVATE KEY",page)
                self.assertNotIn("review-ledger.sqlite3",page)
                self.assertNotIn('href="protected/"',page)
    def test_homepage_public_release_dom_hooks(self):
        home=(ROOT / "docs/index.html").read_text(encoding="utf-8")
        for anchor in ('id="metric-records"','id="metric-sources"','id="metric-integrity"','id="metric-date"','id="release-status"','id="evidence-list"','id="evidence-search"'):
            self.assertIn(anchor,home)
        self.assertIn('assets/app.js',home)
        self.assertIn('assets/fusion-home.css',home)
        self.assertNotIn("UK Fusion Evidence Observatory · Evidence before conclusion",home)
    def test_brand_assets_are_staged(self):
        subprocess.run([sys.executable,"scripts/build_site.py"],cwd=ROOT,check=True,capture_output=True)
        for name in ("index.html","favicon.svg","assets/fusion-home.css","assets/fusion-cross.css","research/index.html","business/index.html"):
            self.assertTrue((ROOT/"build/site"/name).is_file(),name)
    def test_legacy_navigation_not_duplicated(self):
        for name in ("explore.html","methodology.html","limitations.html"):
            text=(ROOT/"docs"/name).read_text(encoding="utf-8")
            self.assertEqual(text.count(">Academic &amp; science</a>"),1)
            self.assertEqual(text.count(">Business</a>"),1)

if __name__=="__main__":
    unittest.main()
