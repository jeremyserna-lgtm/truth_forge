# 3-Month Profitability Plan: Break-Even Strategy

**Date**: January 6, 2026
**Goal**: Break-even in 3 months
**Priority**: Customer Acquisition (Peterson's Pilot) + API Launch
**Budget Constraint**: $1,500/month GCP (CRITICAL: $1,400 mistake = housing loss)

---

## 🎯 EXECUTIVE SUMMARY

**The Path to Profitability:**
- **Month 1**: Secure first customer ($15k-25k) + Launch API foundation
- **Month 2**: 2-3 customers ($30k-50k) + First API subscription ($1.5k-8k/mo)
- **Month 3**: 4-5 customers ($60k-75k) + 2-3 API subscriptions ($3k-15k/mo)
- **Break-Even Target**: $75k-100k in 3 months (covers 3 months costs + buffer)

**Revenue Streams:**
1. Custom Data Projects: $15k-25k each (primary focus)
2. API Subscriptions: $1.5k-8k/month (secondary, scalable)
3. Consulting: $200/hr (fill-in revenue)

---

## 📊 MONTH 1: FOUNDATION + FIRST CUSTOMER (Jan 6 - Feb 5)

### Revenue Goals
- **Target**: $15k-25k (1 custom project)
- **Stretch**: $30k-40k (2 projects)

### Critical Actions

#### 1. Peterson's Pilot (Week 1-2)
**Status**: Tier 1 target - highest probability
**Strategy**: "Rescue" their Credentials dataset

**Action Items:**
- [ ] Research Peterson's current Credentials product status
- [ ] Identify decision maker (likely Data/Product VP)
- [ ] Draft outreach email using business plan template
- [ ] Create pilot proposal: $15k-25k for credential data refresh
- [ ] Schedule discovery call
- [ ] Prepare demo: Show 600k+ records, BigQuery access, API capabilities

**Outreach Template** (from business plan):
```
Subject: Quick question about your credential data

Hi [Name],

I noticed Peterson's Credentials dataset. I'm curious—how are you currently
maintaining and updating the credential-to-institution connections?

I ask because I spent six years at Peterson's building this dataset from scratch,
and I've built a system that can refresh and maintain it at 90% lower cost.

I can deliver a refreshed, connected credential database in 4 weeks. One dataset,
cleaned and maintained, with API access.

Worth a 15-minute call to see if this is relevant?

—Jeremy
Credential Atlas LLC
```

#### 2. API Launch Foundation (Week 2-3)
**Status**: Phase 3 from Master Strategy
**Goal**: Enable self-serve API subscriptions

**Action Items:**
- [ ] Build FastAPI endpoint structure
  - [ ] Authentication layer (API keys)
  - [ ] Rate limiting
  - [ ] Versioning (v1)
  - [ ] Core endpoints:
    - `GET /v1/credentials` - List credentials
    - `GET /v1/credentials/{id}` - Get credential details
    - `GET /v1/institutions` - List institutions
    - `GET /v1/occupations` - List occupations with wage data
- [ ] Deploy to Cloud Run
- [ ] Create API documentation (OpenAPI/Swagger)
- [ ] Set up API key management
- [ ] Create pricing tiers:
  - Starter: $1,500/mo (10k requests/month)
  - Professional: $4,000/mo (100k requests/month)
  - Enterprise: $8,000/mo (unlimited)

#### 3. Cost Tracking Dashboard (Week 1)
**Status**: CRITICAL - Must track every dollar
**Goal**: Real-time visibility into GCP spend

**Action Items:**
- [ ] Set up GCP billing export to BigQuery
- [ ] Create cost tracking dashboard:
  - Daily spend vs $50/day budget
  - Service breakdown (BigQuery, Cloud Run, Storage)
  - Alert at $1,000/month (67% of budget)
  - Alert at $1,400/month (93% of budget) - CRITICAL THRESHOLD
- [ ] Integrate with `governance.budget_tracking` table
- [ ] Create daily cost report script
- [ ] Set up email/Slack alerts for budget thresholds

#### 4. Revenue Tracking System (Week 1)
**Goal**: Track pipeline and closed deals

**Action Items:**
- [ ] Create revenue tracking table in BigQuery:
  - `revenue.opportunities` (pipeline)
  - `revenue.deals` (closed)
  - `revenue.subscriptions` (recurring)
- [ ] Create simple dashboard:
  - Pipeline value
  - Closed deals this month
  - MRR (Monthly Recurring Revenue)
  - Break-even progress

#### 5. Direct Outreach (Week 2-4)
**Target**: 10 high-potential companies from business plan

**Action Items:**
- [ ] Research each company's credential data needs
- [ ] Personalize outreach emails
- [ ] Track responses in revenue tracking system
- [ ] Follow up on non-responses (Week 3)
- [ ] Schedule discovery calls

**Target Companies** (from business plan):
1. Peterson's (Tier 1)
2. Niche (Tier 2 - EdTech)
3. Guild Education (Tier 2 - EdTech)
4. SchooLinks (Tier 2 - EdTech)
5. Credential Engine (Tier 4 - Partner)
6. Lightcast (Tier 4 - Partner)
7. Colorado Workforce Board (Tier 3 - State)
8. Florida Workforce Board (Tier 3 - State)
9. Indiana Workforce Board (Tier 3 - State)
10. [Add 1 more from research]

### Success Metrics (Month 1)
- [ ] 1 signed customer ($15k-25k)
- [ ] API deployed and documented
- [ ] Cost tracking dashboard live
- [ ] 10 companies contacted
- [ ] 3+ discovery calls scheduled
- [ ] GCP spend < $1,200/month

---

## 📈 MONTH 2: SCALE + FIRST SUBSCRIPTION (Feb 6 - Mar 5)

### Revenue Goals
- **Target**: $30k-50k (2-3 custom projects)
- **Stretch**: $60k-75k (3-4 projects + 1 API subscription)

### Critical Actions

#### 1. Deliver First Project (Week 1-2)
**Goal**: Exceed expectations, get referral

**Action Items:**
- [ ] Execute custom project with excellence
- [ ] Document process for repeatability
- [ ] Request testimonial/case study
- [ ] Ask for referral to 2-3 contacts

#### 2. Close 2-3 More Projects (Week 2-4)
**Goal**: Build momentum

**Action Items:**
- [ ] Follow up on Month 1 pipeline
- [ ] Convert discovery calls to proposals
- [ ] Close 2-3 deals at $15k-25k each
- [ ] Start delivery immediately

#### 3. Land First API Subscription (Week 3-4)
**Goal**: Recurring revenue foundation

**Action Items:**
- [ ] Identify companies that need ongoing data access
- [ ] Offer API trial (14 days free)
- [ ] Convert trial to paid subscription
- [ ] Target: 1 subscription at $1.5k-4k/mo

#### 4. Optimize Costs (Ongoing)
**Goal**: Stay under $1,200/month

**Action Items:**
- [ ] Review BigQuery query costs
- [ ] Optimize expensive queries
- [ ] Set up query cost alerts
- [ ] Archive old data to cheaper storage
- [ ] Right-size Cloud Run instances

### Success Metrics (Month 2)
- [ ] 2-3 customers signed ($30k-50k)
- [ ] 1 API subscription ($1.5k-4k/mo MRR)
- [ ] 1 project delivered successfully
- [ ] 1 testimonial/case study
- [ ] GCP spend < $1,200/month
- [ ] Pipeline value > $100k

---

## 🚀 MONTH 3: BREAK-EVEN (Mar 6 - Apr 5)

### Revenue Goals
- **Target**: $60k-75k (4-5 projects total + 2-3 subscriptions)
- **Break-Even**: $75k+ (covers 3 months costs + buffer)

### Critical Actions

#### 1. Deliver Projects (Ongoing)
**Goal**: Maintain quality, build reputation

**Action Items:**
- [ ] Deliver Month 2 projects
- [ ] Maintain 100% customer satisfaction
- [ ] Collect testimonials
- [ ] Document success stories

#### 2. Scale API Subscriptions (Week 2-4)
**Goal**: Build recurring revenue

**Action Items:**
- [ ] Convert 2-3 more API trials to paid
- [ ] Target: $3k-15k/mo total MRR
- [ ] Create API usage dashboard for customers
- [ ] Provide customer support

#### 3. Productize Custom Projects (Week 3-4)
**Goal**: Reduce delivery time, increase margins

**Action Items:**
- [ ] Create project templates
- [ ] Automate common tasks
- [ ] Reduce delivery time from 4 weeks to 2-3 weeks
- [ ] Increase capacity for more projects

#### 4. Prepare for Growth (Week 4)
**Goal**: Set up Month 4+ for scale

**Action Items:**
- [ ] Apply for Google Cloud for Startups credits ($350k)
- [ ] Apply for Colorado Advanced Industries Grant ($250k)
- [ ] Build landing page (credentialatlas.com)
- [ ] Create content marketing strategy

### Success Metrics (Month 3)
- [ ] 4-5 total customers ($60k-75k revenue)
- [ ] 2-3 API subscriptions ($3k-15k/mo MRR)
- [ ] **BREAK-EVEN ACHIEVED** ($75k+ total)
- [ ] GCP spend < $1,200/month
- [ ] Pipeline value > $150k
- [ ] 3+ testimonials/case studies

---

## 💰 FINANCIAL PROJECTIONS

### 3-Month Revenue Projection

| Month | Custom Projects | API Subscriptions | Consulting | Total Revenue |
|-------|----------------|-------------------|------------|---------------|
| Month 1 | $20k (1 project) | $0 | $2k (10 hrs) | **$22k** |
| Month 2 | $40k (2 projects) | $2k (1 sub) | $4k (20 hrs) | **$46k** |
| Month 3 | $50k (2-3 projects) | $6k (2-3 subs) | $4k (20 hrs) | **$60k** |
| **TOTAL** | **$110k** | **$8k** | **$10k** | **$128k** |

**Conservative Estimate**: $75k-100k (accounts for delays, rejections)
**Stretch Goal**: $128k+ (everything goes perfectly)

### 3-Month Cost Projection

| Category | Monthly | 3-Month Total |
|----------|---------|---------------|
| GCP/Infrastructure | $1,200 | $3,600 |
| AI APIs (Gemini/Claude) | $750 | $2,250 |
| Software/Tools | $300 | $900 |
| Legal/Accounting | $250 | $750 |
| Marketing/Sales | $500 | $1,500 |
| **Total Monthly** | **$3,000** | **$9,000** |

**Break-Even Point**: $9k costs + $1.4k safety buffer = **$10.4k minimum**
**Target**: $75k-100k revenue = **$65k-90k profit margin**

---

## 🚨 CRITICAL CONSTRAINTS & PROTECTIONS

### Cost Protection (MANDATORY)
- **$1,400 mistake = housing loss** - This is non-negotiable
- **Daily budget**: $50/day GCP ($1,500/month)
- **Alert thresholds**:
  - $1,000/month (67%) - Warning
  - $1,400/month (93%) - CRITICAL - Block new operations
  - $1,500/month (100%) - HARD STOP
- **Cost tracking**: Every operation must log cost before execution
- **BigQuery protection**: All queries must estimate cost before running

### Revenue Protection
- **Payment terms**: 50% upfront, 50% on delivery (custom projects)
- **API subscriptions**: Monthly billing, paid in advance
- **Contracts**: Use standard MSA + SOW for all projects
- **Collections**: Follow up on invoices immediately

### Quality Protection
- **Don't overpromise**: Under-promise, over-deliver
- **Set expectations**: 4-week delivery, not 2 weeks
- **Communication**: Weekly status updates to customers
- **Documentation**: Every project fully documented

---

## 📋 WEEKLY RITUALS

### Monday: Pipeline Review
- Review all opportunities
- Update revenue tracking
- Plan outreach for week
- Check cost dashboard

### Wednesday: Customer Check-ins
- Status updates to active projects
- Follow up on proposals
- Respond to inquiries

### Friday: Financial Review
- Review week's costs
- Review week's revenue
- Update break-even progress
- Plan next week's priorities

---

## 🎯 SUCCESS CRITERIA

### Month 1 Success
- ✅ 1 customer signed ($15k-25k)
- ✅ API deployed
- ✅ Cost tracking live
- ✅ 10 companies contacted

### Month 2 Success
- ✅ 2-3 customers signed ($30k-50k)
- ✅ 1 API subscription ($1.5k-4k/mo)
- ✅ 1 project delivered
- ✅ Pipeline > $100k

### Month 3 Success (BREAK-EVEN)
- ✅ 4-5 customers ($60k-75k)
- ✅ 2-3 API subscriptions ($3k-15k/mo)
- ✅ **$75k+ total revenue**
- ✅ **Break-even achieved**

---

## 🚀 NEXT STEPS (START TODAY)

1. **Set up cost tracking** (2 hours)
   - GCP billing export
   - Cost dashboard
   - Alert thresholds

2. **Research Peterson's** (1 hour)
   - Find decision maker
   - Understand current product status
   - Draft outreach email

3. **Create revenue tracking** (1 hour)
   - BigQuery tables
   - Simple dashboard
   - Pipeline tracking

4. **Draft Peterson's proposal** (2 hours)
   - Pilot scope
   - Pricing ($15k-25k)
   - Timeline (4 weeks)
   - Value proposition

5. **Start API development** (4 hours)
   - FastAPI structure
   - Authentication
   - Core endpoints
   - Documentation

**Total Time Investment**: 10 hours (1-2 days)
**Expected ROI**: $15k-25k first customer within 2-3 weeks

---

*The path to profitability is clear. Now we execute.*
*Every dollar tracked. Every opportunity pursued. Every customer delighted.*
