# Branching

**Feature branches isolate work. Main is always deployable.**

---

## The Rule

Use GitHub Flow: short-lived feature branches that merge to main via PR.

---

## GitHub Flow

```
main ─────────────────────────────────────────────────►
       │                            ▲
       └── feature/add-login ───────┘
                (branch)        (merge via PR)
```

| Step | Action |
|------|--------|
| 1 | Create branch from main |
| 2 | Make commits on branch |
| 3 | Open PR when ready |
| 4 | Review and approve |
| 5 | Merge to main |
| 6 | Delete branch |

---

## Branch Naming

```
{type}/{description}
```

| Type | Purpose | Example |
|------|---------|---------|
| `feature/` | New functionality | `feature/user-authentication` |
| `fix/` | Bug fixes | `fix/login-validation` |
| `refactor/` | Code improvement | `refactor/extract-pipeline` |
| `docs/` | Documentation | `docs/api-reference` |
| `molt/` | Major transformation | `molt/truth-engine-to-forge` |

---

## Branch Lifecycle

| State | Duration | Action |
|-------|----------|--------|
| Active | Days to weeks | Regular commits |
| Ready | Hours | PR open, awaiting review |
| Merged | Immediate | Delete after merge |
| Stale | > 2 weeks | Evaluate: merge, rebase, or close |

---

## Anti-Patterns

```bash
# WRONG - Committing directly to main
git commit -m "quick fix" && git push origin main

# WRONG - Long-lived feature branches
# Branch open for months, massive merge conflicts

# WRONG - Unclear naming
git checkout -b johns-branch
git checkout -b stuff
```

---

## Correct Pattern

```bash
# Create feature branch
git checkout -b feature/add-user-dashboard

# Work on feature
git add .
git commit -m "feat: add user dashboard component"

# Push and create PR
git push -u origin feature/add-user-dashboard
gh pr create --title "Add user dashboard" --body "..."

# After merge, clean up
git checkout main
git pull
git branch -d feature/add-user-dashboard
```

---

## Molt Branches

For major transformations (molts):

```bash
# Molt branch naming
git checkout -b molt/truth-engine-to-forge

# Molt branches may be longer-lived but must have:
# - Clear scope document
# - Regular sync with main
# - Phased merge plan
```

---

## UP

[INDEX.md](INDEX.md)
