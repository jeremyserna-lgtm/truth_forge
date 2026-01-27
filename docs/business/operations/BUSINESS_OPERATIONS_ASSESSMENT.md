# BUSINESS OPERATIONS ASSESSMENT

**Date:** January 20, 2026
**Purpose:** Comprehensive assessment of all business operations needs
**Status:** Initial assessment

---

## EXECUTIVE SUMMARY

You have two LLCs, two product lines, bank accounts open, and zero customers. The goal is **minimum viable operations** that can scale—not enterprise software you'll never use.

### Current State

| Category | Status | Urgency |
|----------|--------|---------|
| Legal Entities | ✅ Complete | — |
| Banking | ✅ Active (Primitive Engine) | — |
| Accounting | ❌ Nothing set up | HIGH |
| CRM | ❌ Nothing set up | MEDIUM |
| Invoicing | ❌ No templates | HIGH |
| Contracts | ❌ No templates | MEDIUM |
| Email/Calendar | ⚠️ Using personal | LOW |
| Project Management | ⚠️ Ad hoc | LOW |

### Recommended Stack (Day 1)

| Function | Tool | Cost | Why |
|----------|------|------|-----|
| Banking | Mercury | Free | Already open |
| Accounting | Wave | Free | Good enough for <$100K |
| Invoicing | Wave | Free | Integrated with accounting |
| CRM | Notion or Spreadsheet | Free | Under 20 prospects |
| Contracts | Google Docs | Free | Simple templates |
| Scheduling | Calendly | Free tier | 1 event type |
| Email | Gmail | Free | Already have |

**Total Monthly Cost: $0**

---

## 1. ACCOUNTING & BOOKKEEPING

### The Need

Track income, expenses, and prepare for taxes. Two LLCs means potentially two sets of books (or run everything through one).

### Current State

- No accounting software
- No bookkeeper
- No chart of accounts
- No expense tracking system

### Options

| Option | Cost | Pros | Cons |
|--------|------|------|------|
| **Wave** | Free | Full accounting, invoicing, receipts | Limited integrations |
| **QuickBooks Self-Employed** | $15/mo | Tax categories, mileage | Not full accounting |
| **QuickBooks Simple Start** | $30/mo | Full accounting, common | Overkill for now |
| **Spreadsheet** | Free | Full control | Manual, error-prone |
| **Bookkeeper** | $200-500/mo | Hands-off | Expensive for zero revenue |

### Recommendation: Wave (Free)

**Why:** Full double-entry accounting, free invoicing, receipt scanning. Good enough until you hit $100K+ revenue or need payroll.

### Setup Checklist

- [ ] Create Wave account
- [ ] Connect Mercury bank account
- [ ] Set up chart of accounts (Income: CA Projects, CA API, Services | Expenses: Cloud, Software, Professional)
- [ ] Create invoice templates
- [ ] Set up receipt capture (mobile app)

### Decision Required

**Run both entities through one Wave account?**
- Simpler bookkeeping
- Use "categories" or "tags" to separate CA vs Services vs Primitive
- Can separate later if needed

**Or separate Wave accounts per entity?**
- Clean separation from day one
- More overhead
- Better if you might sell one entity

**Recommended:** One Wave account, use tags/categories. Separate if revenue exceeds $50K per entity.

---

## 2. CRM (CUSTOMER RELATIONSHIP MANAGEMENT)

### The Need

Track prospects, conversations, deals, and follow-ups. At your stage: **do not buy Salesforce**.

### Current State

- No CRM
- Prospects exist in head/conversations
- No pipeline tracking

### Options

| Option | Cost | Pros | Cons |
|--------|------|------|------|
| **Spreadsheet** | Free | Full control, simple | Manual, no automation |
| **Notion** | Free | Flexible, databases | Learning curve |
| **HubSpot Free** | Free | Real CRM, email tracking | Overkill, vendor lock-in |
| **Pipedrive** | $15/mo | Sales-focused, simple | Costs money |
| **Airtable** | Free tier | Flexible, views | Limited on free |

### Recommendation: Spreadsheet → Notion

**Phase 1 (Now - 10 prospects):** Google Sheet
- Columns: Name, Company, Product Interest (CA/Services), Status, Last Contact, Next Action, Notes
- Simple, fast, no learning curve

**Phase 2 (10+ prospects):** Notion database
- Better views, relations, filters
- Can link to project pages

### CRM Fields (Minimum Viable)

