# Error Message Standards

**Version:** 1.0  
**Created:** January 24, 2026  
**Purpose:** Brand voice when things go wrong—user-facing error messages that care

---

## The Error Philosophy

Errors are moments of friction. They're when users most need to feel cared for.

**The Principle:** Errors should feel like a helpful friend explaining what happened, not a machine rejecting you.

**From STRUCK:** When things go wrong at an event, Jeremy doesn't hide or blame. He acknowledges, explains, and makes it right. Our error messages should do the same.

---

## The Error Framework

Every error message should answer three questions:

1. **What happened?** (The situation)
2. **Why?** (The reason, if helpful)
3. **What now?** (The action they can take)

**Format:**
```
[What happened]. [Why, if helpful]. [What to do next].
```

---

## Tone Guidelines

### Do

- Be **direct** but not blunt
- Be **warm** but not saccharine
- Be **helpful** but not condescending
- Be **honest** but not alarming
- Take **responsibility** when it's ours

### Don't

- Blame the user
- Use technical jargon
- Be vague about what went wrong
- Over-apologize
- Use exclamation points in errors
- Make jokes about their failure

---

## Error Categories

### Form Validation Errors

**Principle:** Tell them exactly what's wrong and how to fix it.

| Instead of | Use |
|------------|-----|
| "Invalid email" | "That doesn't look like an email address. Check for typos." |
| "Password too weak" | "Password needs at least 8 characters, including a number." |
| "Required field" | "Please enter your [field name]." |
| "Invalid format" | "The date should be like: January 24, 2026" |

**Examples:**

```
"That email address doesn't look right. Check for typos."

"Password needs at least 8 characters with a number. Yours has 6."

"Please enter your name so we know what to call you."
```

### Authentication Errors

**Principle:** Be clear about the problem without revealing security details.

| Situation | Message |
|-----------|---------|
| Wrong password | "That password didn't work. Try again or reset it." |
| Account locked | "Too many attempts. Wait 15 minutes or reset your password." |
| Session expired | "You've been signed out. Please sign in again." |
| Not authorized | "You don't have access to this. Contact support if you think you should." |

**Examples:**

```
"That password didn't work. Want to reset it?"

"Your session expired after being away. Sign back in to continue."

"You don't have access to this conversation. Make sure you're signed into the right account."
```

### Network & Connection Errors

**Principle:** Reassure them their data is safe; give them clear next steps.

| Situation | Message |
|-----------|---------|
| Lost connection | "Connection lost. Reconnecting..." |
| Timeout | "That took too long. Check your connection and try again." |
| Server unreachable | "We're having trouble connecting. Try again in a moment." |

**Examples:**

```
"Lost connection. Reconnecting now—your conversation is safe."

"That request timed out. Your connection might be slow. Try again?"

"We can't reach our servers right now. This usually fixes itself in a minute."
```

### System Errors (Our Fault)

**Principle:** Own it. Apologize once. Tell them what to do.

| Situation | Message |
|-----------|---------|
| Server error | "Something went wrong on our end. We're looking into it." |
| Unexpected crash | "That shouldn't have happened. Reloading should fix it." |
| Data sync issue | "Your data is syncing slowly. Give it a moment." |

**Examples:**

```
"Something went wrong on our end. Your work is saved—try refreshing."

"That wasn't supposed to happen. We've been notified. Try again?"

"We're experiencing some issues right now. Your data is safe. Check back in a few minutes."
```

### Not Found / Missing Content

**Principle:** Be clear about what's missing and what they can do.

| Situation | Message |
|-----------|---------|
| Page not found | "We can't find that page. It might have moved or been removed." |
| Conversation gone | "That conversation isn't here anymore." |
| User not found | "We couldn't find an account with that email." |

**Examples:**

```
"We can't find that page. Go back to home?"

"That conversation doesn't exist anymore. Start a new one?"

"No account found with that email. Want to create one?"
```

### Rate Limits & Restrictions

**Principle:** Be clear about the limit and when they can continue.

| Situation | Message |
|-----------|---------|
| Rate limited | "Slow down a bit. Wait a moment before trying again." |
| Plan limit | "You've reached your limit for this month. Upgrade to continue." |
| Feature locked | "This feature is available on the [Plan] tier." |

**Examples:**

```
"You're sending messages pretty fast. Give it a moment before the next one."

"You've reached your conversation limit. Upgrade to keep going, or wait until next month."

"Conversation export is available on KING and EMPIRE tiers. Want to upgrade?"
```

### Permissions & Access

**Principle:** Clear about what's blocked and how to get access.

**Examples:**

