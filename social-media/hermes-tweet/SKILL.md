---
name: hermes-tweet
description: Use Hermes Tweet from Hermes Agent to search tweets, search X/Twitter, read tweet replies, look up users, monitor tweets, post tweets, post replies, send DMs, run extraction jobs, and automate X actions through Xquik.
version: 0.1.6
author: Xquik
license: MIT
platforms: [linux, macos]
prerequisites:
  commands: [hermes]
  env_vars: [XQUIK_API_KEY]
metadata:
  hermes:
    tags: [hermes-agent, twitter, x, xquik, social-media, automation]
    homepage: https://github.com/Xquik-dev/hermes-tweet
    package: https://pypi.org/project/hermes-tweet/
    docs: https://docs.xquik.com/guides/hermes-tweet
---

# Hermes Tweet

Hermes Tweet is a native Hermes Agent plugin for X/Twitter automation through
Xquik. Use it when a Hermes session needs to search tweets, read tweet replies,
look up users, monitor tweets, post tweets, post replies, send DMs, run
extraction jobs, or automate X actions with approval gates.

## When to use

Use this skill when the user asks to:

- search tweets or X/Twitter conversations
- read tweet details, replies, trends, account status, or public profile data
- look up users, followers, following, or media
- monitor tweets or account activity
- create extraction jobs, giveaway draws, webhooks, or media workflows
- post tweets, post replies, send DMs, follow users, or run other X actions

## Install

Install the Hermes plugin from GitHub:

```bash
hermes plugins install Xquik-dev/hermes-tweet --enable
```

Or install the PyPI package into the Hermes Agent Python environment:

```bash
uv pip install --python ~/.hermes/hermes-agent/venv/bin/python hermes-tweet
hermes plugins enable hermes-tweet
```

Verify the toolset:

```bash
hermes tools list
```

## Configure

Create an Xquik API key in the Xquik dashboard, then set it in the Hermes
runtime environment:

```bash
export XQUIK_API_KEY="xq_..."
```

Optional settings:

```bash
export XQUIK_BASE_URL="https://xquik.com"
export HERMES_TWEET_ENABLE_ACTIONS="false"
```

Keep action endpoints disabled for unattended sessions. Set
`HERMES_TWEET_ENABLE_ACTIONS=true` only for workflows that intentionally allow
posting, replies, DMs, follows, monitor changes, webhook changes, extraction
jobs, or other account actions.

## Workflow

1. Use `tweet_explore` to find the relevant Xquik endpoint.
2. Use `tweet_read` for public read-only `GET` endpoints.
3. Use `tweet_action` only for write-like calls or private reads after the user
   approves the exact operation.

Search tweets:

```json
{"query":"search tweets","method":"GET"}
```

Then call `tweet_read` with the discovered endpoint:

```json
{"path":"/api/v1/x/tweets/search","query":{"q":"AI agents","limit":25}}
```

Post a user-approved tweet:

```json
{"query":"post tweet","include_actions":true}
```

Then call `tweet_action` only after confirming the account and text:

```json
{"path":"/api/v1/x/tweets","method":"POST","body":{"account":"@example","text":"Hello from Hermes Tweet"},"reason":"Post the user-approved tweet."}
```

## Safety rules

- Never ask for or reveal API keys, passwords, cookies, or session material.
- Never pass credentials in tool arguments.
- Do not guess API paths. Use `tweet_explore` first.
- Use only catalog-listed `/api/v1/...` endpoints.
- Do not use account connection, re-authentication, API-key, billing, credit
  top-up, or support-ticket endpoints.
- Summarize the exact action before posting tweets, replies, DMs, follows,
  monitor changes, webhook changes, extraction jobs, or draws.
- If `tweet_action` is disabled, explain that action tools require
  `HERMES_TWEET_ENABLE_ACTIONS=true`.

## Quick checks

```bash
hermes plugins enable hermes-tweet
hermes tools list
```

Expected behavior:

- `tweet_explore` can search the bundled endpoint catalog.
- `tweet_read` requires `XQUIK_API_KEY`.
- `tweet_action` stays hidden or disabled unless
  `HERMES_TWEET_ENABLE_ACTIONS=true`.
- Slash commands such as `/xstatus` and `/xtrends` are available in an active
  Hermes CLI or gateway session.