| Field | Purpose |
|-------|---------|
| Name | Contact name |
| Company | Organization |
| Email | Contact |
| Phone | Contact |
| Product | CA or Services |
| Source | How they found you |
| Status | Lead → Contacted → Discovery → Proposal → Negotiation → Closed Won/Lost |
| Last Contact | Date |
| Next Action | What to do |
| Next Action Date | When |
| Notes | Context |
| Deal Value | $ amount |

### Pipeline Stages

**Credential Atlas:**
1. Lead (identified)
2. Contacted (outreach sent)
3. Discovery (call scheduled or completed)
4. Proposal (sent)
5. Negotiation (discussing terms)
6. Closed Won / Closed Lost

**The Services:**
1. Mentioned (told someone about Seeing)
2. Interested (they want to book)
3. Seeing Scheduled
4. Seeing Complete
5. Pilot Discussion
6. Pilot Sold / Not Interested

### Setup Checklist

- [ ] Create Google Sheet with columns above
- [ ] Add Mo Lam as first entry
- [ ] Add Ashutosh (Google inbound)
- [ ] Add any friends you've mentioned Services to
- [ ] Review and update weekly

---

## 3. INVOICING & PAYMENTS

### The Need

Get paid. Send professional invoices. Track who's paid.

### Current State

- No invoice templates
- Mercury accounts open (can receive ACH)
- No payment processor

### Options for Invoicing

| Option | Cost | Pros | Cons |
|--------|------|------|------|
| **Wave** | Free | Integrated accounting | Limited customization |
| **Stripe Invoicing** | 0.4% | Professional, online pay | Fees |
| **Square Invoices** | 2.9% + $0.30 | Easy, card payments | Higher fees |
| **PayPal Invoices** | 2.9% + $0.49 | Everyone has PayPal | Fees, looks informal |
| **PDF + ACH** | Free | No fees | Manual, no tracking |

### Payment Methods to Accept

| Method | When to Use | Cost |
|--------|-------------|------|
| **ACH/Wire** | Projects >$5K | Free (Mercury) |
| **Check** | If customer insists | Free |
| **Credit Card** | Convenience for small amounts | 2.9% |
| **PayPal/Venmo** | Quick payments, Services | 2.9% |

### Recommendation

**For Projects ($5K+):** Wave invoice + ACH payment
- Send Wave invoice
- Include Mercury bank details for ACH
- No fees

**For Services ($300-$5K):** Wave invoice + Card option
- Send Wave invoice with Stripe/PayPal link
- Eat the 2.9% for convenience
- Or offer ACH for discount

### Invoice Template Elements

| Element | Credential Atlas | The Services |
|---------|------------------|--------------|
| From | Credential Atlas LLC | Primitive Engine LLC |
| EIN | 41-3378106 | 41-3472217 |
| Address | 960 N Sherman St, Denver, CO 80203 | 960 N Sherman St Apt 1E, Denver, CO 80203 |
| Bank | TBD or Primitive Engine | Mercury (routing: 121145433) |
| Payment Terms | Net 15 or 50% upfront | Due on receipt |

### Setup Checklist

- [ ] Create Wave account
- [ ] Set up business profile(s)
- [ ] Add bank account for deposits
- [ ] Create invoice template for CA
- [ ] Create invoice template for Services
- [ ] Test invoice flow (send to self)

---

## 4. CONTRACTS & LEGAL TEMPLATES

### The Need

Protect yourself. Set expectations. Get agreement before work.

### Current State

- No contracts
- No templates
- Operating on handshakes

### Templates Needed

| Template | Product | Urgency | Complexity |
|----------|---------|---------|------------|
| **Seeing Confirmation** | Services | HIGH | Low (email) |
| **Pilot Scope** | Services | HIGH | Medium (1 page) |
| **Stewardship Agreement** | Services | MEDIUM | Medium (2 pages) |
| **Anvil Agreement** | Services | LOW | High (hardware) |
| **CA Project SOW** | CA | HIGH | Medium (2-3 pages) |
| **CA API Agreement** | CA | MEDIUM | Medium |
| **MSA** | Both | LOW | High |

### Minimum Day 1

1. **Seeing Confirmation Email** - "Thanks for booking. Confirming [date/time]. $300 due before session via [payment link]. See you then."

2. **Pilot Scope (1 page):**
   - What we're building
   - What success looks like
   - Timeline (1 week)
   - Price ($3,000 due upfront)
   - What's not included
   - Signature lines

3. **CA Project SOW (2 pages):**
   - Scope of work
   - Deliverables
   - Timeline (4 weeks)
   - Price and payment terms (50% upfront, 50% on delivery)
   - Assumptions
   - Out of scope
   - Signature lines

