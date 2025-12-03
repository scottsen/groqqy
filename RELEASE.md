# Release Process

Complete guide for releasing new versions of Groqqy.

## Quick Reference

```bash
# 1. Prepare
python run_unit_tests.py              # All tests pass
reveal groqqy/*.py --check            # No issues

# 2. Version & Document
# Update: pyproject.toml, groqqy/__init__.py, CHANGELOG.md

# 3. Commit & Tag
git add pyproject.toml groqqy/__init__.py CHANGELOG.md [other files]
git commit -m "feat(vX.Y.Z): description"
git tag -a vX.Y.Z -m "Version X.Y.Z - description"

# 4. Push (requires explicit approval)
git push origin main
git push origin vX.Y.Z

# 5. Create Release (triggers PyPI publish)
gh release create vX.Y.Z \
  --title "vX.Y.Z - Short description" \
  --notes-file <(sed -n '/## \[X.Y.Z\]/,/## \[/p' CHANGELOG.md | head -n -1)

# 6. Verify
gh run watch                          # Monitor workflow
pip install --upgrade groqqy          # Test install
```

## Detailed Process

### Phase 1: Prepare (Local Validation)

**Run quality checks:**

```bash
# 1. Run all tests
python run_unit_tests.py
# Expect: 20/20 tests passing (or current count)

# 2. Check code quality on modified files
reveal groqqy/bot.py --check
reveal groqqy/agent.py --check
# Expect: No critical issues (warnings OK)

# 3. Test build process
python -m build
twine check dist/*
# Expect: No errors, clean build
```

**Verify version locations:**
- `pyproject.toml` - line 7: `version = "X.Y.Z"`
- `groqqy/__init__.py` - line 1: `__version__ = "X.Y.Z"`
- `CHANGELOG.md` - top entry: `## [X.Y.Z] - YYYY-MM-DD`

**Note:** There is NO setup.py (removed in v2.2.2 - pyproject.toml is sufficient)

### Phase 2: Version Management

**Semantic Versioning (semver.org):**

- **MAJOR** (X.0.0) - Breaking changes, incompatible API
- **MINOR** (x.Y.0) - New features, backwards compatible
- **PATCH** (x.y.Z) - Bug fixes, backwards compatible

**Examples:**
- Add `--no-tools` flag → MINOR (2.2.0)
- Fix security issue → PATCH (2.2.1)
- Remove deprecated API → MAJOR (3.0.0)

**Update version in 2 places:**

1. **pyproject.toml:**
   ```toml
   [project]
   version = "X.Y.Z"
   ```

2. **groqqy/__init__.py:**
   ```python
   __version__ = "X.Y.Z"
   ```

**Update CHANGELOG.md:**

