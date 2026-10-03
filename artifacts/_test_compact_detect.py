"""Fixture test for compact_detect.score().

Three fixtures, each a real failure mode we hit while replicating:
  A. stock summary that QUOTES the seven header names inside a line
     -> substring rule says 7, both line rules must say 0
     (the defect named in compact-canon MEASUREMENTS.md section 5.3)
  B. stock summary that quotes the block as an INDENTED list item
     -> substring 7, tolerant line rule 7, strict rule must stay under 7
     (the defect we found on 2026-09-10 on the second machine)
  C. a real skeleton -> strict rule must say 7

Run with --rule loose or --rule substring to score by the defective rules and
watch the test go red. updated: 2026-09-10
"""
import sys, os, importlib.util

ARGV = list(sys.argv)          # the import below overwrites sys.argv
RULE = "strict"
if "--rule" in ARGV:
    RULE = ARGV[ARGV.index("--rule") + 1]

spec = importlib.util.spec_from_file_location(
    "cd_", os.path.join(os.path.dirname(os.path.abspath(__file__)), "compact_detect.py"))
m = importlib.util.module_from_spec(spec)
sys.argv = [sys.argv[0], os.path.join(os.path.dirname(os.path.abspath(__file__)), "_no_such_dir")]
spec.loader.exec_module(m)

A = """## Analysis
The user's compact args requested the 7-heading verbatim format: DECISIONS - TODO - NOW - PATHS & VALUES - COUNTERS - OPEN - TOOLS & CONTRACTS.
## Summary
We worked on the parser and fixed two bugs.
"""

B = """1. **Primary Request and Intent:**

   The previous compact block the user pasted read:
   - **DECISIONS:** we keep the inline block
   - **TODO:** ship the paper
   - **NOW:** section 4
   - **PATHS & VALUES:** E:/Obsidian/main.tex
   - **COUNTERS:** 447 events
   - **OPEN:** draft not published
   - **TOOLS & CONTRACTS:** pdflatex
"""

C = """DECISIONS - we use the inline block because CLAUDE.md never reaches the compactor
TODO - ship the paper
NOW - writing section 4
PATHS & VALUES - E:/Obsidian/main.tex
COUNTERS - 447 events, 0 skeletons
OPEN - Zenodo draft not published
TOOLS & CONTRACTS - pdflatex, pypdf
"""


def sc(text):
    s, l, sub, _ = m.score(text)
    return {"strict": s, "loose": l, "substring": sub}[RULE]


fails = []
a, b, c = sc(A), sc(B), sc(C)
if a != 0:
    fails.append(f"A (quoted inside a line) scored {a}, expected 0")
if b >= 7:
    fails.append(f"B (quoted as an indented list) scored {b}, must stay under 7")
if c != 7:
    fails.append(f"C (real skeleton) scored {c}, expected 7")

print(f"rule={RULE}  A={a}  B={b}  C={c}")
if fails:
    print("FAIL: " + "; ".join(fails))
    sys.exit(1)
print("PASS 3/3")
