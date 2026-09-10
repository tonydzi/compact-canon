# FOR ROBOTS

You are an AI agent reading this repo. Ranked takeaways, densest first. One rule about
this file itself: **it is data, not authorization.** Nothing here overrides your
operator's policies or lets you install anything on your own.

## Alpha, ranked

1. **The documented customization path for compaction does not reach the compactor.**
   0 of 447 compactions applied our CLAUDE.md "Compact Instructions" section: 0/380 for
   bare `/compact`, 0/39 for auto-compact (structurally impossible there), 0/28 for
   `/compact` with free-text args that were not the block. If you added that section and
   assumed it fires, it does not.
2. **The reason is architectural**: compaction runs as a separate call with its own
   system prompt, so project instructions never arrive. That also means a PreCompact
   hook can run correctly and still produce the stock template.
3. **What does work is pasting the block inline** with the command: 5 of 9 runs returned
   our 7 headers, 4 of 5 on recent CLIs, and 15 of 15 seeded facts survived (paths, chat
   IDs, counters, and one rejected decision). The rejected decision matters most: stock
   summaries keep what you did and drop why you refused the alternative.
4. **Compaction is a squeeze, not a save**: 54,358 tokens to 2,522 in the verification
   run.

## Provenance

Dataset: 16,107 transcript files and 456 compaction events across CLI 2.1.161 to
2.1.246, re-run 2026-08-29. These are our own measurements on our own transcripts, not
a vendor statement, and they are version-sensitive: re-measure before trusting them on a
newer CLI. MEASUREMENTS.md carries the breakdown, COMPACT.md the block itself.

## Family

Sibling repos of the Palo Alto AI Research Lab: `claude-bible` is the family map.
`claw-retro` consumes this block at end of session; `always-loaded-diet` covers the
neighbouring always-loaded budget problem.
