# REST

**Resources have URLs. Actions have HTTP methods.**

---

## The Rule

Use RESTful conventions: nouns for resources, HTTP verbs for actions.

---

## URL Structure

```
/{resource}/{id}/{sub-resource}
```

| Pattern | Example | Purpose |
|---------|---------|---------|
| Collection | `/users` | List all users |
| Instance | `/users/123` | Single user |
| Sub-resource | `/users/123/orders` | User's orders |
| Nested instance | `/users/123/orders/456` | Specific order |

---

## HTTP Methods

| Method | Purpose | Idempotent | Safe |
|--------|---------|------------|------|
| GET | Read resource | Yes | Yes |
| POST | Create resource | No | No |
| PUT | Replace resource | Yes | No |
| PATCH | Update resource | Yes | No |
| DELETE | Remove resource | Yes | No |

---

## Status Codes

| Code | Meaning | Use When |
|------|---------|----------|
| 200 | OK | GET/PUT/PATCH success |
| 201 | Created | POST creates resource |
| 204 | No Content | DELETE success |
| 400 | Bad Request | Invalid input |
| 401 | Unauthorized | No/invalid auth |
| 403 | Forbidden | Auth valid, no permission |
| 404 | Not Found | Resource doesn't exist |
| 409 | Conflict | State conflict (duplicate) |
| 422 | Unprocessable | Validation failed |
| 500 | Server Error | Unexpected error |

---

## Request/Response Format

```python
# Request
POST /api/v1/users
Content-Type: application/json
{
    "email": "user@example.com",
    "name": "Example User"
}

# Response
HTTP/1.1 201 Created
Content-Type: application/json
{
    "id": "123",
    "email": "user@example.com",
    "name": "Example User",
    "created_at": "2026-01-26T12:00:00Z"
}
```

---

## Naming Conventions

| Do | Don't |
|----|-------|
| `/users` | `/getUsers` |
| `/users/123` | `/user?id=123` |
| `/users/123/orders` | `/getUserOrders` |
| Plural nouns | Singular nouns |
| Lowercase | camelCase in URLs |
| Hyphens for multi-word | Underscores |

---

## Query Parameters

| Purpose | Parameter | Example |
|---------|-----------|---------|
| Pagination | `page`, `limit` | `?page=2&limit=20` |
| Sorting | `sort`, `order` | `?sort=created_at&order=desc` |
| Filtering | Field names | `?status=active` |
| Search | `q` | `?q=search+term` |

---

## Anti-Patterns

```
# WRONG - Verbs in URL
GET /getUser/123
POST /createUser
DELETE /deleteUser/123

# WRONG - Action in URL
POST /users/123/activate  # Use PATCH with body instead

# WRONG - Mixed casing
GET /Users/123/orderItems
```

---

## UP

[INDEX.md](INDEX.md)
