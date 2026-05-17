# RFC: Stage-Level Tool Whitelist — #26524

**Repo:** NousResearch/hermes-agent
**Issue:** https://github.com/NousResearch/hermes-agent/issues/26524
**Labels:** type/feature, comp/plugins, comp/agent
**Status:** Submitted, awaiting maintainer response

## Summary

Add `{"tools": [...]}` return value support to `pre_llm_call` hook, enabling per-turn tool schema filtering.

## Key Design Decisions (from RFC)

| Decision | Choice | Rationale |
|---|---|---|
| Filter mechanism | Union semantics | Any callback can expand allowed set |
| Return type change | `(results, allowed_tools)` tuple | Backwards compatible if callers check type |
| Core integration point | `run_agent.py` `client.chat.completions.create()` call site | Single call site, minimal invasiveness |
| Enforcement level | Advisory (not hard block) | Model may still call filtered tools via `handle_function_call` |

## Three Implementation Phases

1. **hermes_cli/plugins.py** — extend `invoke_hook()` to return `allowed_tools`
2. **run_agent.py** — filter tools before API call
3. **Documentation** — hook docstring + example skill

## Related upstream issues/PRs

- Hook system: `hermes_cli/plugins.py:1209-1214`
- Agent loop: `run_agent.py` (tools passed to `client.chat.completions.create`)

## Why This RFC Matters

Statewright experiment proves: constraining tool visibility per stage boosts 13B model from 20%→100% on SWE-bench. Hermes has the hook infrastructure to replicate this without core agent redesign — the gap is only the `tools` return value support in `pre_llm_call`.
