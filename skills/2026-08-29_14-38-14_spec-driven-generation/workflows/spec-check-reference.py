# ---
# skill: spec-driven-generation
# role: workflow
# capability: spec-alignment-checker
# ships-command: null
# bundle-id: spec-driven-generation-2026-08-29
# bundle-tier: full
# body: full
# native-hint: shared/workflows/spec-check-reference.py
# ---
# -*- coding: utf-8 -*-
"""Root-alignment check for spec-driven generation — REFERENCE IMPLEMENTATION.

Copy into a project as `0-script/_lib/_spec_check.py`. Generic by design: it reads the output
stage's `_manifest.json` and validates whatever that declares, so it works for any analyze
project in any domain — no project-specific logic.

Implements the six checkable invariants in `specs/SPEC_DRIVEN_GENERATION.md`
→ "Root alignment". Generic: it reads the output stage's `_manifest.json` and validates
whatever it declares, so it is reusable by any analyze project, not just this one.

    python _spec_check.py [<project-root>] [--live]

  <project-root>  defaults to the grandparent of this file (…/money)
  --live          additionally open each `live_target` artifact and confirm the declared
                  units actually exist in it (xlsx only; skipped if unreadable)

Exit 0 = aligned · 1 = drift found. Reports `⚠ DRIFT`, never repairs.
"""
import os, sys, json, glob, re, warnings
sys.stdout.reconfigure(encoding="utf-8")
warnings.filterwarnings("ignore")

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 and not sys.argv[1].startswith("-") \
    else os.path.abspath(os.path.join(HERE, "..", ".."))
LIVE = "--live" in sys.argv

drift, ok = [], []


def D(rule, msg):
    drift.append((rule, msg))


def OK(msg):
    ok.append(msg)


def rel(p):
    return os.path.join(ROOT, p.replace("/", os.sep))


def slugify(fname):
    return re.sub(r"[^a-z0-9]+", "-", fname.lower()).strip("-")


OUT_STAGES = ["4-generated", "2-generated"]
manifests = [os.path.join(ROOT, s, "_manifest.json") for s in OUT_STAGES]
manifests = [m for m in manifests if os.path.isfile(m)]
if not manifests:
    print("no output-stage _manifest.json found under %s — nothing to check" % ROOT)
    raise SystemExit(0)

declared_builders = set()
declared_specs = set()

