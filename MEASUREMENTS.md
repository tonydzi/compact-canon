# Measurements & repro protocol

All numbers below are from our own fleet, dated. Nothing here is extrapolated; where we could not verify a claim we say so.

## 1. The 354-compaction dataset (2026-07-22)

**Question:** does a `CLAUDE.md § Compact Instructions` section influence what bare `/compact` (or auto-compact) preserves?

**Method:** scanned one machine's complete Claude Code transcript archive (`~/.claude/projects/**/*.jsonl`). Compaction events identified by `"isCompactSummary":true` and `compactMetadata`. Each summary checked for our custom 7-header format vs the stock English template.

**Result: 354 of 354 compactions used the stock template. 0 applied the CLAUDE.md section.**

> ⚠️ **Re-measured 2026-08-29 on CLI 2.1.246 — see section 5.** The finding holds and is now stronger
> (0 of 447 instruction-free compactions). The *method* above does not: three defects in it are
> documented in section 5, one of which makes it report false positives. Use the section 5 protocol.

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
- ✅ ~~Whether newer CLI versions changed any of the above.~~ **Answered 2026-08-29, section 5** (CLI up to 2.1.246).
- 🤔 Whether the failure is identical on other platforms. Every number in this file was measured on Windows.

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


## 5. Re-measurement, 2026-08-29 (CLI up to 2.1.246)

Prompted by a fair challenge from the maintainer of
[netresearch/retro-skill#78](https://github.com/netresearch/retro-skill/issues/78): a stale archive
scan does not settle whether the thing works today. Section 4 of this file said the same about
itself, so we re-ran it instead of defending the old number.

**Dataset:** 16,107 transcript files, **456** compaction events with joined metadata,
CLI **2.1.161 → 2.1.246**, 2026-06-06 → 2026-08-29.

| Bucket | n | produced the 7-header skeleton |
|---|---|---|
| auto-compact (instructions structurally impossible) | 39 | **0** |
| bare `/compact`, empty args | 380 | **0** |
| `/compact` + free-text args that were not the block | 28 | **0** |
| **subtotal: every run without an explicit block** | **447** | **0** |
| `/compact` + the full 7-header block inline | 9 | **5** (August alone: **4 / 5**) |

**What this changes.**

1. **The negative finding survives, larger.** Not one of 447 instruction-free compactions across
   three months and 18 CLI versions produced the custom skeleton. A `CLAUDE.md` compact section did
   not reach the compactor even once. `/compact <instructions>` remains the documented mechanism, and
   it is the only one we can measure working — the point of this repo is that the *other* paths people
   are told to use do not.
2. **Our own headline was too strong.** The README advertised **7/7** from a single live test. Across
   real use the inline block lands **5 of 9** lifetime, **4 of 5** on recent CLIs — reliable, not
   deterministic. The table has been corrected. A block run that misses does not partly apply: it comes
   back as the plain stock template.
3. **"Supplements, not replaces" mostly holds.** 8 of the 9 block runs carried the stock template
   alongside our headers; one (2026-08-26, CLI 2.1.237) replaced it outright. So budget for the
   duplication, but do not count on it.

### Three defects in the section 1–3 method (fix these before trusting any rerun)

1. **`compactMetadata` is not on the `isCompactSummary` record.** It lives on a sibling record. Join
   `compactMetadata.preservedMessages.anchorUuid == <summary>.uuid` (auto-compacts may carry no
   `preservedMessages`). Following the section 1 protocol literally today classifies **zero** events.
2. **The JSONL is not in timestamp order.** The `<command-name>/compact</command-name>` record is
   written *after* the summary it caused. Pairing a summary with "the last `/compact` seen while
   reading the file" attaches the wrong `<command-args>`. This bit us inside this very rerun: it made
   two block runs look like failures and five bare runs look like successes, and we nearly published
   that. Pair by timestamp, or by the anchor join above.
3. **Substring matching for the header words is a false-positive machine.** A stock English summary
   that merely *quotes* the instruction line ("args requested the 7-heading verbatim format: РЕШЕНИЯ ·
   TODO · …") scores a perfect 7/7. On this archive substring matching claims **67 of 405** bare
   compactions honored the instructions; requiring each header to *open a line* gives **0 of 380**.
   The 0/354 in section 1 was therefore right by luck of that dataset, not by the detector.

### Corrected repro (deterministic, no LLM, read-only)

```python
# for each ~/.claude/projects/**/*.jsonl:
#   summaries[uuid] = record where isCompactSummary is True
#   metas           = records carrying compactMetadata
#   cmds            = user records matching <command-name>/compact</command-name>,
#                     with <command-args> captured (empty args == bare)
# join : meta -> summaries[meta.preservedMessages.anchorUuid]
# args : nearest cmd with cmd.timestamp <= summary.timestamp  (NOT file order)
# score: header counts only if it opens a line ->
#        re.search(r"(?m)^[\s>]*(?:[-*#]+\s*)?(?:\*\*)?\s*" + re.escape(header), summary)
```

Sanity-check your detector on two fixtures before believing it: a stock summary that quotes all seven
header names must score **0**, and a real skeleton must score **7**. A detector that cannot tell those
apart will hand you the 16.5% that is not there.