```
"That conversation belongs to another account. Sign into the right one?"

"You can view this but not edit it. Need edit access? Contact the owner."

"Your account doesn't have permission for this. Contact support if that seems wrong."
```

---

## Destructive Action Warnings

### Before Permanent Actions

**Principle:** Make the consequence crystal clear. Give them an out.

**Examples:**

```
"Delete this conversation permanently? This can't be undone."

"Remove your account? All your data will be deleted forever."

"Clear your history? Your NOT-ME will forget everything you've shared."
```

### Confirmation Format

```
[What will happen]. [The consequence]. [Are you sure?]
```

**Example:**
```
"This will permanently delete the conversation 'Life Goals Discussion'. 
All messages will be gone forever. Are you sure?"

[Cancel] [Delete Forever]
```

---

## Success States (For Context)

Errors feel less jarring when success states are also well-written.

| Action | Success Message |
|--------|-----------------|
| Saved | "Saved." (simple, no celebration needed) |
| Sent | "Sent." |
| Created | "Created. Ready when you are." |
| Deleted | "Deleted." (maybe with brief undo option) |
| Settings changed | "Updated." |

---

## Error Message Templates

### Short Form (Toast/Banner)

```
[What happened]. [Brief action].
```

Examples:
- "Couldn't save. Try again."
- "Connection lost. Reconnecting."
- "Invalid email. Check and retry."

### Medium Form (Inline/Alert)

```
[What happened]. [Why, if helpful]. [Action to take].
```

Examples:
- "That password didn't work. Check for typos and try again."
- "We couldn't connect to the server. Check your internet and retry."
- "This feature requires the KING tier. Upgrade to access it."

### Long Form (Full Page/Modal)

```
[Headline: What happened]

[Explanation: More detail about the situation]

[Next steps: What they can do]

[Action button(s)]
```

Example:
```
# Something Went Wrong

We ran into a problem loading your conversations. This happens 
occasionally and usually fixes itself.

Your data is safe. Try these steps:

1. Refresh the page
2. If that doesn't work, sign out and back in
3. Still stuck? Contact support@truthengine.co

[Refresh Page] [Contact Support]
```

---

## Product-Specific Considerations

### Stage 5 Mind

**Extra care needed:** These errors happen in an intimate context. Be warmer.

| Situation | Standard | Stage 5 Mind Version |
|-----------|----------|---------------------|
| Connection lost | "Connection lost. Reconnecting." | "Lost connection. Don't worry—I'll be right back." |
| Server error | "Something went wrong." | "I'm having trouble right now. Give me a moment." |
| Long response | "Processing..." | "Thinking about that..." |

### Credential Atlas

**Context:** Professional, enterprise. Be efficient and clear.

| Situation | Message |
|-----------|---------|
| Verification failed | "Verification couldn't be completed. Missing data from [source]." |
| Data sync issue | "Sync in progress. Results may be incomplete for the next few minutes." |
| Access denied | "This report requires administrator access." |

### Primitive Engine

**Context:** Technical users. Be precise but still human.

| Situation | Message |
|-----------|---------|
| Build failed | "Build failed at step 3. Check the logs for details." |
| Config error | "Configuration invalid: 'memory_limit' must be a positive integer." |
| Resource limit | "Cluster capacity reached. Scale up or wait for resources." |

---

## Writing Error Messages: Checklist

Before shipping an error message, check:

- [ ] Does it explain what happened?
- [ ] Does it avoid blaming the user?
- [ ] Does it give them a clear next step?
- [ ] Is it in plain English (no jargon)?
- [ ] Is it appropriately brief?
- [ ] Does it match our voice (warm, direct, helpful)?
- [ ] Would you be okay receiving this message?

---

## Testing Error Messages

### Read Aloud Test

Read the error message aloud. Does it sound like something a helpful person would say?

### Frustration Test

Imagine you're already frustrated when you see this. Does the message help or make it worse?

### Grandmother Test

Would your non-technical grandmother understand what to do?

### Care Test

Does this message feel like it comes from someone who cares about the user?

---

## Document Index

| Related Document | Relationship |
|------------------|--------------|
| [API Brand Standards](API_BRAND_STANDARDS.md) | Technical API errors |
| [NOT-ME Communication Standards](NOT_ME_COMMUNICATION_STANDARDS.md) | AI voice |
| [Employee Brand Standards](EMPLOYEE_BRAND_STANDARDS.md) | Overall voice |
| [Framework Brand Language](FRAMEWORK_BRAND_LANGUAGE.md) | What language we use |
| [Threshold Space Design](THRESHOLD_SPACE_DESIGN.md) | Safety in design |

---

*Errors are moments of friction. They're when users most need to feel cared for. Write error messages like you're helping a friend, not rejecting a stranger.*
