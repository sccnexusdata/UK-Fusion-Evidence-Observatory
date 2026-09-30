#!/usr/bin/env python3
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "build/github-mirror"

HTML = '''<!doctype html>
<html lang="en-GB">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="description" content="Lightweight GitHub mirror for the SCC Nexus UK Fusion Evidence Observatory.">
<link rel="canonical" href="https://www.sccnexus.co.uk/nuclear_fusion/">
<title>UK Fusion Evidence Observatory · SCC Nexus</title>
<style>
:root{color-scheme:dark;background:#071315;color:#eef8f5;font-family:Inter,system-ui,sans-serif}*{box-sizing:border-box}body{margin:0;min-height:100vh;display:grid;place-items:center;background:radial-gradient(circle at 50% 0,#17413d,#071315 48%)}main{width:min(820px,calc(100% - 36px));padding:56px 0}.eyebrow{text-transform:uppercase;letter-spacing:.14em;color:#8bd3c7;font-size:.76rem}h1{font-size:clamp(2.4rem,7vw,5.2rem);line-height:.98;margin:.2em 0}.lede{font-size:1.15rem;line-height:1.6;color:#bad0ca;max-width:700px}.actions{display:flex;flex-wrap:wrap;gap:12px;margin:28px 0}.button{display:inline-block;padding:12px 16px;border-radius:999px;text-decoration:none;border:1px solid #2b5f58;color:#eafffb}.primary{background:#b9fff2;color:#071315;border-color:#b9fff2}.note{margin-top:38px;padding-top:18px;border-top:1px solid #21433e;color:#829d97;font-size:.92rem}</style>
</head>
<body><main>
<p class="eyebrow">SCC Nexus · Search · Corroborate · Communicate</p>
<h1>UK Fusion Evidence Observatory</h1>
<p class="lede">GitHub is the lightweight transparency mirror. The full public Observatory, evidence explorer and current validated release are published on SCC Nexus.</p>
<div class="actions"><a class="button primary" href="https://www.sccnexus.co.uk/nuclear_fusion/">Open the public Observatory →</a><a class="button" href="https://github.com/sccnexusdata/UK-Fusion-Evidence-Observatory">View repository</a><a class="button" href="https://github.com/sccnexusdata/UK-Fusion-Evidence-Observatory/tree/main/data/current">Current release data</a></div>
<p class="note">This mirror intentionally stays small. Evidence data, validation code and release history remain openly inspectable in the repository; the presentation layer lives at SCC Nexus.</p>
</main></body></html>'''

if TARGET.exists():
    shutil.rmtree(TARGET)
TARGET.mkdir(parents=True)
(TARGET / "index.html").write_text(HTML, encoding="utf-8")
(TARGET / ".nojekyll").write_text("", encoding="utf-8")
print(f"Built GitHub mirror at {TARGET}")
