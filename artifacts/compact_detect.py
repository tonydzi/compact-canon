"""Deterministic detector for the compact-canon replication (read-only, 0 LLM).

Purpose: over one machine transcript archive of Claude Code, count compaction
events, classify each by trigger and by what the user actually passed to
/compact, and score whether the resulting summary carries the custom 7-header
skeleton.

Protocol per tonydzi/compact-canon MEASUREMENTS.md section 5, plus two fixes
found while replicating on a second machine (2026-09-10):
  * compactMetadata sits on a sibling compact_boundary record; join through
    preservedMessages.anchorUuid;
  * JSONL is not timestamp-ordered -> pair a summary with the nearest /compact
    command whose timestamp <= summary timestamp;
  * a header counts only if it OPENS a line (substring matching is a
    false-positive machine);
  * NEW: records are duplicated in resumed files -> dedupe events by uuid;
  * NEW: allow at most one leading space before the header. A stock summary that
    quotes the block as a nested list item ("   - **DECISIONS:** ...") otherwise
    scores a perfect 7 under the line-opening rule too.
For every event that does score 7 the detector also reports whether the header
words were already present in the conversation BEFORE the compaction
(carry_over), because a skeleton can be imitated from context content.

Input : root dir of ~/.claude/projects
Output: JSON summary on stdout + compact_detect_events.json next to this file.
Rail  : local python, no network. updated: 2026-09-10
"""
import json, os, re, sys, collections

ROOT = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser("~/.claude/projects")

HEADSETS = {
    "en": ["DECISIONS", "TODO", "NOW", "PATHS & VALUES", "COUNTERS", "OPEN", "TOOLS & CONTRACTS"],
    "ru": ["РЕШЕНИЯ", "TODO", "СЕЙЧАС", "ПУТИ", "СЧЁТЧИКИ", "ОТКРЫТО", "ИНСТРУМЕНТЫ"],
}
STRICT = r"(?m)^[ ]{0,1}(?:[-*]\s+|#{1,4}\s*)?(?:\*\*)?\s*"   # top-level heading or bullet only
LOOSE = r"(?m)^[\s>]*(?:[-*#]+\s*)?(?:\*\*)?\s*"              # tolerant rule (nested quotes slip in)


def count(text, headers, prefix):
    return sum(1 for h in headers if re.search(prefix + re.escape(h), text))


def score(text):
    """-> (strict best, loose best, substring best, which language set)"""
    bs = bl = bsub = 0
    which = None
    for name, hs in HEADSETS.items():
        s = count(text, hs, STRICT)
        l = count(text, hs, LOOSE)
        sub = sum(1 for h in hs if h in text)
        if s > bs:
            bs, which = s, name
        if which is None and l > bl:
            which = name
        bl = max(bl, l)
        bsub = max(bsub, sub)
    return bs, bl, bsub, which


CMD_NAME = re.compile(r"<command-name>/?compact</command-name>")
CMD_ARGS = re.compile(r"<command-args>(.*?)</command-args>", re.S)


def text_of(rec):
    out = []
    m = rec.get("message")
    if isinstance(m, dict):
        c = m.get("content")
        if isinstance(c, str):
            out.append(c)
        elif isinstance(c, list):
            for part in c:
                if isinstance(part, dict) and isinstance(part.get("text"), str):
                    out.append(part["text"])
    if isinstance(rec.get("content"), str):
        out.append(rec["content"])
    if isinstance(rec.get("summary"), str):
        out.append(rec["summary"])
    return "\n".join(out)


buckets = collections.Counter()
strict7 = collections.Counter()
loose7 = collections.Counter()
sub7 = collections.Counter()
carry = collections.Counter()
versions = set()
dates = []
files = 0
events = []
seen_uuid = set()

