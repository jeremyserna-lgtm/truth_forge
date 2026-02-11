# Version Control

**The Standard** | Every change is atomic, traceable, reviewable, and reversible.

**Authority**: [07_STANDARDS.md](../07_STANDARDS.md) | **Status**: CANONICAL

---

## Quick Reference

| Requirement | Rule |
|-------------|------|
| Commits | Atomic, single-purpose, conventional format |
| Branches | Feature branches, protected main |
| Reviews | All changes require review |
| History | Linear history, no force push to main |
| Secrets | Never committed, always in .gitignore |
| Messages | Conventional commits format |

---

## WHY (Theory)

### The Observability Imperative

From 06_LAW: *"Every action must be observable."*

Version control is the audit log of code. Every commit is a decision. Every branch is an experiment. Every merge is an integration. Without proper version control, you lose the ability to understand how code evolved and why.

### The Reversibility Principle

Good version control enables fearless development. Any change can be reverted. Any state can be restored. Any decision can be revisited.

---

## WHAT (Specification)

### Branch Strategy

```
main (protected)
  │
  ├── feature/add-user-auth
  │     └── PR → main
  │
  ├── fix/login-timeout
  │     └── PR → main
  │
  └── release/v2.0.0 (if needed)
```

| Branch Type | Pattern | Purpose |
|-------------|---------|---------|
| Main | `main` | Production-ready code |
| Feature | `feature/{description}` | New functionality |
| Fix | `fix/{description}` | Bug fixes |
| Hotfix | `hotfix/{description}` | Emergency production fixes |
| Release | `release/v{version}` | Release preparation |

### MUST (Required)

#### Commit Messages

1. **Conventional Commits** — All commits MUST follow conventional commit format.

```
<type>(<scope>): <description>

[optional body]

[optional footer(s)]
```

**Types:**

| Type | Purpose | Example |
|------|---------|---------|
| `feat` | New feature | `feat(auth): add OAuth2 support` |
| `fix` | Bug fix | `fix(api): resolve timeout on large requests` |
| `docs` | Documentation | `docs(readme): update installation steps` |
| `style` | Formatting | `style: apply black formatting` |
| `refactor` | Code restructure | `refactor(db): extract query builder` |
| `perf` | Performance | `perf(cache): implement LRU eviction` |
| `test` | Tests | `test(auth): add login failure cases` |
| `chore` | Maintenance | `chore(deps): update dependencies` |
| `ci` | CI/CD | `ci: add security scanning` |

```bash
# ✅ Correct
feat(auth): add two-factor authentication

Implements TOTP-based 2FA with backup codes.
- Add QR code generation for authenticator apps
- Store encrypted backup codes
- Add rate limiting on verification

Closes #123

# ❌ Wrong
fixed stuff
update
WIP
```

2. **Atomic Commits** — Each commit MUST be a single logical change.

```bash
# ✅ Correct - separate commits for separate changes
git commit -m "feat(api): add user endpoint"
git commit -m "test(api): add user endpoint tests"
git commit -m "docs(api): document user endpoint"

# ❌ Wrong - mixed concerns
git commit -m "add user endpoint, tests, and update readme"
```

3. **Present Tense** — Commit messages MUST use imperative present tense.

```bash
# ✅ Correct
"add feature" not "added feature"
"fix bug" not "fixed bug"
"update docs" not "updated docs"
```

#### Branch Rules

4. **Protected Main** — The main branch MUST be protected.

```yaml
# Branch protection rules
main:
  require_pull_request: true
  required_reviews: 1
  require_status_checks: true
  require_linear_history: true
  no_force_push: true
  no_deletions: true
```

5. **Feature Branches** — All changes MUST go through feature branches.

```bash
# ✅ Correct workflow
git checkout -b feature/add-payment-processing
# ... make changes ...
git commit -m "feat(payments): add Stripe integration"
git push origin feature/add-payment-processing
# Create PR → Review → Merge

# ❌ Wrong - direct commit to main
git checkout main
git commit -m "add payment stuff"
git push origin main
```

6. **Branch Naming** — Branches MUST follow naming convention.

```bash
# Format: {type}/{brief-description}

# Features
feature/user-authentication
feature/payment-processing
feature/api-v2

# Fixes
fix/login-timeout
fix/memory-leak
fix/null-pointer

# Hotfixes (emergency)
hotfix/security-patch
hotfix/data-corruption
```

#### Code Review

7. **Pull Request Required** — All merges to main MUST go through PR.

```markdown
## PR Template

### Description
Brief description of changes

### Type of Change
- [ ] Feature
- [ ] Bug fix
- [ ] Refactor
- [ ] Documentation
- [ ] Other: ___

### Testing
- [ ] Unit tests added/updated
- [ ] Integration tests pass
- [ ] Manual testing completed

### Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No secrets committed
```

