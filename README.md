# compact-canon

**A measured paste-block format that stops Claude Code's `/compact` from erasing your session's decisions — built after proving that every "official" customization path silently fails.**

## The pain, in your words

- *"Claude forgot everything after compact."*
- *"I added a Compact Instructions section to CLAUDE.md and compaction completely ignores it."*
- *"After `/compact` it remembers WHAT we did, but not WHY we rejected the other approach."*
- *"My PreCompact hook runs, but the summary comes out in the same stock template every time."*

If any of these is you, the problem is not your prompt. It's that the compactor runs as a separate call with its own system prompt, and none of your customization reaches it.

## The numbers (our measurements, re-run 2026-08-29 on CLI up to 2.1.246)

| Measurement | Result |
|---|---|
| Compactions with **no** inline block that applied our `CLAUDE.md` "Compact Instructions" section | **0 / 447** |
| - of those, bare `/compact` (empty args) | 0 / 380 |
| - of those, auto-compact (instructions structurally impossible) | 0 / 39 |
| - of those, `/compact` with free-text args that were not the block | 0 / 28 |
| Runs where the full block **was** pasted inline and the 7 headers came back | **5 / 9** (recent CLIs: 4 / 5) |
| Seeded facts surviving a successful block run (paths, chat IDs, counters, one rejected decision) | **15 / 15** |
| Token squeeze in the live verification run | **54,358 -> 2,522** |

Dataset: 16,107 transcript files, 456 compaction events, CLI 2.1.161 -> 2.1.246, 2026-06-06 -> 2026-08-29,
plus the July live verification on CLI 2.1.186 in both a headless and a real interactive session.

⚠️ **Two honest corrections to our own earlier claims**, both found by re-running this in August
after the maintainer of [netresearch/retro-skill](https://github.com/netresearch/retro-skill/issues/78)
rightly pointed out that a stale scan settles nothing:

- The inline block is **reliable, not deterministic** - 5 of 9 lifetime, 4 of 5 on recent CLIs. We
  previously printed **7/7** from a single live test. A run that misses returns the plain stock template.
- Our original detector counted a header as present anywhere in the summary, so a stock summary that
  merely *quotes* the instruction line scored a perfect 7/7. That method claims 67 of 405 bare
  compactions "worked"; a detector that requires the header to open a line says 0 of 380. Full method,
  the three defects, and a corrected repro: [MEASUREMENTS.md](MEASUREMENTS.md) section 5.

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

---

<!--ecosystem-map:start-->

## 🧩 One piece of a working system

This repository is one piece lifted out of a live operation: one non-technical founder, an AI
cofounder, and a fleet of machines that reach consensus with each other and wake the human only
for money or the irreversible. It was extracted after it survived production, not written as a
demo — and it runs on its own: nothing here phones home to the rest.

**See how the whole thing fits together → [SYSTEM.md](https://github.com/tonydzi/tonydzi/blob/main/SYSTEM.md)**

Its closest neighbours in the **memory** layer: [`sqlite-graph-memory`](https://github.com/tonydzi/sqlite-graph-memory) · [`second-brain-starter-kit`](https://github.com/tonydzi/second-brain-starter-kit) · [`voice2brain`](https://github.com/tonydzi/voice2brain)

<!--ecosystem-map:end-->

## AI contributors

This project is built by a human + AI team, and the git log says so: Claude writes most of
the code, Codex and Grok review it, Gemini feeds the research. Each is credited on a commit
**only if its output changed that commit's content** — no decorative credits. Lab-wide
policy, one source for every repo: [AI-CONTRIBUTORS.md](https://github.com/tonydzi/.github/blob/main/AI-CONTRIBUTORS.md).
