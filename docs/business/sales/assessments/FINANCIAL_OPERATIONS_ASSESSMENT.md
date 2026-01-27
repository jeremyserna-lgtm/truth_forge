# Financial Operations Assessment

**Date:** January 20, 2026
**Updated:** Added Services revenue streams alongside Credential Atlas
**Purpose:** Define how money flows in and out for both product lines

---

## CURRENT FINANCIAL STATE

### Entity Information

| Field | Value |
|-------|-------|
| Legal Name | Credential Atlas LLC |
| State | Colorado |
| Formation Date | December 28, 2025 |
| Colorado SOS ID | 20258406582 |
| FEIN | **41-3378106** ✅ Received Jan 6, 2026 |
| Bank Account | **Ready to open** (EIN received) |

**Second Entity (for future B2C):**
| Field | Value |
|-------|-------|
| Legal Name | Primitive Engine LLC |
| Formation Date | January 6, 2026 |
| Colorado SOS ID | 20261019859 |
| FEIN | **41-3472217** ✅ Received Jan 8, 2026 |

### Revenue Status

| Metric | Current |
|--------|---------|
| Revenue YTD | $0 |
| Pipeline Value | TBD (Mo Lam + Services) |
| MRR | $0 |
| Customers | 0 |

### Cost Status

| Category | Monthly Budget | Current Spend |
|----------|----------------|---------------|
| GCP (BigQuery, etc.) | $1,500 | Variable |
| Software/Tools | ~$100 | Active |
| CRITICAL THRESHOLD | $1,400 | DO NOT EXCEED |

---

## REVENUE STREAMS BY PRODUCT

### Credential Atlas Revenue

| Offering | Price | Type | When |
|----------|-------|------|------|
| Entry Project | $15,000 | One-time | 4 weeks |
| State Project | $20-25,000 | One-time | 4-6 weeks |
| API Subscription | $1,500-8,000/mo | Recurring | After project |
| State License | $25-35,000/year | Annual | After project |

### The Services Revenue

| Service | Price | Type | When |
|---------|-------|------|------|
| The Seeing | $300 | One-time | 90 min session |
| The Pilot | $3,000 | One-time | 1 week |
| The Stewardship | $5,000/mo | Recurring | Monthly |
| The Anvil | $15-22,000 | One-time | Hardware + setup |

### Revenue Mix Target (Year 1)

| Source | Amount | % of Revenue |
|--------|--------|--------------|
| Credential Atlas Projects | $60-100K | 60% |
| Credential Atlas Subscriptions | $10-20K | 15% |
| Services (Seeing + Pilot) | $10-20K | 15% |
| Stewardship Retainers | $10-30K | 10% |
| **TOTAL** | $90-170K | 100% |

---

## HOW MONEY COMES IN

### Payment Flow by Product

**Credential Atlas:**
```
Contract signed → Invoice 50% upfront → Work →
Invoice 50% on delivery → Complete
```

**The Seeing:**
```
Session booked → Payment 100% before session → Session
```

**The Pilot:**
```
Proposal accepted → Payment 100% before work →
Build → Deliver
```

**The Stewardship:**
```
Agreement signed → First month payment → Work →
Monthly billing (1st of month)
```

### Payment Methods

| Method | Setup Required | Fees | Use For |
|--------|----------------|------|---------|
| ACH Transfer | Bank account | $0 | Projects, retainers |
| Wire Transfer | Bank account | ~$15-25 | Large projects |
| PayPal/Venmo | Account | 2.9% | Seeing sessions (interim) |
| Credit Card | Stripe | 2.9% + $0.30 | If requested |

**Recommendation:**
- Credential Atlas: ACH for projects
- Services: PayPal/Stripe for $300-$3,000 payments (convenience)
- Stewardship: ACH monthly

### Invoice Process

1. Create invoice from template
2. Send to customer (PDF via email)
3. Track in spreadsheet
4. Follow up at Net 15 if not paid
5. Record payment when received

---

## HOW MONEY GOES OUT

### Current Expenses

| Expense | Amount | Frequency |
|---------|--------|-----------|
| GCP Services | Variable | Monthly |
| Domain | ~$12 | Annual |
| Software subscriptions | ~$100 | Monthly |

### Projected First-Year Expenses

| Category | Monthly | Annual |
|----------|---------|--------|
| GCP | $500-1,500 | $6,000-18,000 |
| Business email | $6 | $72 |
| Website (Carrd) | $2 | $19 |
| Software/Tools | $100 | $1,200 |
| Calendly Pro (if needed) | $12 | $144 |
| Professional services | TBD | $1,000-3,000 |
| **TOTAL** | $600-1,600 | $8,000-22,000 |

### The $1,400 Rule

> If monthly spend approaches $1,400, STOP. This threshold protects housing.

Cost protection hooks active in `care_cost_protection.py`.

---

## CASH FLOW PROJECTION

### Scenario: First Customers in February

| Month | CA Revenue | Services Revenue | Expenses | Net | Cumulative |
|-------|------------|------------------|----------|-----|------------|
| Jan | $0 | $0 | $500 | -$500 | -$500 |
| Feb | $7,500 | $300 | $500 | +$7,300 | +$6,800 |
| Mar | $7,500 | $3,000 | $600 | +$9,900 | +$16,700 |
| Apr | $0 | $5,300 | $700 | +$4,600 | +$21,300 |
| May | $15,000 | $5,300 | $800 | +$19,500 | +$40,800 |
| Jun | $0 | $5,600 | $900 | +$4,700 | +$45,500 |

**Key Insight:**
- Services provides smoother cash flow (Stewardship = MRR)
- CA projects create lumpy revenue
- Combined = more stable

### Break-Even Analysis

**Fixed Monthly Costs:** ~$700
**Variable per Project:** ~$200