### Setup Checklist

- [ ] Draft Seeing confirmation email template
- [ ] Draft Pilot scope template
- [ ] Draft CA SOW template
- [ ] Store in `/docs/03_business/legal/templates/`
- [ ] Get one customer to sign before building more

---

## 5. COMMUNICATION

### Email

**Current:** Personal Gmail
**Needed:** Professional email (eventually)

| Option | Cost | Pros | Cons |
|--------|------|------|------|
| **Gmail (personal)** | Free | Works | Looks amateur |
| **Google Workspace** | $6/mo | Professional, custom domain | Monthly cost |
| **Zoho Mail** | Free (1 user) | Custom domain free | Less polished |

**Recommendation:** Use Gmail for now. Set up Google Workspace when you have paying customers and care about perception.

### Scheduling

**Current:** Back-and-forth emails
**Needed:** Self-service booking (especially for Seeing)

| Option | Cost | Pros | Cons |
|--------|------|------|------|
| **Calendly Free** | Free | 1 event type | Limited |
| **Calendly Standard** | $10/mo | Multiple events, reminders | Cost |
| **Cal.com** | Free (self-host) | Open source | Setup time |

**Recommendation:** Calendly Free for now (1 event type = "The Seeing 90-min Session"). Upgrade when you need multiple event types.

### Setup Checklist

- [ ] Set up Calendly account
- [ ] Create "The Seeing" event type (90 min)
- [ ] Set availability
- [ ] Add payment requirement ($300 via Stripe/PayPal)
- [ ] Test booking flow

---

## 6. PROJECT MANAGEMENT

### The Need

Track what you're working on. Manage deliverables for customers.

### Current State

- Claude conversations (not persistent)
- Truth Engine codebase (technical)
- No project tracking

### Options

| Option | Cost | Pros | Cons |
|--------|------|------|------|
| **Notion** | Free | Flexible, good for docs + tasks | Learning curve |
| **Todoist** | Free | Simple tasks | No projects |
| **Linear** | Free (small teams) | Engineering-focused | Overkill |
| **Spreadsheet** | Free | Simple | Limited views |

**Recommendation:** Don't add tools yet. Use:
- Truth Engine docs for documentation
- Simple checklist in Notion or paper for projects
- Add tooling when you have 3+ concurrent projects

---

## 7. DOCUMENT MANAGEMENT

### The Need

Store and find contracts, invoices, deliverables.

### Current State

- Truth Engine codebase (technical docs)
- Documents folder (unsorted)
- No customer folder structure

### Recommended Structure

```
/Users/jeremyserna/Business/
├── Credential_Atlas/
│   └── Customers/
│       └── [Company_Name]/
│           ├── contracts/
│           ├── invoices/
│           ├── deliverables/
│           └── correspondence/
└── Primitive_Engine/
    └── Clients/
        └── [Client_Name]/
            ├── seeing/
            ├── pilot/
            ├── stewardship/
            └── invoices/
```

### Setup Checklist

- [ ] Create folder structure
- [ ] Move legal docs already done ✅
- [ ] Create first customer folder when you have one

---

## 8. TAX PLANNING

### The Need

Don't get surprised by taxes. Set aside money.

### Current State

- Two single-member LLCs (pass-through to personal)
- No estimated tax payments made
- No tax professional

### Key Decisions

**Quarterly Estimated Taxes:**
- Due: April 15, June 15, September 15, January 15
- Required if expecting >$1,000 tax liability
- Safe harbor: Pay 100% of prior year tax (or 110% if income >$150K)

**Set Aside Rule:**
- Set aside 25-30% of every payment received
- Put in Mercury savings account (0842)
- Don't touch until tax time

**S-Corp Election?**
- Consider if net income exceeds ~$40K
- Can save 15.3% self-employment tax on portion
- Requires payroll ($100-200/mo)
- Deadline: March 15 for current year (or file late with reasonable cause)
- **Decision:** Wait until you have consistent revenue

### Tax Professional

**Not urgent but recommended once revenue starts:**
- CPA familiar with single-member LLCs
- Can help with quarterly estimates
- Cost: $500-1,500/year for simple returns

---

## 9. INSURANCE

### The Need

Protect against liability. Required for some contracts.

### Types to Consider

| Type | What It Covers | Need Now? | Cost |
|------|----------------|-----------|------|
| **General Liability** | Property damage, bodily injury | LOW | $300-500/yr |
| **Professional Liability (E&O)** | Errors, negligence, bad advice | MEDIUM | $500-1,500/yr |
| **Cyber Liability** | Data breaches | LOW | $500-1,000/yr |

