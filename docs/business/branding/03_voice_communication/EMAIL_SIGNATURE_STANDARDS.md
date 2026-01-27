# Email Signature Standards

**Version:** 1.0  
**Created:** January 24, 2026  
**Scope:** All Truth Engine family brands

---

## Core Principles

1. **Professional but warm** — Not corporate sterile
2. **Consistent across brands** — Same structure, brand-specific colors
3. **Functional** — Essential information only
4. **Mobile-friendly** — Readable on small screens
5. **Accessible** — Plain text fallback, real text (not images)

---

## Standard Signature Format

### Primary Format (Recommended)

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Jeremy Serna
Founder & Architect

Truth Engine · The Source of All Systems
jeremy@truthengine.co · +1 (XXX) XXX-XXXX

truthengine.com
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### Minimal Format (Internal/Quick Replies)

```
Jeremy Serna · Truth Engine
jeremy@truthengine.co
```

### Formal Format (External/New Contacts)

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Jeremy Serna
Founder & Architect
Truth Engine LLC

Email: jeremy@truthengine.co
Phone: +1 (XXX) XXX-XXXX
Web: truthengine.com

The Source of All Systems
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## Brand-Specific Signatures

### Truth Engine

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[Name]
[Title]

Truth Engine · The Source of All Systems
[email] · [phone]

truthengine.com
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### Primitive Engine

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[Name]
[Title]

Primitive Engine · We Build What Lasts
[email] · [phone]

primitive-engine.com
A Truth Engine Company
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### Credential Atlas

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[Name]
[Title]

Credential Atlas · See What Others Can't
[email] · [phone]

credential-atlas.com
A Truth Engine Company
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### Stage 5 Mind

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[Name]
[Title]

Stage 5 Mind · Who Do You Need?
[email] · [phone]

stage5mind.com
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## HTML Signature (Styled)

### Template

```html
<table cellpadding="0" cellspacing="0" style="font-family: Arial, sans-serif; font-size: 14px; color: #0D0D0D; line-height: 1.4;">
  <tr>
    <td style="padding-bottom: 8px; border-bottom: 1px solid #B5B5B5;">
      <strong style="font-size: 16px;">Jeremy Serna</strong><br>
      <span style="color: #4A4A4A; font-size: 13px;">Founder & Architect</span>
    </td>
  </tr>
  <tr>
    <td style="padding-top: 8px;">
      <span style="color: #0D0D0D;">Truth Engine</span> 
      <span style="color: #888888;">·</span> 
      <span style="color: #4A4A4A; font-style: italic;">The Source of All Systems</span><br>
      <a href="mailto:jeremy@truthengine.co" style="color: #0D0D0D; text-decoration: none;">jeremy@truthengine.co</a>
      <span style="color: #888888;">·</span>
      <span style="color: #4A4A4A;">+1 (XXX) XXX-XXXX</span>
    </td>
  </tr>
  <tr>
    <td style="padding-top: 8px;">
      <a href="https://truthengine.com" style="color: #4A6FA5; text-decoration: none;">truthengine.com</a>
    </td>
  </tr>
</table>
```

### Dark Mode Variant

For clients primarily using dark mode email clients:

```html
<table cellpadding="0" cellspacing="0" style="font-family: Arial, sans-serif; font-size: 14px; color: #F5F0E6; line-height: 1.4;">
  <!-- Same structure, inverted colors -->
</table>
```

---

## Logo in Signature

### When to Include Logo

- **Yes:** External communications, new relationships, formal contexts
- **No:** Internal communications, reply chains, quick exchanges

### Logo Specifications

If including logo:
- Format: PNG with transparency
- Size: Maximum 100px wide
- Position: Left of name OR above signature block
- Alt text: "Truth Engine Logo"

### Logo Placement

```
[LOGO 80px]

Jeremy Serna
Founder & Architect
...
```

---

## Typography (If Email Client Supports)

### Preferred Fonts (Web-Safe Fallbacks)

| Element | Primary | Fallback |
|---------|---------|----------|
| Name | Georgia | Times New Roman, serif |
| Title | Arial | Helvetica, sans-serif |
| Body | Arial | Helvetica, sans-serif |
| Links | Arial | Helvetica, sans-serif |

**Note:** We cannot use Instrument Serif or JetBrains Mono in email signatures as they are not universally installed. Use web-safe equivalents.

---

## What NOT to Include

- ❌ Inspirational quotes
- ❌ Legal disclaimers (unless required)
- ❌ Multiple social media links
- ❌ Animated GIFs
- ❌ Large images/banners
- ❌ Calendly or scheduling links (use in email body instead)
- ❌ Pronouns (unless specifically requested)
- ❌ Lengthy titles
- ❌ Multiple phone numbers

---

## Optional Elements

### When Appropriate

| Element | When to Include |
|---------|-----------------|
| LinkedIn | Networking-focused roles |
| Calendar link | Sales/customer-facing roles |
| Physical address | Legal requirements only |
| Pronouns | If requested by individual |
| Certification badges | If relevant to conversation |

### LinkedIn Format (If Included)

```
linkedin.com/in/jeremyserna
```

NOT:
- Full URL with tracking
- "Connect with me on LinkedIn"
- LinkedIn logo image

---

## Email Address Conventions

### Format by Role

| Role | Email Format |
|------|--------------|
| Founder | jeremy@truthengine.co |
| General inquiries | hello@truthengine.co |
| Support | support@truthengine.co |
| Sales | sales@truthengine.co |

### Brand-Specific Domains

| Brand | Primary Domain |
|-------|----------------|
| Truth Engine | @truthengine.co |
| Primitive Engine | @primitive-engine.com |
| Credential Atlas | @credential-atlas.com |
| Stage 5 Mind | @stage5mind.com |

---

## Setup Instructions

### Gmail

1. Go to Settings → See all settings
2. Scroll to "Signature"
3. Click "Create new"
4. Paste formatted signature
5. Set as default for compose and reply

### Apple Mail

1. Go to Mail → Preferences → Signatures
2. Select account
3. Click + to add new signature
4. Paste signature
5. Uncheck "Always match my default message font"

### Outlook

1. Go to File → Options → Mail → Signatures
2. Click "New" to create signature
3. Paste signature
4. Set for new messages and replies

---

## Mobile Signature

### Short Format for Mobile

```
Jeremy Serna
Truth Engine
truthengine.com

Sent from mobile
```

### iOS Setup

1. Settings → Mail → Signature
2. Select "Per Account" if multiple accounts
3. Enter mobile signature

---

## Signature Audit Checklist

Quarterly, verify:

- [ ] Name spelled correctly
- [ ] Title current
- [ ] Phone number accurate
- [ ] Email address correct
- [ ] Website URL working
- [ ] Tagline matches current brand
- [ ] No broken images
- [ ] Mobile signature matches desktop tone

---

*Your signature is your handshake. Make it firm, warm, and memorable.*
