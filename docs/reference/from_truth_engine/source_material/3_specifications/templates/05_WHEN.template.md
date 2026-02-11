# {SYSTEM_NAME}: When To Use

**Doc ID**: doc:{CATEGORY}:primitive:05:when
**Series**: PRIMITIVE
**System**: {SYSTEM_NAME}

---

## TL;DR

- Use when: {USE_CONDITIONS}
- Don't use when: {DONT_USE_CONDITIONS}
- Alternative: {ALTERNATIVE}

---

## Use Cases

| Scenario | Use This? | Why |
|----------|-----------|-----|
| {SCENARIO_1} | Yes | {REASON} |
| {SCENARIO_2} | Yes | {REASON} |
| {SCENARIO_3} | No | {REASON} |
| {SCENARIO_4} | No | {REASON} |

---

## Decision Tree

```
Need to {ACTION}?
│
├── Yes → Is {CONDITION_1}?
│   │
│   ├── Yes → USE {SYSTEM_NAME}
│   │
│   └── No → Is {CONDITION_2}?
│       │
│       ├── Yes → USE {SYSTEM_NAME}
│       │
│       └── No → Use {ALTERNATIVE}
│
└── No → Don't use this
```

---

## Anti-Patterns

### Don't Use For

| Wrong Use | Why Wrong | Instead Use |
|-----------|-----------|-------------|
| {WRONG_USE_1} | {WHY_WRONG} | {ALTERNATIVE} |
| {WRONG_USE_2} | {WHY_WRONG} | {ALTERNATIVE} |

---

## Timing Considerations

| When | Consideration |
|------|---------------|
| Startup | {STARTUP_NOTES} |
| Runtime | {RUNTIME_NOTES} |
| Shutdown | {SHUTDOWN_NOTES} |
| Maintenance | {MAINTENANCE_NOTES} |

---

## Related

- [Where It Lives](04_WHERE.md)
- [Who's Involved](06_WHO.md)
