# Commits

**Commit messages explain WHY. The diff shows WHAT.**

---

## The Rule

Use Conventional Commits format. Every commit tells a story.

---

## Conventional Commits Format

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

| Component | Required | Purpose |
|-----------|----------|---------|
| type | Yes | Category of change |
| scope | No | Module/component affected |
| description | Yes | Short summary (imperative mood) |
| body | No | Detailed explanation |
| footer | No | Breaking changes, issue refs |

---

## Commit Types

| Type | Purpose | Example |
|------|---------|---------|
| `feat` | New feature | `feat: add user authentication` |
| `fix` | Bug fix | `fix: correct validation error` |
| `docs` | Documentation | `docs: update API reference` |
| `refactor` | Code restructure | `refactor: extract pipeline logic` |
| `test` | Test changes | `test: add integration tests` |
| `chore` | Maintenance | `chore: update dependencies` |
| `style` | Formatting | `style: apply ruff formatting` |
| `perf` | Performance | `perf: optimize database queries` |

---

## Good Commit Messages

```bash
# GOOD - Explains why
feat(auth): add JWT token refresh

Tokens were expiring during long sessions, forcing re-login.
Added automatic refresh 5 minutes before expiry.

Closes #123

# GOOD - Clear scope and action
fix(pipeline): handle empty batch gracefully

# GOOD - Breaking change noted
feat(api)!: change authentication endpoint

BREAKING CHANGE: /auth/login now returns JWT instead of session cookie
```

---

## Bad Commit Messages

```bash
# BAD - No type
"fixed stuff"

# BAD - Too vague
"updates"

# BAD - Describes what (the diff shows that)
"changed line 42 in auth.py"

# BAD - Past tense
"added feature"  # Should be "add feature"
```

---

## Commit Frequency

| Guideline | Reason |
|-----------|--------|
| Commit logical units | Each commit should be atomic |
| Commit often | Smaller commits are easier to review |
| Don't commit broken code | Main should always work |
| Squash WIP before merge | Clean history for others |

---

## The WHY Principle

The diff shows WHAT changed. The message explains WHY.

```bash
# WRONG - Repeats the diff
"change MAX_RETRIES from 3 to 5"

# RIGHT - Explains the why
"fix(retry): increase retries for flaky external API

The payment gateway times out under load.
Increasing retries from 3 to 5 reduces failed transactions by 40%."
```

---

## UP

[INDEX.md](INDEX.md)
