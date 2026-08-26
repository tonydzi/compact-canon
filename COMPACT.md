# The 7-header compact block

Two parts: the **skeleton** you (or your agent) fill, and the **fill-in prompt** that makes the agent do it.

## Skeleton

Paste this — filled, never with `<...>` placeholders left inside — as one message, starting with `/compact `:

```
/compact Preserve VERBATIM under 7 headers (rationales disappear first):
- DECISIONS — <what was decided + WHY, including rejected alternatives ("we do X / we do NOT do Y because...")>
- TODO — <tasks with priorities>
- NOW — <the active task or live error + the immediate next step>
- PATHS & VALUES — <exact file paths, scripts, folders + exact values: note names, frontmatter keys, chat/DB IDs, env vars, constants>
- COUNTERS — <final self-check numbers + what is NOT finished>
- OPEN — <what broke / remains / diverges: broken links, known gotchas, bugs + symptoms>
- TOOLS & CONTRACTS — <scripts, scheduled tasks, MCP servers, versions, API/format contracts touched>
Compress what works to 1 line + component names. Drop: debugging back-and-forth, dead-end hypotheses, file contents (except exact values), logs, rephrasings.
```

## Fill-in prompt (give this to your agent before compacting)

> Fill the 7-header compact block from COMPACT.md with THIS session's real facts. Every header gets actual content from this chat — decisions with their why and what we rejected, the live error into NOW, exact paths/IDs/constants, self-check counters and what's unfinished, everything broken into OPEN. No empty headers, no `<...>` placeholders, no summaries of summaries. Output ONE fenced code block starting with `/compact `, with the line "➤ Copy the whole block and paste it as your next message" above it.

## Rules of thumb

- **Rationales first.** The stock compactor keeps *what* happened; the first thing it drops is *why*. That's why DECISIONS demands the rejected alternatives explicitly.
- **Exact values die second.** A summary that says "updated the config" instead of the actual key name costs you a re-discovery next session. PATHS & VALUES is verbatim-only.
- **Compact at ~60% context, at a task boundary.** Waiting for auto-compact at 95% both loses more and removes your ability to steer (auto-compact cannot be given instructions at all).
- **A pointer is not a block.** "Paste the block from such-and-such file" defeats the whole mechanism — the text must be printed, filled, in the chat, ready to copy. We learned this the hard way and banned the pointer wording in our own agent's rules.
