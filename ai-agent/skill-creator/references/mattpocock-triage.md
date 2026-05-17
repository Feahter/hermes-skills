# Issue Triage — from mattpocock/triage

> Triage issues through a state machine driven by triage roles.

## When to Use
- Creating issues
- Reviewing incoming bugs or feature requests
- Preparing issues for an AFK agent
- Managing issue workflow

## Core Concept: Tracer-Bullet Vertical Slices

Break plans into **vertical slices** (end-to-end feature increments), not horizontal layers. Each issue is a thin but complete capability.

## State Machine (Triage Roles)

| State | Action | Next |
|-------|--------|------|
| new | Initial assessment | triage |
| triage | Label + assign priority | blocked / ready |
| blocked | Waiting on dependency | ready |
| ready | Ready for implementation | in-progress |
| in-progress | Being worked | review |
| review | Code review | done |
| done | Closed | — |

## Key Triggers
- "triage this"
- "create an issue"
- "review incoming bugs"
- "prepare issues for when I'm away"