Follow [Keep a Changelog](https://keepachangelog.com/) format:

```markdown
## [X.Y.Z] - YYYY-MM-DD

### Added
- New features

### Changed
- Changes to existing functionality

### Fixed
- Bug fixes

### Security
- Security improvements
```

### Phase 3: Commit & Tag

**Commit message format:**

```bash
git commit -m "feat(vX.Y.Z): brief description

Longer description of changes:
- Key improvement 1
- Key improvement 2
- Key improvement 3

Security fixes, new features, etc.
"
```

**Tag format:**

```bash
git tag -a vX.Y.Z -m "$(cat <<'EOF'
Groqqy vX.Y.Z - Release Title

Brief description of release focus.

Highlights:
- Major feature or fix 1
- Major feature or fix 2
- Major feature or fix 3

See CHANGELOG.md for complete details.
EOF
)"
```

**Verify locally:**

```bash
git log --oneline -3        # Check commit
git tag -l "v*" | tail -5   # Check tag
git show vX.Y.Z             # View tag details
```

### Phase 4: Push to GitHub

**🚨 CRITICAL: This step requires explicit approval!**

Push makes changes public and starts the release process:

```bash
# Push main branch
git push origin main

# Push tag
git push origin vX.Y.Z
```

**Verify push:**

```bash
git log origin/main --oneline -3
git ls-remote --tags origin | grep vX.Y.Z
```

**Wait 30 seconds** before creating release (GitHub stabilization).

### Phase 5: Create GitHub Release

**This triggers automatic PyPI publishing!**

**Option A: With CHANGELOG excerpt (recommended):**

```bash
gh release create vX.Y.Z \
  --title "vX.Y.Z - Release Title" \
  --notes-file <(sed -n '/## \[X.Y.Z\]/,/## \[/p' CHANGELOG.md | head -n -1)
```

**Option B: Manual notes:**

```bash
gh release create vX.Y.Z \
  --title "vX.Y.Z - Release Title" \
  --notes "See CHANGELOG.md for details"
```

**Option C: Interactive (opens editor):**

```bash
gh release create vX.Y.Z --title "vX.Y.Z - Release Title"
# Opens editor for release notes
```

**What happens next:**
1. GitHub Actions workflow triggers (`.github/workflows/publish.yml`)
2. Builds package using `python -m build`
3. Publishes to PyPI via Trusted Publishing (no tokens needed)
4. Package available on PyPI within 2-3 minutes

### Phase 6: Monitor & Verify

**Watch workflow:**

```bash
gh run watch
# Shows real-time workflow progress
```

**Check workflow status:**

```bash
gh run list --limit 5
# Should show "Publish to PyPI" with status "completed" and conclusion "success"
```

**Verify PyPI:**

1. **Check package page:** https://pypi.org/project/groqqy/
2. **Test installation:**
   ```bash
   pip install --upgrade groqqy
   python -c "import groqqy; print(groqqy.__version__)"
   # Should output: X.Y.Z
   ```

3. **Quick smoke test:**
   ```bash
   groqqy --help
   # Should show current version
   ```

## Rollback Procedures

### If workflow fails during publish:

**Investigate:**
```bash
gh run list --limit 5
gh run view <run-id> --log-failed
```

**Common issues:**
- Build failure → Fix locally, delete tag, re-release
- PyPI auth failure → Check Trusted Publishing config
- Version conflict → Version already exists on PyPI (can't overwrite!)

### If bad version published to PyPI:

**⚠️ CANNOT delete or overwrite PyPI versions!**

**Options:**
1. **Yank the release** (makes it non-installable by default):
   ```bash
   # Requires PyPI account access
   pip install twine
   twine upload --skip-existing dist/*  # Won't help if already there

   # Or via PyPI web interface:
   # https://pypi.org/manage/project/groqqy/releases/
   # Click release → "Options" → "Delete release" or "Yank release"
   ```

2. **Publish hotfix** (recommended):
   ```bash
   # Bump to next patch version
   # X.Y.Z → X.Y.(Z+1)
   # Fix issue, follow full release process
   ```

### If tag pushed but no release created:

**Delete remote tag:**
```bash
git push --delete origin vX.Y.Z
```

**Delete local tag:**
```bash
git tag -d vX.Y.Z
```

**Fix issues and re-tag:**
```bash
# Fix whatever needs fixing
git add .
git commit --amend  # or new commit
git tag -a vX.Y.Z -m "..."
git push origin main
git push origin vX.Y.Z
```

## Troubleshooting

### Workflow not triggering

**Check:**
1. Is it a GitHub Release or just a tag?
   - Workflow triggers on `release: types: [published]`
   - Just pushing a tag won't trigger it

2. Is the release a draft?
   - Draft releases don't trigger workflows
   - Publish the release

3. Check workflow file:
   ```bash
   cat .github/workflows/publish.yml
   ```

### Version conflict on PyPI

**Error:** "File already exists on PyPI"

**Cause:** Version X.Y.Z already published (PyPI versions are immutable)

**Solution:**
1. Bump to next version (X.Y.Z+1)
2. Update pyproject.toml and __init__.py
3. Commit and create new release

### Build fails locally

**Test build:**
```bash
rm -rf dist/ build/ *.egg-info
python -m build
```

**Common issues:**
- Missing dependencies → Check pyproject.toml `[build-system]`
- Syntax errors → Run tests first
- File permission issues → Check .gitignore

### Tests fail

**Debug:**
```bash
python run_unit_tests.py
# Check which test failed

# Run specific test:
python -m pytest tests/unit/test_optional_type.py -v
```

**Don't release with failing tests!**

## Version History

**Version management evolution:**

- **v0.x-v2.2.1:** Used setup.py + pyproject.toml (redundant)
- **v2.2.2+:** Modern pyproject.toml only (PEP 517/518)

**Single source of truth:**
- Primary: `pyproject.toml` (line 7)
- Secondary: `groqqy/__init__.py` (for runtime version checks)
- Documented: `CHANGELOG.md` (human-readable)

## Automation Details

### GitHub Actions Workflow

**File:** `.github/workflows/publish.yml`

**Trigger:** GitHub Release published (not draft, not pre-release)

**Steps:**
1. Checkout code at release tag
2. Set up Python 3.11
3. Install build tools (`pip install build`)
4. Build package (`python -m build`)
5. Publish to PyPI via Trusted Publishing

**No secrets required!** Uses PyPI Trusted Publishing (OIDC).

### PyPI Trusted Publishing

**Setup (one-time):**

1. Go to: https://pypi.org/manage/account/publishing/
2. Add publisher:
   - PyPI Project: `groqqy`
   - Owner: `scottsen`
   - Repository: `groqqy`
   - Workflow: `publish.yml`
   - Environment: `pypi`

**Benefits:**
- No API tokens to manage
- More secure (OIDC-based)
- Automatic rotation
- Works only from GitHub Actions

## Best Practices

### Before releasing:

- ✅ All tests pass
- ✅ Code quality checks pass
- ✅ CHANGELOG.md updated
- ✅ Version bumped in 2 places
- ✅ Commit message is descriptive
- ✅ Tag message is clear

### During release:

- ✅ Push main before tag
- ✅ Wait for push to stabilize (30s)
- ✅ Create release with good notes
- ✅ Monitor workflow

### After release:

- ✅ Verify workflow succeeded
- ✅ Check PyPI package page
- ✅ Test installation
- ✅ Update documentation if needed

### Don't:

- ❌ Rush releases without testing
- ❌ Skip CHANGELOG updates
- ❌ Reuse version numbers
- ❌ Publish with known bugs
- ❌ Forget to push before creating release

## Resources

- **GitHub Releases:** https://github.com/scottsen/groqqy/releases
- **PyPI Package:** https://pypi.org/project/groqqy/
- **Workflow Runs:** https://github.com/scottsen/groqqy/actions
- **Semantic Versioning:** https://semver.org/
- **Keep a Changelog:** https://keepachangelog.com/
- **PEP 517:** https://peps.python.org/pep-0517/ (build system)
- **PEP 518:** https://peps.python.org/pep-0518/ (pyproject.toml)

## Support

**Issues:** https://github.com/scottsen/groqqy/issues

For release-specific issues, tag with `release` label.
