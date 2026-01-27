# History

**Git history is a story. Make it readable.**

---

## The Rule

Maintain clean, linear history. Future readers must understand the evolution.

---

## Clean History Principles

| Principle | Implementation |
|-----------|----------------|
| Linear when possible | Rebase feature branches |
| Meaningful commits | Squash WIP before merge |
| No merge noise | Avoid unnecessary merge commits |
| Traceable | Link commits to issues/PRs |

---

## Rebase vs Merge

```
# PREFERRED - Rebase (linear history)
main:    A ─── B ─── C ─── D ─── E
                              ▲
                         (feature rebased and merged)

# AVOID - Merge commits (noisy history)
main:    A ─── B ─────────── M ─── (merge commit)
              \             /
feature:       C ─── D ─── E
```

---

## When to Squash

| Situation | Action |
|-----------|--------|
| WIP commits | Squash into logical unit |
| "fix typo" commits | Squash into parent |
| Logical separate changes | Keep separate |

```bash
# Squash last 3 commits into one
git rebase -i HEAD~3
# Mark commits as 'squash' or 's'
```

---

## History Hygiene

```bash
# Before pushing feature branch, clean up
git rebase -i main

# Sync with main (rebase, not merge)
git fetch origin
git rebase origin/main

# Force push to YOUR branch only (never shared branches)
git push --force-with-lease origin feature/my-branch
```

---

## Protected History

| Branch | Protection |
|--------|------------|
| main | No force push, no direct commits |
| release/* | No force push |
| feature/* | Force push allowed (your branch) |

---

## Git Log Best Practices

```bash
# Useful log formats
git log --oneline --graph
git log --pretty=format:"%h %s (%an, %ar)"

# Find when something changed
git log -p -- path/to/file
git blame path/to/file
```

---

## History and Molts

During molts, history tells the transformation story:

```
# Molt history should show clear phases
a1b2c3d feat: add new architecture
d4e5f6g refactor: migrate component A
g7h8i9j refactor: migrate component B
j0k1l2m docs: update for new naming
m3n4o5p chore: remove deprecated code
```

---

## Anti-Patterns

```bash
# WRONG - Force push to shared branch
git push --force origin main

# WRONG - Merge main into feature repeatedly
# Creates noisy history with merge commits

# WRONG - Giant squash of unrelated changes
# 50 files changed in one "update everything" commit
```

---

## UP

[INDEX.md](INDEX.md)