**Break-even scenarios:**
- 1 CA project ($15K) = profitable
- 10 Seeing sessions ($3K) + 1 Pilot ($3K) = profitable
- 2 Stewardship clients ($10K/mo) = very profitable

---

## PRICING MARGIN ANALYSIS

### Credential Atlas Margins

| Offering | Price | Est. Cost | Margin |
|----------|-------|-----------|--------|
| $15K Project | $15,000 | $2,000 | 87% |
| API $1.5K/mo | $1,500 | $300 | 80% |
| API $8K/mo | $8,000 | $500 | 94% |

### Services Margins

| Service | Price | Est. Hours | $/Hour | Margin |
|---------|-------|------------|--------|--------|
| Seeing | $300 | 2 (incl prep) | $150/hr | 90% |
| Pilot | $3,000 | 40 | $75/hr | 85% |
| Stewardship | $5,000 | 20 | $250/hr | 90% |
| Anvil | $15,000 | 40 + $8K HW | $175/hr | 45% |

**Takeaway:** All services are highly profitable. Stewardship has best $/hour.

---

## BOOKKEEPING

### Minimum Viable Tracking

| Date | Type | Product | Description | Amount | Balance |
|------|------|---------|-------------|--------|---------|
| 2/15 | Income | Services | Seeing - Client A | +300 | 300 |
| 2/20 | Income | CA | Mo Lam - 50% | +7,500 | 7,800 |
| 2/25 | Expense | GCP | February | -450 | 7,350 |
| 3/1 | Income | Services | Pilot - Client A | +3,000 | 10,350 |

### Categories to Track

**Income:**
- Credential Atlas - Projects
- Credential Atlas - Subscriptions
- Services - Seeing
- Services - Pilot
- Services - Stewardship
- Services - Anvil

**Expenses:**
- GCP (BigQuery, Cloud Run, Storage)
- Software (tools, subscriptions)
- Professional Services (legal, accounting)
- Marketing (website)
- Hardware (for Anvil builds)

---

## TAX PREPARATION

### What to Track

| Item | Why |
|------|-----|
| All income by category | Revenue reporting |
| All expenses by category | Deductions |
| Home office percentage | Deduction |
| Equipment purchases | Depreciation |
| Mileage (if client meetings) | Deduction |

### Quarterly Estimated Taxes

If profitable, pay quarterly:
- Q1: April 15
- Q2: June 15
- Q3: September 15
- Q4: January 15

**Rule:** Set aside 25-30% of net profit for taxes.

---

## FINANCIAL MILESTONES

### Immediate (Before First Customer)

| Milestone | Status | Blocks |
|-----------|--------|--------|
| FEIN received | Pending | IRS |
| Bank account opened | Blocked | FEIN |
| Invoice template created | Not done | - |
| Bookkeeping spreadsheet | Not done | - |

### First Revenue

| Milestone | When | What It Proves |
|-----------|------|----------------|
| First Seeing paid | Session booked | Services work |
| First CA invoice | Contract signed | CA works |
| First Stewardship | Pilot converts | Recurring revenue possible |

### Stability ($5K/mo MRR)

| Milestone | What It Means |
|-----------|---------------|
| 1 Stewardship client | $5K/mo recurring |
| 2 API subscriptions | $3K+/mo recurring |
| Combined $5K MRR | Covers all expenses |

### Break-Even ($75K/year)

| Milestone | What It Means |
|-----------|---------------|
| Revenue > Expenses | Self-sustaining |
| Runway > 6 months | Stability |
| Can consider help | Scaling possible |

---

## BANK ACCOUNT SETUP — DO TODAY

### Requirements (All Met ✅)

1. ✅ FEIN (41-3378106)
2. ✅ LLC formation documents
3. ✅ Colorado SOS ID (20258406582)
4. ✅ Government ID (have)

### Recommended Banks

| Bank | Why | Notes |
|------|-----|-------|
| Mercury | Startup-focused, no fees | Online |
| Relay | No fees, multiple accounts | Online |
| Chase | Physical branches | May have fees |

### Setup Checklist

1. [x] FEIN received (41-3378106)
2. [ ] Choose bank (Mercury recommended)
3. [x] Gather documents (have all)
4. [ ] Apply online
5. [ ] Fund initial deposit
6. [ ] Set up online banking

---

## FINANCIAL CONTROLS

### Separation of Funds

**RULE:** Business and personal money never mix.
- All business income → business account
- All business expenses → from business account
- Pay yourself via owner's draw

### Spending Authority

| Level | Action |
|-------|--------|
| Under $100 | Just do it |
| $100-500 | Pause and consider |
| $500-1,400 | Plan carefully |
| Over $1,400 | DO NOT SPEND |

### Monthly Review

1. Reconcile bank account
2. Update bookkeeping
3. Review GCP vs budget
4. Check runway
5. Update revenue tracking

---

## VERIFICATION

Financial operations ready when:

1. [x] FEIN received ✅ (41-3378106)
2. [ ] Bank account open
3. [ ] Invoice templates created (CA + Services)
4. [ ] Bookkeeping system chosen
5. [ ] Expense categories defined
6. [ ] Tax plan documented
7. [ ] Spending controls understood

---

## THE HONEST ASSESSMENT

**✅ UNBLOCKED:**
- FEIN received (January 6, 2026)
- All documents ready for bank account

**Ready:**
- LLC formed
- Cost tracking exists
- Revenue tracking code exists
- Know what to do

**Action Required TODAY:**
1. Open Mercury account (30 min)
2. Create invoice templates (30 min)
3. Set up bookkeeping spreadsheet (30 min)

**Timeline:** 1-2 hours to be fully payment-ready.

---

*Financial operations UNBLOCKED. EIN received. Open bank account TODAY.*
