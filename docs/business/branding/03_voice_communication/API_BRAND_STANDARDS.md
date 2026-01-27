# API Brand Standards

**Version:** 1.0  
**Created:** January 24, 2026  
**Purpose:** How the API feels—brand voice and experience in technical interfaces

---

## The API Philosophy

An API is a conversation with code. It should feel like Truth Engine.

**The Principle:** Even technical interfaces carry brand. Every error message, every response structure, every piece of documentation is a brand touchpoint.

Developers who use our API should feel:
- **Respected** — We don't waste their time
- **Informed** — Clear, predictable behavior
- **Supported** — When things go wrong, we help
- **Sovereign** — It's their data, their control

---

## Naming Conventions

### Endpoint Naming

**Philosophy:** Clear, predictable, honest.

**Patterns:**

| Action | Pattern | Example |
|--------|---------|---------|
| Create | `POST /resource` | `POST /conversations` |
| Read one | `GET /resource/{id}` | `GET /conversations/123` |
| Read many | `GET /resources` | `GET /conversations` |
| Update | `PUT /resource/{id}` | `PUT /conversations/123` |
| Delete | `DELETE /resource/{id}` | `DELETE /conversations/123` |
| Action | `POST /resource/{id}/action` | `POST /conversations/123/analyze` |

**Naming Rules:**
- Lowercase, hyphenated: `/user-preferences` not `/userPreferences`
- Plural for collections: `/conversations` not `/conversation`
- Nouns, not verbs: `/analyses` not `/analyze` (except actions)
- Honest about what it does: `/credential-verification` not `/check`

**Avoid:**
- Cute names
- Abbreviations that aren't obvious
- Internal jargon
- Versioning in URLs when possible (use headers)

### Field Naming

**Pattern:** snake_case for JSON fields

```json
{
  "user_id": "usr_123",
  "created_at": "2026-01-24T12:00:00Z",
  "conversation_history": [...],
  "is_active": true
}
```

**Rules:**
- Consistent case everywhere (snake_case)
- Boolean fields start with `is_`, `has_`, `can_`
- Timestamps end with `_at`: `created_at`, `updated_at`
- IDs end with `_id` when foreign keys

### Resource IDs

**Pattern:** Prefixed for clarity

| Resource | Prefix | Example |
|----------|--------|---------|
| User | `usr_` | `usr_1a2b3c4d` |
| Conversation | `conv_` | `conv_5e6f7g8h` |
| Message | `msg_` | `msg_9i0j1k2l` |
| Session | `sess_` | `sess_3m4n5o6p` |
| Credential | `cred_` | `cred_7q8r9s0t` |

**Benefits:**
- Immediately know what type of resource
- Prevents mixing up IDs across tables
- Easier debugging and support

---

## Response Structures

### Successful Responses

**Pattern:** Consistent envelope with clear status

```json
{
  "status": "success",
  "data": {
    // The actual response data
  },
  "meta": {
    "request_id": "req_abc123",
    "timestamp": "2026-01-24T12:00:00Z",
    "version": "1.0"
  }
}
```

**List responses:**

```json
{
  "status": "success",
  "data": [
    // Array of items
  ],
  "meta": {
    "total": 100,
    "page": 1,
    "per_page": 20,
    "has_more": true,
    "request_id": "req_abc123"
  }
}
```

### Error Responses

**Pattern:** Helpful, not defensive

```json
{
  "status": "error",
  "error": {
    "code": "validation_error",
    "message": "The request couldn't be processed.",
    "details": "The 'email' field must be a valid email address.",
    "help": "Check the email format and try again.",
    "documentation": "https://docs.truthengine.co/errors/validation"
  },
  "meta": {
    "request_id": "req_abc123",
    "timestamp": "2026-01-24T12:00:00Z"
  }
}
```

**Error Response Principles:**
- `message`: What happened (human-readable)
- `details`: Specifically what's wrong
- `help`: What to do about it
- `documentation`: Where to learn more

---

## Error Messages

### The Philosophy

Error messages are moments of failure. They're when developers most need us to be helpful.

**From STRUCK:** When something goes wrong, we don't hide or blame. We acknowledge, help, and make recovery easy.

### Error Message Structure

Every error message should answer:
1. **What happened?** (The error)
2. **Why did it happen?** (The cause)
3. **What can you do?** (The remedy)

### Error Categories & Codes

| Category | Code Range | Meaning |
|----------|------------|---------|
| Validation | 400-level | Your request has a problem |
| Authentication | 401-403 | Who you are or what you can do |
| Not Found | 404 | Resource doesn't exist |
| Conflict | 409 | State conflict |
| Rate Limit | 429 | Too many requests |
| Server | 500-level | Our problem, not yours |

### Error Message Examples

**Validation Error (400)**
```json
{
  "code": "validation_error",
  "message": "The request couldn't be processed.",
  "details": "The 'start_date' must be before 'end_date'.",
  "help": "Adjust the date range so start_date comes first."
}
```

**Authentication Error (401)**
```json
{
  "code": "authentication_required",
  "message": "This endpoint requires authentication.",
  "details": "No API key was provided in the request headers.",
  "help": "Include your API key in the 'Authorization' header.",
  "documentation": "https://docs.truthengine.co/authentication"
}
```

**Authorization Error (403)**
```json
{
  "code": "insufficient_permissions",
  "message": "You don't have access to this resource.",
  "details": "Your API key doesn't have permission to access conversation conv_123.",
  "help": "Verify you're using the correct API key for this account."
}
```

