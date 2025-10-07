# Version Management

## Single Source of Truth

All version numbers are now managed from a single file: `_version.py`

```python
__version__ = '1.0.12'
```

All other files (`__init__.py`, `helper_functions.py`, `ysa_signal.py`, `setup.py`, `pyproject.toml`) import the version from this file.

## Automated Release Process

### How it works

1. Update the version in `_version.py`
2. Commit and push to `main` branch
3. GitHub Actions automatically:
   - Detects the version change
   - Runs tests
   - Builds the package
   - Publishes to PyPI
   - Creates a GitHub release with tag

### Setup Requirements

1. **PyPI API Token**: Add `PYPI_API_TOKEN` to GitHub repository secrets
   - Go to: Settings → Secrets and variables → Actions → New repository secret
   - Name: `PYPI_API_TOKEN`
   - Value: Your PyPI API token (create at https://pypi.org/manage/account/token/)

2. **GitHub Token**: Already available by default as `GITHUB_TOKEN`

### Release Workflow

#### Option 1: Automatic (Recommended)
```bash
# Edit _version.py to bump version
echo "__version__ = '1.0.13'" > _version.py

# Commit and push
git add _version.py
git commit -m "Bump version to 1.0.13"
git push origin main

# GitHub Actions will automatically build and publish
```

#### Option 2: Manual using release.sh
```bash
# Run the release script (still works, but now only updates _version.py)
./release.sh
```

## Version Number Locations (READ-ONLY)

These files now **import** the version and should NOT be edited directly:

- `_version.py` ← **EDIT THIS ONE**
- `__init__.py` (imports from `_version.py`)
- `helper_functions.py` (imports from `_version.py`)
- `ysa_signal.py` (imports from `_version.py`)
- `setup.py` (reads from `_version.py`)
- `pyproject.toml` (configured to read from `_version.py`)

## Benefits

- ✅ No more version mismatches
- ✅ Automatic PyPI releases on merge to main
- ✅ Automatic GitHub releases with tags
- ✅ No manual intervention needed
- ✅ Single source of truth for version
