# GitHub Actions Workflows

**For complete release documentation, see [RELEASE.md](../RELEASE.md) in the repository root.**

## PyPI Publishing (`publish.yml`)

Automatically publishes Groqqy to PyPI when a GitHub Release is published.

### Quick Start

**Trigger a release:**
```bash
gh release create vX.Y.Z \
  --title "vX.Y.Z - Description" \
  --notes-file <(sed -n '/## \[X.Y.Z\]/,/## \[/p' CHANGELOG.md | head -n -1)
```

**Monitor workflow:**
```bash
gh run watch
```

**Verify publish:**
```bash
pip install --upgrade groqqy
python -c "import groqqy; print(groqqy.__version__)"
```

### How It Works

1. **You create GitHub Release** (tag like `vX.Y.Z`)
2. **Workflow triggers automatically:**
   - Checks out code at release tag
   - Sets up Python 3.11
   - Installs build tools
   - Builds package (`python -m build`)
   - Publishes to PyPI via Trusted Publishing
3. **Done!** Package available on PyPI in 2-3 minutes

### PyPI Trusted Publishing Setup

**One-time configuration (already done):**

1. Go to: https://pypi.org/manage/account/publishing/
2. Add publisher:
   - **PyPI Project**: `groqqy`
   - **Owner**: `scottsen`
   - **Repository**: `groqqy`
   - **Workflow**: `publish.yml`
   - **Environment**: `pypi`

**Benefits:**
- ✅ No API tokens to manage
- ✅ More secure (OIDC-based)
- ✅ Automatic credential rotation
- ✅ Works only from GitHub Actions

### Workflow Triggers

**Triggers on:**
- ✅ GitHub Release published

**Does NOT trigger on:**
- ❌ Just pushing a tag
- ❌ Draft releases
- ❌ Pre-releases (can enable if needed)
- ❌ Direct commits to main

### Local Testing

Test the build process locally before releasing:

```bash
# Clean previous builds
rm -rf dist/ build/ *.egg-info

# Build package
python -m build

# Verify distribution
twine check dist/*

# Inspect contents
tar -tzf dist/groqqy-X.Y.Z.tar.gz
```

**Optional: Test on TestPyPI first**
```bash
twine upload --repository testpypi dist/*
pip install --index-url https://test.pypi.org/simple/ groqqy
```

### Monitoring & Troubleshooting

**View recent runs:**
```bash
gh run list --limit 10
```

**Watch current run:**
```bash
gh run watch
```

**View failed run logs:**
```bash
gh run list --limit 5
gh run view <run-id> --log-failed
```

**Common issues:**
- **"File already exists"** → Version already on PyPI (can't overwrite)
- **Build fails** → Check Python syntax, dependencies in pyproject.toml
- **Auth fails** → Verify Trusted Publishing configuration

See [RELEASE.md](../RELEASE.md) for detailed troubleshooting.

### Version Management (v2.2.2+)

**Modern approach (pyproject.toml only):**

Update version in 2 places:
1. `pyproject.toml` (line 7): `version = "X.Y.Z"`
2. `groqqy/__init__.py` (line 1): `__version__ = "X.Y.Z"`

**Note:** No setup.py needed (removed in v2.2.2, pyproject.toml is sufficient per PEP 517/518)

### Resources

- **Complete Release Guide**: [RELEASE.md](../RELEASE.md)
- **Workflow File**: `publish.yml`
- **Package on PyPI**: https://pypi.org/project/groqqy/
- **Workflow Runs**: https://github.com/scottsen/groqqy/actions
- **PEP 517** (Build System): https://peps.python.org/pep-0517/
- **PEP 518** (pyproject.toml): https://peps.python.org/pep-0518/
