#!/usr/bin/env python3
"""Stage the static website and validated data for GitHub Pages."""

from __future__ import annotations

from pathlib import Path
import shutil

from validate_public_repo import ROOT, validate_repository


def build_site() -> Path:
    validate_repository()
    target = ROOT / "build/site"
    if target.exists():
        shutil.rmtree(target)
    shutil.copytree(ROOT / "docs", target)
    data_target = target / "data/current"
    data_target.mkdir(parents=True)
    for name in ("evidence.json", "sources.json", "release-manifest.json"):
        shutil.copy2(ROOT / "data/current" / name, data_target / name)
    (target / ".nojekyll").write_text("", encoding="utf-8")
    return target


if __name__ == "__main__":
    destination = build_site()
    print(f"Built validated site at {destination}")
