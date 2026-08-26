# compact-canon

**A measured paste-block format that stops Claude Code's `/compact` from erasing your session's decisions — built after proving that every "official" customization path silently fails.**

## The pain, in your words

- *"Claude forgot everything after compact."*
- *"I added a Compact Instructions section to CLAUDE.md and compaction completely ignores it."*
- *"After `/compact` it remembers WHAT we did, but not WHY we rejected the other approach."*
- *"My PreCompact hook runs, but the summary comes out in the same stock template every time."*

If any of these is you, the problem is not your prompt. It's that the compactor runs as a separate call with its own system prompt, and none of your customization reaches it.

## The numbers (our measurements, July 2026)

| Measurement | Result |
|---|---|
| Bare `/compact` runs that applied our `CLAUDE.md` "Compact Instructions" section | **0 / 354** |
| Same runs falling back to the stock English template | **354 / 354** |
| Custom headers surviving when the block is pasted **inline** after `/compact` | **7 / 7** |
| Seeded facts surviving compaction (paths, chat IDs, counters, one rejected decision) | **15 / 15** |
| Token squeeze in the live verification run | **54,358 → 2,522** |

Dataset: one machine's complete transcript archive (JSONL, `compactMetadata` / `isCompactSummary` markers), plus live verification on Claude Code CLI 2.1.186 — both headless (`claude -p --resume`) and in a real interactive session. Full method and repro protocol: [MEASUREMENTS.md](MEASUREMENTS.md).

Why the official paths fail:
- [anthropics/claude-code#14160](https://github.com/anthropics/claude-code/issues/14160) — custom instructions for auto-compact; closed as duplicate, PreCompact receives **empty** `custom_instructions` on auto-trigger.
- [anthropics/claude-code#43733](https://github.com/anthropics/claude-code/issues/43733) — PreCompact injection; closed *not planned*, the hook can only emit stderr.
- The `CLAUDE.md` section approach recommended by several blogs: measured **0/354** above. 🤔 The `compactPrompt` settings key circulating in posts is unverified folklore as far as we can tell.

## Self-diagnosis in 30 seconds

Find your last compaction summary and look at its headers:

```bash
grep -rl '"isCompactSummary":true' ~/.claude/projects/ | head -3
```

Open one match. If the summary uses the stock English template sections even though you wrote custom compact instructions somewhere — your instructions never applied. That's the disease this repo treats.

## How it fixes it

One mechanism, zero machinery: **paste a structured block inline, right after the command** — `/compact <block>`. Inline text is the only injection path that provably reaches the compactor.

The block is a 7-header preservation order ([COMPACT.md](COMPACT.md)):

1. **DECISIONS** — what was decided **and why**, including rejected alternatives (rationales die first)
2. **TODO** — tasks with priorities
3. **NOW** — the active task / live error + next step
4. **PATHS & VALUES** — exact files, IDs, constants (exact values die second)
5. **COUNTERS** — self-check numbers + what is NOT done
6. **OPEN** — what broke, diverged, or remains
7. **TOOLS & CONTRACTS** — scripts, versions, APIs, formats touched

Have the agent fill the skeleton with the session's real facts before you paste it — an exact fill-in prompt ships in [COMPACT.md](COMPACT.md).

Honest nuance from the live test: the inline block **supplements** the default template rather than replacing it (both appear in the summary, ~2.5k duplicated tokens). We consider that a fair price for 15/15 fact survival.

## Design choices

- **Plain text. Zero dependencies. Nothing to install.** No plugin, no hook, no daemon — a text block you paste. If it stops working, you can see why.
- **Fail-open:** worst case you get the stock summary you'd have gotten anyway.
- **Manual `/compact` only.** Auto-compact cannot be steered (see issues above) — so compact deliberately at ~60% context instead of letting auto-compact fire at 95%. Our companion ritual [claw-retro](https://github.com/tonydzi/claw-retro) prints this block for you at every session close, so there is nothing to remember.

## Install

1. Copy [COMPACT.md](COMPACT.md) somewhere your agent can read it (or into your prompt library).
2. At a task boundary, ask the agent: *"Fill the 7-header compact block with THIS session's facts, verbatim values, one fenced block starting with `/compact `."*
3. Copy the fenced block, paste it as your next message.
4. Verify it worked: after compaction, ask *"why did we reject &lt;alternative&gt;?"* — a session compacted with the block answers specifically; a stock-compacted one answers generically.

## FAQ

**Why not a PreCompact hook?** It can't inject text — stderr only ([#43733](https://github.com/anthropics/claude-code/issues/43733)).

**Why not a CLAUDE.md section?** Measured: 0 applications in 354 compactions. The compactor never loads it.

**Does the block replace the stock summary?** No — verified live: it's appended alongside it. Duplication ≈2.5k tokens, tolerable.

**Does this help auto-compact?** No. Nothing does, today. Compact manually at task boundaries; that's the actual discipline this repo encodes.

**Is this Claude-Code-specific?** The measurements are. The 7-header preservation order works anywhere a lossy session summary is written — the categories encode *what dies first*, which is model-agnostic.

## Attribution & license

Invented by **Mycroft** (synthetic cofounder) & **Tony** — [Palo Alto AI Research Lab](https://github.com/tonydzi). MIT license.

Siblings: [claw-retro](https://github.com/tonydzi/claw-retro) (the ritual that prints this block) · [claw-consensus](https://github.com/tonydzi/claw-consensus) (multi-machine agent consensus).

We hand free working seeds of our lab tooling to engineer-testers — WhatsApp **+1 (341) 222-9178**.
