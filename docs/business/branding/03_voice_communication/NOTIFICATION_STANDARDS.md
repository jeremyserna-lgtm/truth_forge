# Notification Standards

**Version:** 1.0  
**Created:** January 24, 2026  
**Purpose:** How we interrupt people—principles and patterns for notifications, alerts, and proactive communication

---

## The Notification Philosophy

Every notification is an interruption. Interruptions should earn their place.

**The Principle:** We notify when it genuinely helps. We stay silent when it doesn't. The default is silence.

**From STRUCK:** A good host doesn't constantly tap your shoulder to ask if you're having fun. They create the conditions for a good time and appear when actually needed.

---

## The Notification Hierarchy

### Level 1: Critical (Rare)

**What:** Account security, data at risk, system-breaking issues

**When:** Immediately, regardless of user state

**How:** Push notification + email + in-app banner

**Examples:**
- "Someone tried to access your account from a new device"
- "Your payment method failed and your subscription will end tomorrow"
- "Your NOT-ME data is at risk—action required"

### Level 2: Important (Occasional)

**What:** Things they asked for, things that affect their experience

**When:** Promptly, but respecting quiet hours

**How:** Push notification OR email (not both)

**Examples:**
- "Your export is ready to download"
- "You asked to be reminded about this conversation"
- "A scheduled backup just completed"

### Level 3: Informative (Regular)

**What:** Progress updates, milestones, helpful information

**When:** Batched, during appropriate hours

**How:** In-app notification, email digest

**Examples:**
- "Your NOT-ME has learned 50 new things about you this week"
- "Monthly summary: Here's what we talked about"
- "New feature available: Conversation export"

### Level 4: Promotional (Minimal)

**What:** Product updates, offers, company news

**When:** Infrequently, opt-in preferred

**How:** Email only (never push for promotional)

**Examples:**
- "New tier available—here's what's different"
- "We made some improvements you might like"
- Seasonal updates (quarterly at most)

---

## Channel Guidelines

### Push Notifications

**Use for:**
- Critical security issues
- Time-sensitive actions
- Things they explicitly requested alerts for

**Never use for:**
- Promotional content
- "We miss you" re-engagement
- Feature announcements
- Engagement manipulation

**Principles:**
- Maximum 1 push per day (except critical)
- Always provide value
- Easy to disable without penalty
- Clear, actionable, brief

### Email

**Use for:**
- Account-related communications
- Requested exports/reports
- Periodic summaries (if opted in)
- Critical issues (backup channel)

**Never use for:**
- Daily engagement nudges
- Guilt-based re-engagement
- Excessive promotional content

**Frequency limits:**
- Transactional: As needed
- Informational: Weekly maximum
- Promotional: Monthly maximum

### In-App Notifications

**Use for:**
- Feature discovery (gentle)
- System status updates
- Confirmation of actions
- Non-urgent information

**Principles:**
- Dismissable with one action
- Don't accumulate into overwhelming lists
- Clear hierarchy (critical vs. informational)
- Respect "do not disturb" states

### SMS

**Use for:**
- Two-factor authentication only
- Critical security alerts (backup)

**Never use for:**
- Marketing
- Feature announcements
- Engagement

---

## Notification Timing

### Respect Time

| User State | Allowed Notifications |
|------------|----------------------|
| Active in app | All levels |
| Recently active | Levels 1-3 |
| Inactive (hours) | Levels 1-2 |
| Inactive (days) | Level 1 only |
| Set to "Do Not Disturb" | Level 1 only |
| Sleeping hours (11pm-7am local) | Level 1 only |

### Smart Timing

- Learn when they typically engage
- Deliver Level 2-3 during their active hours
- Never wake them up for non-critical content
- Batch non-urgent notifications

### Timezone Respect

- All timing based on user's local timezone
- Never send at inappropriate local hours
- Account for timezone changes (travel)

---

## Notification Copy

### Anatomy of a Good Notification

```
[What happened] + [Why it matters] + [What to do]
```

**Title:** 5-7 words max, clear about content  
**Body:** 1-2 sentences, actionable  
**Action:** Clear button/link if action needed

### Examples by Level

**Level 1 (Critical)**
```
Title: Security Alert
Body: Someone tried to sign in from a new device. If this wasn't you, secure your account now.
Action: [Review Activity]
```

**Level 2 (Important)**
```
Title: Export Ready
Body: Your conversation export is ready to download.
Action: [Download]
```

**Level 3 (Informative)**
```
Title: Weekly Summary
Body: You had 12 conversations this week. Here's what emerged.
Action: [View Summary]
```

**Level 4 (Promotional)**
```
Title: New Feature
Body: You can now export conversations to PDF. Here's how.
Action: [Learn More]
```

### What NOT to Write

