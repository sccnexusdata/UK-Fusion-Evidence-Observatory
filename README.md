# UK Fusion Evidence Observatory

An independent, evidence-led record of UK fusion science, programme delivery, industry, funding and environmental evidence.

This is the **public** repository. It accepts only validated publication bundles produced by the private `UK-Fusion-Evidence-Engine` and independently checks them before deployment.

## Scope and limitations

The observatory distinguishes:

- an announcement from an achieved milestone;
- plasma gain from facility gain and exported electricity;
- a prototype target from commercial operation;
- public funding announced from expenditure evidenced in contracts;
- attributed claims from independently corroborated results.

It is not affiliated with UKAEA, UK Fusion Energy, STEP or a commercial fusion company. Inclusion is not endorsement. The sample release proves the publication mechanism and is not yet a comprehensive UK fusion dataset.

## Exact repository naming

| Repository | Visibility |
|---|---|
| `UK-Fusion-Evidence-Engine` | Private |
| `UK-Fusion-Evidence-Observatory` | Public |

Recommended GitHub location:

```text
https://github.com/sccnexusdata/UK-Fusion-Evidence-Observatory
```

Do not add a year, `main`, `public`, `v2` or `final` to the repository name.

## Installation and local validation

Python 3.11 or newer is required. The validator and website builder use only the Python standard library.

### Windows PowerShell

```powershell
git clone https://github.com/sccnexusdata/UK-Fusion-Evidence-Observatory.git
Set-Location UK-Fusion-Evidence-Observatory
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python scripts/validate_public_repo.py
python -m unittest discover -s tests -v
python scripts/build_site.py
python -m http.server 8000 --directory build/site
```

Open `http://localhost:8000` and stop the server with `Ctrl+C`.

### macOS or Linux

```bash
git clone https://github.com/sccnexusdata/UK-Fusion-Evidence-Observatory.git
cd UK-Fusion-Evidence-Observatory
python3 -m venv .venv
. .venv/bin/activate
python scripts/validate_public_repo.py
python -m unittest discover -s tests -v
python scripts/build_site.py
python -m http.server 8000 --directory build/site
```

## First GitHub upload

1. Create a new **public** repository named exactly `UK-Fusion-Evidence-Observatory`.
2. Do not initialise it with a README or licence because both are supplied here.
3. Upload the contents of this folder, preserving `.github` and all subfolders.
4. Commit to `main`.
5. Open **Settings → Pages** and choose **GitHub Actions** as the source.
6. Open **Actions → Validate and deploy public observatory → Run workflow**.
7. Protect `main` and require the `validate-public-repository` check for future pull requests.

No secrets or repository variables are required for the supplied release.

## Updating public evidence

1. Build a bundle in the private engine.
2. Create a branch such as `data/2026-08-release` in this repository.
3. Replace only these files in `data/current/`:

   - `evidence.json`
   - `sources.json`
   - `release-manifest.json`

4. Run `python scripts/validate_public_repo.py`.
5. Open a pull request.
6. Merge only after validation and human review pass.

The public validator checks the allow-list, identifiers, dates, HTTPS sources, limitations, duplicate records, sensitive field names, source-register consistency, record count and SHA-256 hashes.

## Naming conventions

- Repository: exactly `UK-Fusion-Evidence-Observatory`.
- Default branch: `main`.
- Data branches: `data/<short-description>`.
- Documentation branches: `docs/<short-description>`.
- Evidence files: `lowercase-kebab-case.json`.
- Evidence IDs: `EVD-NNNNNN` such as `EVD-000001`.
- Release tags: calendar versions such as `2026.08.0`.
- Dates: `YYYY-MM-DD`; timestamps: UTC ending in `Z`.
- Current files never contain a date in the filename; archived snapshots may.
- GitHub variables and secrets, if later needed, begin `FUSION_`.

Never use a mutable organisation name or URL as a record identifier.

## Repository structure

```text
data/current/                 Validated evidence and release manifest
data/schemas/                 Public JSON Schema
docs/                         Static, accessible public website
scripts/validate_public_repo.py Independent publication validator
scripts/build_site.py         Deterministic website staging
tests/                        Regression and security tests
.github/workflows/            Validation and GitHub Pages deployment
```

## Corrections

Open an evidence-correction issue containing the record ID, disputed field, supporting primary source and requested change. Do not include private correspondence or personal data. A corrected data release should supersede rather than silently conceal a material change.

## Licence

The repository software is MIT licensed. Original narrative content may be reused with attribution. Each evidence source retains its own copyright and reuse terms; the `licence` field describes the source classification and does not transfer ownership.
