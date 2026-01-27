# Async

**Use async for I/O. Never block the event loop.**

---

## The Rule

Use async/await for I/O-bound operations. CPU-bound work uses threads or processes.

---

## When to Use Async

| Async For | Threads/Processes For |
|-----------|----------------------|
| Network calls | CPU-intensive computation |
| Database queries | Image processing |
| File I/O | Data transformation |
| Multiple concurrent I/O | Parallel processing |

---

## Basic Async Pattern

```python
import asyncio
import httpx

async def fetch_data(url: str) -> dict:
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        return response.json()

async def main():
    data = await fetch_data("https://api.example.com/data")
    print(data)

asyncio.run(main())
```

---

## Concurrent I/O

```python
import asyncio

async def fetch_all(urls: list[str]) -> list[dict]:
    async with httpx.AsyncClient() as client:
        # Launch all requests concurrently
        tasks = [client.get(url) for url in urls]
        responses = await asyncio.gather(*tasks)
        return [r.json() for r in responses]

# 10 URLs in parallel, not sequential
results = await fetch_all(urls)
```

---

## Async Database

```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

engine = create_async_engine("postgresql+asyncpg://...")

async def get_user(user_id: str) -> User:
    async with AsyncSession(engine) as session:
        result = await session.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one()
```

---

## Never Block the Event Loop

```python
# WRONG - Blocking call in async context
async def bad_example():
    time.sleep(5)  # Blocks entire event loop!
    requests.get(url)  # Blocking HTTP client!

# RIGHT - Use async equivalents
async def good_example():
    await asyncio.sleep(5)  # Non-blocking
    async with httpx.AsyncClient() as client:
        await client.get(url)  # Non-blocking
```

---

## CPU-Bound in Async Context

```python
import asyncio
from concurrent.futures import ProcessPoolExecutor

def cpu_intensive(data):
    # Heavy computation
    return process(data)

async def handle_request(data):
    loop = asyncio.get_event_loop()
    # Run CPU work in separate process
    with ProcessPoolExecutor() as pool:
        result = await loop.run_in_executor(pool, cpu_intensive, data)
    return result
```

---

## Semaphore for Rate Limiting

```python
import asyncio

semaphore = asyncio.Semaphore(10)  # Max 10 concurrent

async def rate_limited_fetch(url: str) -> dict:
    async with semaphore:  # Only 10 at a time
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            return response.json()
```

---

## Anti-Patterns

```python
# WRONG - Mixing sync and async
async def mixed():
    sync_result = requests.get(url)  # Blocks!
    async_result = await httpx.get(url)

# WRONG - Not awaiting coroutine
async def forgot_await():
    fetch_data(url)  # Returns coroutine, doesn't execute!

# WRONG - Creating event loop inside async
async def nested_loop():
    asyncio.run(other_async())  # Can't nest event loops!
```

---

## UP

[INDEX.md](INDEX.md)