**Recommendation:**
- Don't buy yet
- Get quotes when first enterprise customer asks for it
- Many small clients won't require it
- Enterprise (State workforce boards) will require $1M+

---

## 10. COMPLIANCE TRACKING

### Annual Requirements

| Entity | Requirement | Due | Status |
|--------|-------------|-----|--------|
| Credential Atlas LLC | CO Periodic Report | December 2026 | Not due |
| Primitive Engine LLC | CO Periodic Report | January 2027 | Not due |
| Personal | Federal Tax Return | April 15, 2027 | Not due |
| Personal | CO State Tax Return | April 15, 2027 | Not due |

### Recurring

| Task | Frequency | Notes |
|------|-----------|-------|
| Bank reconciliation | Monthly | Match Mercury to Wave |
| Invoice follow-up | Weekly | Check unpaid invoices |
| Estimated taxes | Quarterly | If revenue starts |
| Expense categorization | Weekly | Receipt capture |

---

## PRIORITY ACTION LIST

### DO THIS WEEK

| # | Action | Time | Why |
|---|--------|------|-----|
| 1 | Sign up for Wave | 30 min | Accounting + invoicing |
| 2 | Connect Mercury to Wave | 15 min | Auto-import transactions |
| 3 | Create CRM spreadsheet | 30 min | Track prospects |
| 4 | Add Mo Lam + Ashutosh to CRM | 10 min | Pipeline |
| 5 | Set up Calendly | 30 min | Seeing bookings |
| 6 | Draft Seeing confirmation email | 15 min | Ready for first booking |

### DO BEFORE FIRST CUSTOMER

| # | Action | Time | Why |
|---|--------|------|-----|
| 7 | Create CA invoice template | 30 min | Ready to bill |
| 8 | Create Services invoice template | 30 min | Ready to bill |
| 9 | Draft CA SOW template | 1 hr | Contract ready |
| 10 | Draft Pilot scope template | 30 min | Contract ready |
| 11 | Create customer folder structure | 15 min | Organization |

### DO WHEN YOU HAVE REVENUE

| # | Action | Trigger |
|---|--------|---------|
| 12 | Set up 25% tax reserve transfers | First payment received |
| 13 | Find CPA | Revenue > $10K |
| 14 | Get insurance quotes | Enterprise customer asks |
| 15 | Consider S-Corp election | Net income > $40K |

---

## COST SUMMARY

### Day 1 Stack (Free)

| Tool | Function | Cost |
|------|----------|------|
| Mercury | Banking | $0 |
| Wave | Accounting + Invoicing | $0 |
| Google Sheets | CRM | $0 |
| Calendly | Scheduling | $0 |
| Google Docs | Contracts | $0 |
| Gmail | Email | $0 |
| **Total** | | **$0/month** |

### Upgraded Stack (When Revenue Justifies)

| Tool | Function | Cost | Trigger |
|------|----------|------|---------|
| Google Workspace | Professional email | $6/mo | Care about perception |
| Calendly Pro | Multiple event types | $10/mo | Need more booking types |
| Notion | Project management | $10/mo | 3+ concurrent projects |
| Professional liability insurance | Protection | $50-100/mo | Enterprise asks |
| CPA | Tax help | $100-150/mo | Revenue > $10K |
| **Total** | | **$180-280/mo** | |

---

## THE HONEST ASSESSMENT

**What you actually need to operate:**
1. Wave account (free) - accounting + invoicing
2. CRM spreadsheet (free) - track prospects
3. Calendly (free) - book Seeing sessions
4. Contract templates (free) - Google Docs

**What you don't need yet:**
- Fancy CRM (no customers to manage)
- Project management tool (no projects)
- Professional email (Gmail works)
- Insurance (no one asking)
- Bookkeeper (no transactions)

**The trap to avoid:**
Spending weeks setting up "proper operations" instead of sending the email to Mo Lam.

**The rule:**
Set up each system when you need it, not before. The first customer is more important than the perfect stack.

---

## VERIFICATION

Business operations ready when:

1. [ ] Wave account created
2. [ ] Mercury connected to Wave
3. [ ] CRM spreadsheet exists with prospects
4. [ ] Calendly set up for Seeing
5. [ ] Invoice templates created
6. [ ] Basic contract templates exist
7. [ ] Customer folder structure ready
8. [ ] First customer contacted ← **THIS IS THE REAL GATE**

---

*Business operations assessed. $0/month stack defined. Set up Wave and CRM this week. Don't over-engineer—get the first customer.*
