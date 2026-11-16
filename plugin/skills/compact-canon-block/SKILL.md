---
name: compact-canon-block
description: "Fill and print the 7-header block to paste after /compact in Claude Code, so the summary keeps decisions with their reasons, exact paths, values and open problems. Use when the user wants to compact, asks for a compact block, or is at a task boundary near 60% context."
---

# Print a filled 7-header compact block

This skill writes text into the chat. It runs nothing, and it cannot run
`/compact` for the user: the user pastes the block as their next message.

## Why an inline block

Measured in Claude Code transcripts (source: MEASUREMENTS.md in
https://github.com/tonydzi/compact-canon):

- A `CLAUDE.md` compact section does not reach the compactor. Re-measured
  2026-08-29: **0 of 447** instruction-free compactions produced the custom
  skeleton (auto-compact 39, bare `/compact` 380, `/compact` with other
  free-text args 28; the first 2026-07-22 scan saw 354 of 354 on the stock
  template).
- `/compact` with the full 7-header block inline landed **5** of 9 runs
  lifetime, **4 / 5** in August. A miss comes back as the plain stock template.
- Seeded live tests: **7/7 custom headers present**, **15/15 spot-checked
  facts survived** (2026-07-23, `preTokens 54358 → postTokens 2522`); 2026-09-05
  on CLI 2.1.246: inline block **7/7 headers, 15/15 facts**, while the
  `CLAUDE.md` section plus bare `/compact` gave **0/7 marker headers** and
  6/15 seeded facts.
- The block usually supplements the stock summary: 8 of the 9 block runs kept
  the stock template alongside the headers. Fact duplication costs ≈2.5k tokens.
- Auto-compact cannot take instructions at all, so compact manually.

## Workflow

1. Confirm timing with the user: a task boundary, ideally near 60% context.
   Very short sessions may get `not enough messages to compact.` and no summary.
2. Collect this session's real facts. Fill every header with verbatim content
   from this chat. No empty headers, no `<...>` placeholders, no summaries of
   summaries:
   - DECISIONS: what was decided and WHY, including rejected alternatives
     ("we do X / we do NOT do Y because...").
   - TODO: tasks with priorities.
   - NOW: the active task or live error plus the immediate next step.
   - PATHS & VALUES: exact file paths, scripts, folders and exact values (note
     names, frontmatter keys, chat or DB IDs, env vars, constants).
   - COUNTERS: final self-check numbers and what is NOT finished.
   - OPEN: what broke, remains or diverges: broken links, gotchas, bugs and
     symptoms.
   - TOOLS & CONTRACTS: scripts, scheduled tasks, MCP servers, versions,
     API or format contracts touched.
3. Print the line `➤ Copy the whole block and paste it as your next message`,
   then ONE fenced code block in this shape, filled:

```
/compact Preserve VERBATIM under 7 headers (rationales disappear first):
- DECISIONS — ...
- TODO — ...
- NOW — ...
- PATHS & VALUES — ...
- COUNTERS — ...
- OPEN — ...
- TOOLS & CONTRACTS — ...
Compress what works to 1 line + component names. Drop: debugging back-and-forth, dead-end hypotheses, file contents (except exact values), logs, rephrasings.
```

4. Print the block itself in the chat. Never answer with a pointer such as
   "paste the block from that file": a pointer preserves nothing.
5. After the user compacts, a good check is asking "why did we reject X?" and
   getting a specific answer.

## Rules of thumb

- Rationales die first, exact values second; that is why DECISIONS demands the
  rejected alternatives and PATHS & VALUES is verbatim-only.
- Do not suggest a PreCompact hook or a `CLAUDE.md` section as a substitute:
  the hook cannot inject text into the compactor, and the section was never
  applied in the measurements above.
- The measurements were taken on Windows with Claude Code CLI up to 2.1.246;
  say so if the user asks about other platforms or versions.
