# LINKS

**Navigate through hubs, not meshes.**

---

## The Rule

Documents link UP to INDEX. INDEX links UP to parent INDEX. That's the entire navigation system.

---

## Mesh vs Hub

```
MESH (fragile):
A ──→ B ──→ C
│     │     │
└──→──┴──→──┘
Every node links to every node.
One move breaks many links.

HUB (resilient):
A ──→ INDEX ←── B ←── C
Each node links to hub.
One move updates one hub.
```

---

## The Pattern

```
Document → UP → INDEX
                  ↓
           UP → Parent INDEX
                  ↓
           UP → ... → ALPHA
```

Documents don't know about each other.

---

## HOLD:AGENT:HOLD Parallel

```
AGENT doesn't know about other AGENTs.
HOLD handles coordination.

DOCUMENT doesn't know about other DOCUMENTs.
INDEX handles coordination.
```

---

## When Structure Changes

1. Identify affected INDEX files
2. Update only those INDEX files
3. Child documents unchanged

---

## UP

[INDEX.md](INDEX.md)
