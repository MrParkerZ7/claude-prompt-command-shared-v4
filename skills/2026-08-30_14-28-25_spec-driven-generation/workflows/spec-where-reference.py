# ---
# skill: spec-driven-generation
# role: workflow
# capability: value-lineage-query
# ships-command: null
# bundle-id: spec-driven-generation-2026-08-30
# bundle-tier: full
# body: full
# native-hint: shared/workflows/spec-where-reference.py
# ---
# -*- coding: utf-8 -*-
"""`_where.py` — REFERENCE IMPLEMENTATION: "where did this number come from?"

Copy into a project as `0-script/_lib/_where.py`. Reads `_data/_lineage.json`, which the
builders write via `spec-lineage-reference.py`. Generic - no project-specific logic.
See `specs/SPEC_DRIVEN_GENERATION.md` § Value lineage.

`_where.py` — answer "where did this number come from?" for any recorded cell.

This is the tool a LATER session runs when it opens the workbook, distrusts a figure, and
needs the answer without guessing. It reads `_data/_lineage.json`, which the builders write
at cell-write time.

    python _where.py "🤖Salary!C20"      one cell - full chain, source checked on disk
    python _where.py 87300               every cell recorded with that value
    python _where.py --sheet 🤖Salary    coverage summary for one sheet
    python _where.py --audit             every 'documented' claim whose source does NOT resolve
    python _where.py                     what is covered, and what is not

Exit 1 when --audit finds a broken claim, so it can gate.
"""
import os, io, sys, json, glob

_HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(_HERE, "..", ".."))          # the project (money/)
CASE = os.path.abspath(os.path.join(ROOT, ".."))                 # the case repo
LEDGER = os.path.join(_HERE, "..", "_data", "_lineage.json")
sys.stdout.reconfigure(encoding="utf-8")

if not os.path.isfile(LEDGER):
    print("no lineage ledger at %s — run a builder first" % LEDGER); raise SystemExit(1)
LED = json.load(io.open(LEDGER, encoding="utf-8"))
SHEETS = LED.get("sheets", {})

MARK = {"documented": "✅ documented", "derived": "🔧 derived",
        "estimated": "⚠ estimated", "assumed": "✎ assumed"}


def resolves(src):
    """Does a recorded source actually exist? Sources are repo-relative or prose."""
    if not src:
        return None
    head = src.split(" : ")[0].split(" · ")[0].strip()
    if not head or " " in head and "/" not in head:
        return None                                   # prose, not a path
    for base in (CASE, ROOT):
        cand = os.path.join(base, head.replace("/", os.sep))
        if os.path.exists(cand):
            return True
        if "*" in head and glob.glob(cand):
            return True
    return False if "/" in head else None


def show(sheet, cell, e):
    print("\n  %s!%s   =  %s" % (sheet, cell, e.get("value")))
    print("     %s" % MARK.get(e["confidence"], e["confidence"]))
    if e.get("source"):
        r = resolves(e["source"])
        tag = {True: " ✓ exists", False: " ❗ DOES NOT RESOLVE", None: ""}[r]
        print("     source : %s%s" % (e["source"], tag))
    if e.get("method"):
        print("     method : %s" % e["method"])
    if e.get("inputs"):
        for i in e["inputs"]:
            print("     input  : %s" % i)
    if e.get("chain"):
        print("     chain  : %s" % "  →  ".join(e["chain"]))
    if e.get("note"):
        print("     note   : %s" % e["note"])


args = [a for a in sys.argv[1:]]
if not args:
    print("=" * 78); print("VALUE LINEAGE — coverage"); print("=" * 78)
    for sh, blk in sorted(SHEETS.items()):
        from collections import Counter
        c = Counter(v["confidence"] for v in blk["cells"].values())
        print("  %-18s %4d values   %s   (stamped %s)"
              % (sh, len(blk["cells"]),
                 " · ".join("%s %d" % (k, c[k]) for k in MARK if c[k]), blk.get("stamped", "?")))
    print("\n  query a cell:   python _where.py \"<Sheet>!<Cell>\"")
    print("  query a value:  python _where.py 87300")
    print("  audit claims:   python _where.py --audit")
    raise SystemExit(0)

if args[0] == "--audit":
    bad = []
    for sh, blk in SHEETS.items():
        for cell, e in blk["cells"].items():
            if e["confidence"] == "documented" and resolves(e.get("source")) is False:
                bad.append((sh, cell, e.get("source")))
    if bad:
        print("❗ %d 'documented' value(s) name a source that does not resolve:" % len(bad))
        for sh, cell, src in bad[:40]:
            print("   %s!%s -> %s" % (sh, cell, src))
        raise SystemExit(1)
    n = sum(1 for b in SHEETS.values() for e in b["cells"].values() if e["confidence"] == "documented")
    print("✓ all %d 'documented' values name a source that resolves on disk" % n)
    raise SystemExit(0)

if args[0] == "--sheet":
    sh = args[1]
    blk = SHEETS.get(sh)
    if not blk:
        print("no lineage for sheet %r. Known: %s" % (sh, ", ".join(SHEETS))); raise SystemExit(1)
    for cell, e in sorted(blk["cells"].items()):
        show(sh, cell, e)
    raise SystemExit(0)

q = args[0]
if "!" in q:
    sh, cell = q.split("!", 1)
    blk = SHEETS.get(sh)
    if not blk:
        print("no lineage recorded for sheet %r.\nKnown sheets: %s" % (sh, ", ".join(SHEETS)))
        raise SystemExit(1)
    e = blk["cells"].get(cell.upper())
    if not e:
        print("❗ %s!%s has NO lineage record." % (sh, cell))
        print("   That means it was not emitted with provenance — treat it as UNVERIFIED,")
        print("   not as documented. See the sheet's spec for what is and is not payslip-backed.")
        raise SystemExit(1)
    show(sh, cell, e)
    raise SystemExit(0)

try:
    val = float(q.replace(",", ""))
except ValueError:
    print("give a cell ref (Sheet!A1), a number, --sheet <name>, or --audit"); raise SystemExit(1)
hits = [(sh, c, e) for sh, b in SHEETS.items() for c, e in b["cells"].items()
        if e.get("value") is not None and abs(float(e["value"]) - val) < 0.005]
if not hits:
    print("no recorded value equals %s" % q); raise SystemExit(1)
print("%d cell(s) hold %s:" % (len(hits), q))
for sh, c, e in hits[:25]:
    show(sh, c, e)
if len(hits) > 25:
    print("\n  … +%d more" % (len(hits) - 25))
