---
name: python-try-finally-wrapper-pattern
description: "Correctly wrap a Python method body in try/finally by rewriting the entire method. Use when injecting cleanup, lease-release, or metrics that must fire on every exit path of a function with multiple return branches."
category: software-development
---

# Python try/finally Wrapper Pattern

When you need to inject logic that fires on **every exit path** of a function (cleanup, lease release, metrics, logging), use a try/finally at the function level — not inline patching.

## The Failure Mode: Patch Breaks Indentation

Suppose you have:

```python
def foo():
    if condition:
        return result_a
    elif other:
        return result_b
    else:
        return result_c
```

You want to wrap everything in `try/finally`. **Naive patch fails**:

```
# WRONG — indentation breaks on untouched branches
def foo():
    try:          # you added this
        if condition:
            return result_a   # still at original indent = SyntaxError
```

## The Correct Pattern: Full Method Rewrite

Read the **entire method** (not just the changed portion), then replace the whole thing:

```python
def foo():
    # Preamble: runs before try
    _cleanup_token = None
    if resource_manager:
        _cleanup_token = resource_manager.acquire()

    def _release():
        if _cleanup_token is not None:
            resource_manager.release(_cleanup_token)

    try:
        if condition:
            return result_a
        elif other:
            return result_b
        else:
            return result_c
    finally:
        _release()    # fires on every return path
```

## Key Rules

1. **Read full method before editing** — partial read + patch corrupts indentation of untouched branches
2. **Move preamble before `try`** — anything that must run before the protected block
3. **Put `finally` at the same indent as `try`** — they are a pair
4. **`return` stays inside `try`** — don't move return statements; `finally` fires before propagation
5. **Close over local variables in closure** — `_release()` safely accesses `_cleanup_token` from outer scope

## Decision Checklist

- Does the function have multiple return points (if/elif/else, early returns)?
- Does it need guaranteed cleanup on every exit (lease, file handle, lock, metrics)?
- Are you tempted to add try/except around each return individually?
→ Use the full method rewrite pattern instead.
