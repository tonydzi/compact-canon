# compact-canon plugin

An instructions-only plugin with one skill, `compact-canon-block`. It fills a
7-header block with the current session's real facts and prints it in the
chat, ready to paste after `/compact` in Claude Code. The summary then keeps
decisions with their reasons, exact paths and values, counters and open
problems.

The plugin runs no code and cannot run `/compact` itself: you paste the
printed block as your next message.

## Why

From the measurements in the
[repository](https://github.com/tonydzi/compact-canon/blob/main/MEASUREMENTS.md):
a `CLAUDE.md` compact section reached the compactor in 0 of 447
instruction-free compactions, while `/compact` with the 7-header block inline
landed 5 of 9 runs lifetime (4 / 5 in August) and kept 15/15 seeded facts in
live tests.

## Install and use

```text
/plugin marketplace add tonydzi/compact-canon
/plugin install compact-canon@compact-canon
```

At a task boundary, ideally near 60% context, ask Claude for a compact block.
Copy the fenced block it prints and send it as your next message.

## Contents

Only Markdown instructions, JSON metadata and an icon. No data is collected or
sent; see [PRIVACY.md](https://github.com/tonydzi/compact-canon/blob/main/PRIVACY.md).
