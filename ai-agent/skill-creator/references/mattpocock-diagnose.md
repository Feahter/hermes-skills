# Diagnosis Loop — from mattpocock/diagnose

> Disciplined diagnosis loop for hard bugs and performance regressions.

## When to Use
- User says "diagnose this" / "debug this"
- Bug report: something is broken/throwing/failing
- Performance regression described

## The Loop

```
Reproduce → Minimise → Hypothesise → Instrument → Fix → Regression-test
```

### 1. Reproduce
Get exact steps to trigger the failure consistently.

### 2. Minimise
Strip the reproduction case to smallest possible (binary search the cause).

### 3. Hypothesise
Form specific, falsifiable hypotheses — not "something is wrong."

### 4. Instrument
Add logging/probing at the hypothesis point.

### 5. Fix
Apply the minimal change that addresses the root cause.

### 6. Regression-test
Verify the fix and that no new failures were introduced.

## Key Triggers
- "diagnose this"
- "debug this"
- "it's broken"
- "it's throwing"
- "it's failing"
- "performance regression"
