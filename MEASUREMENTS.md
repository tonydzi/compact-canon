# Measurements & repro protocol

All numbers below are from our own fleet, dated. Nothing here is extrapolated; where we could not verify a claim we say so.

## 1. The 354-compaction dataset (2026-07-22)

**Question:** does a `CLAUDE.md § Compact Instructions` section influence what bare `/compact` (or auto-compact) preserves?

**Method:** scanned one machine's complete Claude Code transcript archive (`~/.claude/projects/**/*.jsonl`). Compaction events identified by `"isCompactSummary":true` and `compactMetadata`. Each summary checked for our custom 7-header format vs the stock English template.

**Result: 354 of 354 compactions used the stock template. 0 applied the CLAUDE.md section.**

**Root cause:** the compactor is a separate model call with its own system prompt; project/user `CLAUDE.md` is not part of that call. Confirmed by the issue tracker:
- [#14160](https://github.com/anthropics/claude-code/issues/14160) — request for `autoCompact.customInstructions` / a respected CLAUDE.md section; closed as duplicate; on auto-trigger the PreCompact hook receives an **empty** `custom_instructions` field.
- [#43733](https://github.com/anthropics/claude-code/issues/43733) — request for PreCompact instruction injection; closed *not planned*; the hook can only print to stderr (it can block, not steer).

## 2. Live verification, headless (2026-07-23, CLI 2.1.186)

**Question:** does an inline block after manual `/compact` actually reach the compactor, and what survives?

**Method:**
1. Seed a session with 40+ verifiable facts (paths, chat IDs, three distinct counters, one explicitly rejected decision, a test-status marker):
   `claude -p "<seeding prompt with the facts>"`
2. Compact it with the block inline:
   `claude -p --resume <session-id> "/compact <the filled 7-header block>"`
3. Read the resulting transcript JSONL; find the summary message; check headers and spot-check facts **by script, not by eye**.

**Result:**
- `compactMetadata: trigger=manual, preTokens 54358 → postTokens 2522`
- **7/7 custom headers present** in the summary.
- **15/15 spot-checked facts survived** — including the exact counters and the rejected-decision rationale, which stock compaction reliably drops.

**Finding (correction of our own earlier belief):** the inline block **supplements** the stock template rather than replacing it — the summary contains the stock sections, a separator, then our 7 headers. Fact duplication costs ≈2.5k tokens. We had previously claimed "replaces"; the transcript proved otherwise, so we corrected the canon.

## 3. Live verification, interactive (2026-07-23)

Same protocol, but a human pressed `/compact <block>` in a real interactive session (not `-p`). Transcript line: `isCompactSummary=true`, `compactMetadata.trigger=manual`. Verified by script: **7/7 headers present, 9/9 spot-check keys survived.** This closes the gap between the headless harness and the path a human actually uses.

## 4. What we did NOT verify

- 🤔 The `compactPrompt` key in `settings.json` mentioned in some blog posts — we found no documentation and did not test it.
- 🤔 Whether newer CLI versions changed any of the above. Our data is CLI 2.1.186, July 2026. The repro protocol above takes ~10 minutes; re-run it before relying on these numbers on a newer CLI. PRs with fresh measurements are the single most welcome contribution to this repo.

## Repro checklist (10 minutes)

```bash
# 1. seed
claude -p "Remember these facts verbatim: <invent 15+ facts: 3 fake paths, 2 fake IDs, 3 counters, 1 rejected decision with a reason>"
# note the session id printed / from ~/.claude/projects/<project>/

# 2. compact with the block
claude -p --resume <session-id> "/compact <filled block from COMPACT.md>"

# 3. verify
grep -l '"isCompactSummary":true' ~/.claude/projects/<project>/*.jsonl
# open the summary, count your headers, grep for each seeded fact
```