for mf in manifests:
    stage = os.path.basename(os.path.dirname(mf))
    man = json.load(open(mf, encoding="utf-8"))
    for fname, entry in man.get("files", {}).items():
        if entry.get("kind") not in ("generated", "deploy-record"):
            continue
        label = "%s/%s" % (stage, fname)

        # (1) spec ⇄ artifact
        spec = entry.get("spec")
        if not spec:
            D(1, "%s has no `spec` field" % label)
            continue
        spath = rel(spec)
        if not os.path.exists(spath):
            D(1, "%s → spec `%s` does not resolve" % (label, spec))
            continue
        declared_specs.add(os.path.normpath(spath))
        OK("%s → spec resolves" % label)

        # (5) slug matches artifact name
        artifact = entry.get("artifact") or fname
        if os.path.isdir(spath):
            want = "spec_" + slugify(artifact)
            got = os.path.basename(spath.rstrip(os.sep))
            if got != want:
                D(5, "%s: spec folder `%s` should be `%s` for artifact `%s`" % (label, got, want, artifact))
            else:
                OK("%s → slug matches artifact" % label)

        units = entry.get("units")
        if not units:
            continue

        spec_files = {os.path.basename(p) for p in glob.glob(os.path.join(spath, "*.md"))
                      if not os.path.basename(p).startswith("_")} if os.path.isdir(spath) else set()
        specced = set()

        for uname, u in units.items():
            owner = u.get("owner")
            ulab = "%s :: %s" % (label, uname)

            if owner == "user":
                # (3) a builder pointed at a user-owned unit is a data-loss hazard
                if u.get("builder"):
                    D(3, "%s is owner=user but declares builder `%s` — data-loss hazard" % (ulab, u["builder"]))
                if not u.get("policy"):
                    D(3, "%s is owner=user with no `policy` (expected never-write)" % ulab)
                continue

            if owner != "claude":
                D(3, "%s has unknown owner `%s` (expected claude|user)" % (ulab, owner))
                continue

            # (2) unit ⇄ spec
            us = u.get("spec")
            if not us:
                D(2, "%s (owner=claude) declares no `spec`" % ulab)
            elif not os.path.isfile(rel(us)):
                D(2, "%s → spec `%s` does not resolve" % (ulab, us))
            else:
                specced.add(os.path.basename(rel(us)))

            # (3) unit ⇄ builder
            b = u.get("builder")
            if not b:
                if not u.get("note"):
                    D(3, "%s (owner=claude) has no `builder` and no explanatory `note`" % ulab)
                else:
                    OK("%s → no builder, gap documented" % ulab)
            elif not os.path.isfile(rel(b)):
                D(3, "%s → builder `%s` does not exist" % (ulab, b))
            else:
                declared_builders.add(os.path.normpath(rel(b)))
                OK("%s → builder exists" % ulab)

            # (4) declared paths resolve
            for k in ("data", "sources"):
                for p in u.get(k, []):
                    if k == "sources" and not re.match(r'^[\w.\-/]+$', p):
                        continue            # prose source description, not a path
                    if "*" in p:
                        if not glob.glob(rel(p)):
                            D(4, "%s → %s glob `%s` matches nothing" % (ulab, k, p))
                    elif not os.path.exists(rel(p)):
                        D(4, "%s → %s `%s` does not resolve" % (ulab, k, p))

        # (2 inverse) spec files with no unit
        for orphan in sorted(spec_files - specced):
            D(2, "%s: spec `%s` describes no declared unit (deleted unit?)" % (label, orphan))

        # (--live) declared units vs the real artifact
        lt = entry.get("live_target")
        if LIVE and lt and lt.lower().endswith(".xlsx"):
            try:
                import openpyxl
                wb = openpyxl.load_workbook(lt, read_only=True)
                actual = set(wb.sheetnames); wb.close()
                for miss in sorted(set(units) - actual):
                    D(2, "%s: unit `%s` declared but absent from the live artifact" % (label, miss))
                for extra in sorted(actual - set(units)):
                    D(2, "%s: live artifact has undeclared unit `%s`" % (label, extra))
                if set(units) == actual:
                    OK("%s → all %d units match the live artifact" % (label, len(actual)))
            except Exception as e:
                print("  (live check skipped: %s)" % str(e)[:70])

# (6) orphan scripts
sdir = os.path.join(ROOT, "0-script")
if os.path.isdir(sdir):
    readme = ""
    rp = os.path.join(sdir, "README.md")
    if os.path.isfile(rp):
        readme = open(rp, encoding="utf-8").read()
    for p in sorted(glob.glob(os.path.join(sdir, "*.py"))):
        if os.path.normpath(p) in declared_builders:
            continue
        if os.path.basename(p) in readme:      # explicitly documented (e.g. "do not run")
            OK("0-script/%s → not a builder, documented in README" % os.path.basename(p))
        else:
            D(6, "0-script/%s is named by no unit and undocumented in README.md" % os.path.basename(p))

print("=" * 78)
print("SPEC ALIGNMENT — %s" % ROOT)
print("=" * 78)
for m in ok:
    print("  ✓ %s" % m)
if drift:
    print()
    for rule, m in sorted(drift):
        print("  ⚠ DRIFT [rule %d] %s" % (rule, m))
print()
print("%d checks passed · %d drift item(s)" % (len(ok), len(drift)))
raise SystemExit(1 if drift else 0)