for dirpath, _, names in os.walk(ROOT):
    for n in names:
        if not n.endswith(".jsonl"):
            continue
        files += 1
        p = os.path.join(dirpath, n)
        recs = []
        try:
            with open(p, encoding="utf-8", errors="replace") as fh:
                for line in fh:
                    line = line.strip()
                    if line:
                        try:
                            recs.append(json.loads(line))
                        except Exception:
                            pass
        except Exception:
            continue

        summaries = {r.get("uuid"): r for r in recs if r.get("isCompactSummary") is True}
        metas = [r for r in recs if isinstance(r.get("compactMetadata"), dict)]
        cmds = []
        for r in recs:
            t = text_of(r)
            if CMD_NAME.search(t):
                a = CMD_ARGS.search(t)
                cmds.append((r.get("timestamp") or "", (a.group(1).strip() if a else "")))
        cmds.sort(key=lambda x: x[0])

        for meta in metas:
            key = (p, meta.get("uuid"))
            if key in seen_uuid:
                continue          # duplicated record in a resumed file
            seen_uuid.add(key)
            cm = meta["compactMetadata"]
            trig = cm.get("trigger", "?")
            ts = meta.get("timestamp") or ""
            anchor = (cm.get("preservedMessages") or {}).get("anchorUuid")
            summ = summaries.get(anchor)
            joined = summ is not None
            if summ is None:
                cands = [s for s in summaries.values() if (s.get("timestamp") or "") <= ts]
                summ = max(cands, key=lambda s: s.get("timestamp") or "") if cands else None
            stext = text_of(summ) if summ else ""
            sts = (summ.get("timestamp") if summ else ts) or ts

            if trig != "manual":
                bucket = "auto"
            elif not cmds:
                bucket = "manual_args_unknown"      # no command record survived in the file
            else:
                prev = [c for c in cmds if c[0] <= sts]
                args = prev[-1][1] if prev else ""
                if args.strip() == "":
                    bucket = "manual_bare"
                else:
                    a_any = max(sum(1 for h in hs if h in args) for hs in HEADSETS.values())
                    bucket = "manual_block" if a_any >= 6 else "manual_freetext"

            s, l, sub, which = score(stext)
            buckets[bucket] += 1
            if s >= 7:
                strict7[bucket] += 1
            if l >= 7:
                loose7[bucket] += 1
            if sub >= 7:
                sub7[bucket] += 1

            carried = None
            if s >= 7:
                hs = HEADSETS[which]
                carried = False
                for r in recs:
                    rts = r.get("timestamp") or ""
                    if rts and rts < sts and not r.get("isCompactSummary"):
                        blob = json.dumps(r, ensure_ascii=False)
                        if sum(1 for h in hs if h in blob) >= 6:
                            carried = True
                            break
                if carried:
                    carry[bucket] += 1

            v = meta.get("version") or (summ or {}).get("version")
            if v:
                versions.add(v)
            if ts:
                dates.append(ts[:10])
            events.append({"bucket": bucket, "strict": s, "loose": l, "substring": sub,
                           "set": which, "carry_over": carried, "anchor_joined": joined,
                           "ts": ts, "version": v, "pre": cm.get("preTokens"),
                           "post": cm.get("postTokens"), "file": p})

res = {
    "files_scanned": files,
    "compaction_events": sum(buckets.values()),
    "buckets": dict(buckets),
    "skeleton_7of7_strict": dict(strict7),
    "skeleton_7of7_loose_rule": dict(loose7),
    "skeleton_7of7_substring_rule": dict(sub7),
    "of_strict_hits_format_already_in_context": dict(carry),
    "anchor_join_failures": sum(1 for e in events if not e["anchor_joined"]),
    "cli_versions": sorted(versions),
    "date_range": [min(dates), max(dates)] if dates else None,
}
print(json.dumps(res, ensure_ascii=False, indent=2))
with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "compact_detect_events.json"), "w", encoding="utf-8") as fh:
    json.dump(events, fh, ensure_ascii=False, indent=1)
