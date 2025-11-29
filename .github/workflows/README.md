# GitHub Actions Workflows

## PyPI Publishing (`publish.yml`)

Automatically publishes to PyPI when a new GitHub release is created.

### Setup: PyPI Trusted Publishing (Recommended)

**Secure, no tokens needed!**

1. **Go to PyPI**: https://pypi.org/manage/account/publishing/
2. **Add a new publisher**:
   - PyPI Project Name: `groqqy`
   - Owner: `scottsen`
   - Repository: `groqqy`
   - Workflow name: `publish.yml`
   - Environment name: `pypi`
3. **Save**

That's it! Next release will auto-publish.

### Alternative: API Token Method

If you prefer using a token instead:

1. **Generate PyPI API token**: https://pypi.org/manage/account/token/
2. **Add to GitHub Secrets**:
   - Go to: https://github.com/scottsen/groqqy/settings/secrets/actions
   - Name: `PYPI_API_TOKEN`
   - Value: `pypi-...` (your token)
3. **Update workflow**: Change the publish step to:
   ```yaml
   - name: Publish to PyPI
     uses: pypa/gh-action-pypi-publish@release/v1
     with:
       password: ${{ secrets.PYPI_API_TOKEN }}
   ```

### How It Works

1. Create a new release on GitHub (tag like `v2.0.1`)
2. Workflow automatically:
   - Checks out code
   - Sets up Python
   - Builds package (`python -m build`)
   - Publishes to PyPI
3. Done! Users can `pip install groqqy`

### Testing

To test without publishing:

```bash
# Build locally to verify
python -m build

# Check distribution
twine check dist/*

# Test upload to TestPyPI first (optional)
twine upload --repository testpypi dist/*
```

### Workflow Triggers

- ✅ **Release published** - Main trigger
- ❌ Draft releases - Not triggered
- ❌ Pre-releases - Not triggered (can enable if needed)

To publish:
```bash
gh release create v2.0.1 --title "v2.0.1 - Bug fixes" --notes "..."
```

Workflow runs automatically, package appears on PyPI within 2-3 minutes.