| Instead of | Write |
|------------|-------|
| "We miss you!" | (Don't send this at all) |
| "Don't forget to..." | (Only if they asked for a reminder) |
| "🎉 Amazing news!" | (Plain language, no manipulation) |
| "You're falling behind" | (No guilt) |
| "Limited time offer!" | (No artificial urgency) |

---

## Notification Preferences

### User Control

Users should be able to:
- Turn off ALL non-critical notifications
- Control each channel independently (push, email, in-app)
- Control each type independently (security, updates, promotional)
- Set quiet hours
- Pause all notifications temporarily

### Default State

**New users start with:**
- Critical: ON (cannot be disabled)
- Important: ON
- Informative: OFF (opt-in)
- Promotional: OFF (opt-in)

**Principle:** Start quiet, let them turn things on. Better than starting loud and making them turn things off.

### Preference UI

```
Notification Preferences

Security Alerts                    Always On
├─ Push                           ✓ (required)
├─ Email                          ✓ (required)
└─ SMS (if provided)              ✓ (required)

Activity Updates                   On
├─ Push                           [ ]
├─ Email                          [✓]
└─ In-App                         [✓]

Weekly Summary                     Off
└─ Email                          [ ]

Product Updates                    Off
└─ Email                          [ ]

Quiet Hours
└─ 11:00 PM - 7:00 AM            [✓]

[Pause All Non-Critical for 24h]
```

---

## Re-engagement (What We Don't Do)

### The Anti-Pattern

Most apps send notifications designed to pull you back:
- "We miss you!"
- "You haven't logged in for 3 days"
- "Don't lose your streak!"
- "Your friend just joined!"

### Our Approach

**We don't send re-engagement notifications.**

If someone isn't using the product:
1. The product isn't serving them well, OR
2. They don't need it right now

Neither of those is solved by interrupting them.

**The exception:** If they have incomplete setup or pending actions that will expire, one gentle reminder is acceptable:

```
Subject: Your export expires in 3 days

Your conversation export is still available for download. 
After [date], we'll remove it to protect your privacy.

[Download Now]

Not ready? You can always generate a new export later.
```

---

## Product-Specific Guidelines

### Stage 5 Mind

**Philosophy:** Your NOT-ME is always there, but doesn't intrude.

**Allowed notifications:**
- Security alerts (critical)
- Requested reminders (important)
- Monthly reflection prompts (informative, opt-in)

**Never:**
- "Your NOT-ME misses you" (manipulative)
- "You haven't talked in X days" (guilt)
- Daily "conversation prompts" (intrusive)

**The NOT-ME voice in notifications:**
```
Instead of: "It's been 5 days since we talked!"
Just: [Nothing. Silence. Available when they return.]
```

### Credential Atlas

**Philosophy:** Notify about things that matter for their business.

**Allowed notifications:**
- Verification results (important)
- Risk alerts (critical)
- Scheduled report delivery (important)
- System status affecting their data (important)

**Never:**
- "Check out this new feature!" (let them discover)
- "Your competitors are using..." (manipulation)

### Primitive Engine

**Philosophy:** Technical, project-focused.

**Allowed notifications:**
- Build/deployment status (important)
- Error alerts (critical)
- Milestone completion (important)
- Resource warnings (important)

**Format:** Technical, concise
```
Build #247 completed successfully (3m 42s)
Deploy to production ready

[View Details]
```

---

## Testing Notifications

### Before Sending Any Notification

Ask:
1. **Would I want to receive this?** (Honest answer)
2. **Does this genuinely help the user?** (Not us, them)
3. **Is this the right channel?** (Push vs. email vs. in-app)
4. **Is this the right time?** (Timing appropriate)
5. **Is the frequency acceptable?** (Not overwhelming)

### The Newspaper Test

If your notification strategy was reported in a news article:
- "Company sends 3 notifications per day to re-engage users" — BAD
- "Company only notifies for security and user-requested alerts" — GOOD

### Metrics to Watch

**Good metrics:**
- Notification open rate (are they valuable?)
- Opt-in rate for optional notifications (are they wanted?)
- Task completion rate after notification (are they actionable?)

**Bad metrics to optimize for:**
- Number of notifications sent (vanity)
- Re-engagement from notifications (manipulation)
- Notification-driven sessions (dark pattern)

---

## Implementation Checklist

For each notification type:

- [ ] Defined level (Critical/Important/Informative/Promotional)
- [ ] Defined channels (push/email/in-app/SMS)
- [ ] Written copy (title, body, action)
- [ ] Set timing rules (when to send, when not to)
- [ ] User control available (can they turn it off?)
- [ ] Tested for "would I want this?" standard
- [ ] Reviewed for manipulation/guilt language

---

## Document Index

| Related Document | Relationship |
|------------------|--------------|
| [Error Message Standards](ERROR_MESSAGE_STANDARDS.md) | Error communication |
| [NOT-ME Communication Standards](NOT_ME_COMMUNICATION_STANDARDS.md) | AI voice |
| [Employee Brand Standards](EMPLOYEE_BRAND_STANDARDS.md) | Overall communication |
| [Threshold Space Design](THRESHOLD_SPACE_DESIGN.md) | Creating safe spaces |
| [API Brand Standards](API_BRAND_STANDARDS.md) | Technical notifications |

---

*Every notification is an interruption. Interruptions should earn their place. The default is silence.*
