# Operations Assessment

**Date:** January 20, 2026
**Updated:** Added Services delivery operations alongside Credential Atlas
**Purpose:** Define delivery operations for both product lines

---

## OPERATIONAL STATUS BY PRODUCT

| Component | Credential Atlas | The Services | Status |
|-----------|------------------|--------------|--------|
| Delivery method | BigQuery access | Session + docs | ✅ Ready |
| Process documented | Partial | Partial | ⚠️ Needs work |
| Infrastructure | Knowledge graph ready | Ready to deliver | ✅ |
| FEIN | 41-3378106 | (via CA) | ✅ **Received** |
| Payment collection | Ready to open bank | Ready to open bank | ⚠️ Open today |
| Contracts | Not created | Not created | ❌ |

---

## CREDENTIAL ATLAS: DELIVERY OPERATIONS

### The 4-Week Delivery Process

**Week 1: Discovery & Data Audit**
| Day | Activity | Deliverable |
|-----|----------|-------------|
| 1-2 | Kickoff call, access requirements | Meeting notes |
| 3-5 | Receive customer's credential data | Data received |

**Week 2: Credential Matching**
| Day | Activity | Deliverable |
|-----|----------|-------------|
| 6-7 | Map credentials to internal taxonomy | Mapping document |
| 8-10 | Match to institutional entities | Match report |

**Week 3: Outcome Integration**
| Day | Activity | Deliverable |
|-----|----------|-------------|
| 11-12 | Connect institutions to outcomes | Outcome linkage |
| 13-15 | Quality assurance | QA report |

**Week 4: Delivery**
| Day | Activity | Deliverable |
|-----|----------|-------------|
| 16-17 | Final dataset preparation | Dataset ready |
| 18-19 | Documentation | User guide |
| 20 | Walkthrough call, delivery | Access granted |

### Data Delivery Options

**Option 1: BigQuery Access (Technical Customers)**
- Grant read access to specific dataset
- Customer queries directly
- Already works

**Option 2: Data Export (Less Technical)**
- Generate CSV/JSON exports
- Deliver via secure link
- Manual process

**Option 3: Dashboard (Premium)**
- Looker Studio dashboard
- Visual interface
- Additional setup