**Not Found Error (404)**
```json
{
  "code": "resource_not_found",
  "message": "The requested resource doesn't exist.",
  "details": "No conversation found with ID conv_999.",
  "help": "Check the ID and try again, or list available conversations."
}
```

**Rate Limit Error (429)**
```json
{
  "code": "rate_limit_exceeded",
  "message": "You've made too many requests.",
  "details": "Rate limit of 100 requests per minute exceeded.",
  "help": "Wait before retrying. Consider implementing exponential backoff.",
  "retry_after": 30
}
```

**Server Error (500)**
```json
{
  "code": "internal_error",
  "message": "Something went wrong on our end.",
  "details": "We've been notified and are investigating.",
  "help": "Try again in a few minutes. If the problem persists, contact support.",
  "support_email": "support@truthengine.co"
}
```

### What NOT to Say

| Instead of | Say |
|------------|-----|
| "Invalid request" | "The 'email' field must be a valid email address" |
| "Error occurred" | "The conversation couldn't be saved because..." |
| "Bad request" | "The request is missing required field 'user_id'" |
| "Forbidden" | "Your API key doesn't have permission to..." |
| "Something went wrong" | "We couldn't process this request because..." |

---

## Documentation Voice

### Tone

- **Direct:** Get to the point
- **Helpful:** Anticipate questions
- **Human:** Not robotic or corporate
- **Confident:** We know what we're talking about

### Structure

Every endpoint should document:
1. **What it does** (one sentence)
2. **When to use it** (use cases)
3. **Request** (method, URL, parameters)
4. **Response** (success and error)
5. **Example** (real code)

### Example Documentation Block

```markdown
## Create Conversation

Start a new conversation with the user's NOT-ME.

### When to Use

Call this when starting a new conversation session. Each conversation 
maintains context and history.

### Request

`POST /conversations`

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| user_id | string | Yes | The user's ID |
| context | string | No | Optional context for the conversation |

### Response

Returns the created conversation object.

```json
{
  "status": "success",
  "data": {
    "id": "conv_abc123",
    "user_id": "usr_xyz789",
    "created_at": "2026-01-24T12:00:00Z",
    "status": "active"
  }
}
```

### Errors

| Code | Meaning |
|------|---------|
| 400 | Missing required parameter |
| 401 | Invalid API key |
| 404 | User not found |

### Example

```python
import truthengine

client = truthengine.Client(api_key="your_key")
conversation = client.conversations.create(user_id="usr_xyz789")
print(conversation.id)  # conv_abc123
```
```

---

## SDK Naming

### Method Naming

**Pattern:** Verb + noun, clear about what it does

```python
# Good
client.conversations.create()
client.conversations.get(id)
client.conversations.list()
client.conversations.delete(id)
client.messages.send(conversation_id, content)

# Avoid
client.newConversation()
client.getConvo()
client.doMessage()
```

### Parameter Naming

**Pattern:** Match the API, be explicit

```python
# Good
client.conversations.list(
    user_id="usr_123",
    limit=20,
    created_after="2026-01-01"
)

# Avoid
client.conversations.list(uid="usr_123", n=20, after="2026-01-01")
```

---

## Rate Limiting

### Communication

Rate limits should be:
- **Documented clearly**
- **Communicated in headers**
- **Generous for legitimate use**
- **Explained when hit**

### Headers

Include in every response:

```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1706097600
```

### When Exceeded

The error message should:
1. State the limit
2. Say when they can retry
3. Suggest alternatives

---

## Versioning

### Strategy

- **Header-based:** `Accept: application/vnd.truthengine.v1+json`
- **Graceful deprecation:** 6+ months notice
- **Clear changelog:** What changed, what to do

### Deprecation Notice

When deprecating:

```json
{
  "status": "success",
  "data": { ... },
  "warnings": [
    {
      "code": "deprecated_endpoint",
      "message": "This endpoint is deprecated and will be removed on 2026-07-01.",
      "help": "Use /v2/conversations instead.",
      "documentation": "https://docs.truthengine.co/migration/v2"
    }
  ]
}
```

---

## Security in Communication

### What We Say

- "Your API key grants access to your data only"
- "All requests are encrypted in transit"
- "We never log request bodies containing sensitive data"

### What We Don't Say

- Never reveal internal architecture in errors
- Never include stack traces in production
- Never expose other users' data in error messages

---

## The Meta-Principle

The API is a relationship. Treat it like one.

- Be consistent (developers learn your patterns)
- Be helpful (especially when things go wrong)
- Be honest (don't hide problems)
- Be respectful (of their time, their data, their trust)

**The test:** Would a developer feel cared for using this API? If not, revise.

---

## Document Index

| Related Document | Relationship |
|------------------|--------------|
| [Error Message Standards](ERROR_MESSAGE_STANDARDS.md) | User-facing error messages |
| [Framework Brand Language](FRAMEWORK_BRAND_LANGUAGE.md) | What language we use |
| [NOT-ME Communication Standards](NOT_ME_COMMUNICATION_STANDARDS.md) | AI communication principles |
| [Employee Brand Standards](EMPLOYEE_BRAND_STANDARDS.md) | Overall voice guidelines |

---

*An API is a conversation with code. It should feel like Truth Engine: direct, helpful, and caring.*