8. **Review Requirements** — PRs MUST have at least one approval.

#### Security

9. **No Secrets in Git** — Secrets MUST NOT be committed.

```bash
# .gitignore - REQUIRED entries
.env
.env.*
!.env.template
*.pem
*.key
*.p12
secrets/
credentials/
.aws/
```

```bash
# Pre-commit check
git secrets --scan
```

10. **No Force Push to Protected Branches** — History MUST be preserved.

```bash
# ✅ Correct - rebase locally before push
git rebase main
git push origin feature/my-branch

# ❌ Wrong - force push to main
git push --force origin main
```

### SHOULD (Recommended)

1. **Signed Commits** — Commits SHOULD be GPG signed.

```bash
git config --global commit.gpgsign true
git config --global user.signingkey YOUR_KEY_ID
```

2. **Small PRs** — PRs SHOULD be under 400 lines changed.

3. **Draft PRs** — Work in progress SHOULD use draft PRs.

4. **Linear History** — SHOULD prefer rebase over merge commits.

```bash
# Preferred
git fetch origin
git rebase origin/main
git push origin feature/my-branch

# Creates cleaner history than merge commits
```

5. **Squash on Merge** — Feature branches SHOULD squash commits.

```bash
# Many work-in-progress commits
feat: initial structure
feat: add validation
fix: typo
fix: tests

# Squashed to single commit on merge
feat(auth): add OAuth2 authentication
```

### MAY (Optional)

1. **Git Hooks** — Enforce standards with pre-commit hooks.
2. **Conventional Changelog** — Auto-generate changelogs from commits.
3. **Release Branches** — For complex release processes.

### MUST NOT (Prohibited)

1. **Never Force Push to Main** — History is sacred.
2. **Never Commit Secrets** — Even "temporarily."
3. **Never Bypass Reviews** — Even for "small" changes.
4. **Never Delete Protected Branches** — Without explicit approval.
5. **Never Commit Merge Conflicts** — Resolve completely before commit.

---

## HOW (Reference)

### Git Configuration

```bash
# ~/.gitconfig
[user]
    name = Your Name
    email = your.email@company.com
    signingkey = YOUR_GPG_KEY

[commit]
    gpgsign = true

[pull]
    rebase = true

[fetch]
    prune = true

[init]
    defaultBranch = main

[alias]
    st = status
    co = checkout
    br = branch
    ci = commit
    lg = log --oneline --graph --decorate
```

### Pre-commit Hooks

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
        args: ['--maxkb=500']
      - id: detect-private-key
      - id: check-merge-conflict

  - repo: https://github.com/commitizen-tools/commitizen
    rev: v3.13.0
    hooks:
      - id: commitizen
        stages: [commit-msg]

  - repo: https://github.com/awslabs/git-secrets
    rev: master
    hooks:
      - id: git-secrets
```

### Workflow Examples

```bash
# Starting a new feature
git checkout main
git pull origin main
git checkout -b feature/add-notifications

# Making commits
git add src/notifications.py
git commit -m "feat(notifications): add email notification service"

git add tests/test_notifications.py
git commit -m "test(notifications): add email notification tests"

# Keeping up to date
git fetch origin
git rebase origin/main

# Pushing for review
git push origin feature/add-notifications

# After PR approval - squash merge via GitHub/GitLab UI
```

### Reverting Changes

```bash
# Revert a single commit
git revert <commit-hash>

# Revert a merge
git revert -m 1 <merge-commit-hash>

# Create a fix branch from revert
git checkout -b fix/revert-broken-feature
git revert <commit-hash>
git push origin fix/revert-broken-feature
# Create PR
```

---

## Enforcement

### Automated Checks

| Tool | Check | Severity |
|------|-------|----------|
| commitlint | Conventional commits | error |
| git-secrets | No secrets | error |
| pre-commit | Hooks pass | error |
| GitHub/GitLab | Branch protection | error |

### CI Configuration

```yaml
# .github/workflows/pr.yml
name: PR Checks
on: [pull_request]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Validate commit messages
        uses: wagoid/commitlint-github-action@v5

      - name: Check for secrets
        uses: gitleaks/gitleaks-action@v2
```

### Escape Hatch

For emergency hotfixes:

```bash
# standard:override version-control-review - Emergency security patch
# Approved by: @security-lead at 2025-01-18 14:30 UTC
# Incident: SEC-2025-001
git push origin hotfix/security-patch
```

---

## Related Standards

- [DEPRECATION.md](DEPRECATION.md) — Version-based deprecation
- [SECURITY.md](SECURITY.md) — Secrets management
- [API_DESIGN.md](API_DESIGN.md) — API versioning

---

## Changelog

| Date | Change | Author |
|------|--------|--------|
| 2025-01-18 | Initial standard | Claude |