### For Mo Lam (First Customer)
- Likely: BigQuery access (Peterson's has technical team)
- Backup: Export to their preferred format

---

## THE SERVICES: DELIVERY OPERATIONS

### The Seeing (90 Minutes)

**Before Session:**
| When | Action |
|------|--------|
| Booking | Send calendar link, collect $300 |
| -1 day | Confirm appointment |
| -1 hour | Prepare blank canvas for mapping |

**During Session:**
| Time | Activity |
|------|----------|
| 0-15 min | Orientation: "Tell me what's not working" |
| 15-60 min | Active mapping: Draw architecture, identify leaks |
| 60-75 min | The Mirror: Show map, name what they couldn't see |
| 75-90 min | First move: Recommend action, propose Pilot if fit |

**After Session:**
| When | Action |
|------|--------|
| Same day | Send architecture map (PDF or screenshot) |
| +1 day | Send Pilot proposal if appropriate |
| +7 days | Follow up if no response |

**Deliverables:**
- Architecture map (visual)
- Gap identification (written)
- First move recommendation
- Pilot proposal (if fit)

### The Pilot (1 Week)

**Before Work:**
| When | Action |
|------|--------|
| Contract | Send Pilot proposal, collect $3,000 |
| Day 0 | Kickoff: Confirm scope, get access |

**During Week:**
| Day | Activity | Output |
|-----|----------|--------|
| 1-2 | Build structure | Skeleton in place |
| 3-4 | Test breath (HOLD → AGENT → HOLD) | System runs |
| 5 | Document + handoff | Delivered |

**After Delivery:**
| When | Action |
|------|--------|
| Day 5 | Handoff call: Walk through, confirm breathing |
| +3 days | Check-in: How is it running? |
| +7 days | Propose Stewardship if fit |

**Deliverables:**
- One working mechanism
- Documentation (what it does, how it works)
- Proof that it breathes (HOLD → AGENT → HOLD)

### The Stewardship (Ongoing)

**Monthly Rhythm:**
| Cadence | Activity |
|---------|----------|
| Weekly | Heartbeat check (vital signs) |
| Bi-weekly | Breath audit (is HOLD → AGENT → HOLD clean?) |
| Monthly | Health report to client |
| As needed | Molt support (evolution when needed) |

**Monthly Report Template:**
```
STEWARDSHIP HEALTH REPORT
Month: [Month Year]
Client: [Name]

VITAL SIGNS
- Heartbeat: [Running / Issues]
- Breath: [Clean / Intervention needed]
- Growth: [Stable / Learning / Adapting]

ACTIVITIES THIS MONTH
- [What was done]
- [Issues addressed]
- [Improvements made]

NEXT MONTH
- [Planned maintenance]
- [Potential molt if applicable]

SYSTEM STATUS: [Healthy / Needs Attention / Critical]
```

**Exit Process (Either Party):**
- 30 days notice
- Final health report
- System either lives independently or graceful death
- No zombie infrastructure

### The Anvil (Hardware Install)

**Pre-Install:**
| Step | Activity |
|------|----------|
| 1 | Hardware specification based on needs |
| 2 | Procurement (client pays hardware cost) |
| 3 | Schedule install date |

**Install Week:**
| Day | Activity |
|-----|----------|
| 1-2 | Physical setup, OS configuration |
| 3-4 | AI stack installation, air-gap verification |
| 5 | Testing, handoff, documentation |

**Deliverables:**
- Operational local AI system
- Air-gap verification
- Documentation
- Training session

---

## INFRASTRUCTURE INVENTORY

### What Exists (Built)

| System | Location | Status |
|--------|----------|--------|
| Revenue Tracking | `scripts/profitability/revenue_tracking.py` | Built, not deployed |
| Cost Tracking | `scripts/profitability/cost_tracking_dashboard.py` | Built, not deployed |
| CRM Integration | `src/services/central_services/contacts/twenty_crm.py` | Built, not configured |
| Cost Protection Hooks | `scripts/hooks/care_cost_protection.py` | Active |
| BigQuery Integration | Multiple files | Active |
| Knowledge Graph | 51.8M entities | Active |

### What's Missing (Not Built)

| System | Need | Priority |
|--------|------|----------|
| Website | Public presence | HIGH |
| Business Email | Professional communication | HIGH |
| Invoice Template | Payment collection | HIGH |
| Contract Templates | Legal protection | HIGH |
| Seeing Deliverable Template | Session output | MEDIUM |
| Pilot Documentation Template | Build handoff | MEDIUM |

---

## MINIMUM VIABLE OPERATIONS

### Before First Customer (MUST HAVE)

| Item | Credential Atlas | The Services | Status |
|------|------------------|--------------|--------|
| FEIN | 41-3378106 | (via CA) | ✅ **Received** |
| Bank Account | Ready to open | Ready to open | ⚠️ **Open today** |
| Invoice Template | Required | Required | ❌ Create today |
| Basic Contract | Required | $300 = payment is agreement | ❌ Create this week |
| Delivery Method | BigQuery | Session + PDF | ✅ Ready |

### Before Second Customer (SHOULD HAVE)

| Item | Status |
|------|--------|
| Website | Domain only |
| Business Email | Pending |
| CRM Tracking | Code exists |
| Onboarding Checklist | Not documented |
| Seeing Template | Not created |
| Pilot Template | Not created |

---

## PAYMENT INFRASTRUCTURE

### Current State
- ✅ FEIN received (41-3378106)
- ⚠️ Bank account ready to open
- ❌ No invoice template

### Payment Flow by Product

**Credential Atlas:**
```
Contract signed → Invoice 50% → Work begins →
Delivery → Invoice 50% → Complete
```

**The Seeing:**
```
Session booked → Payment 100% before session → Session
```

**The Pilot:**
```
Proposal accepted → Payment 100% before work → Build → Deliver
```

**The Stewardship:**
```
Agreement signed → First month payment → Work begins →
Monthly billing (1st of month)
```

### Invoice Template

```
Credential Atlas LLC
Colorado SOS ID: 20258406582
FEIN: [pending]

INVOICE #[number]
Date: [date]
Due: [date + terms]

Bill To:
[Customer Name]
[Address]

Services:
[Description of service]

Amount: $[amount]

Payment: ACH/Wire to [bank details]
         or PayPal/Zelle: jeremy.serna@gmail.com (interim)
```

---

## COMMUNICATION INFRASTRUCTURE

### Email
- **Current:** jeremy.serna@gmail.com
- **Needed:** jeremy@credentialatlas.com
- **Setup:** Google Workspace ($6/mo) or Zoho (free)

### Scheduling
- **Current:** Manual
- **Needed:** Calendly (free tier)
- **For:** Seeing sessions, discovery calls

---

## DEPLOYMENT CHECKLIST

### TODAY (January 20, 2026)

| Task | Status | Time |
|------|--------|------|
| ✅ FEIN received | Complete | — |
| Open Mercury bank account | **DO NOW** | 30 min |
| Create CA invoice template | **DO NOW** | 30 min |
| Send Mo Lam email | **DO NOW** | 30 min |

### This Week

| Task | Status | Blocks |
|------|--------|--------|
| Set up business email | Pending | — |
| Create CA contract template | Pending | — |
| Create Seeing deliverable template | Pending | — |
| Set up Calendly | Pending | — |
| Research 5 EdTech contacts | Pending | — |
| Send 5 cold emails | Pending | — |

---

## VERIFICATION

Operations ready when:

**Both Products:**
- [ ] Can receive payment (bank + invoice)
- [ ] Can communicate professionally (email)
- [ ] Can sign agreements (contracts)

**Credential Atlas:**
- [ ] Can deliver data (BigQuery access) ✅
- [ ] 4-week process documented
- [ ] First delivery complete

**The Services:**
- [ ] Can run Seeing session
- [ ] Seeing deliverable template ready
- [ ] Can run Pilot (1-week build)
- [ ] Pilot documentation template ready
- [ ] Stewardship monthly rhythm defined

---

## THE HONEST ASSESSMENT

**✅ UNBLOCKED:**
- FEIN received (41-3378106)
- Bank account ready to open

**NOT Blocking:**
- Infrastructure works
- Delivery methods ready
- Knowledge graph operational
- Services ready to deliver

**Action Required TODAY:**
1. Open Mercury bank account (30 min)
2. Create invoice template (30 min)
3. Send Mo Lam email (30 min)

---

*Operations UNBLOCKED. EIN received. Open bank account and send outreach TODAY.*
