---
skill: spec-driven-generation
role: spec
capability: spec-driven-generation-standard
ships-command: null
bundle-id: spec-driven-generation-2026-08-30
bundle-tier: full
body: full
native-hint: shared/SPEC_DRIVEN_GENERATION.md
---

# Spec-Driven Generation

> **The standard:** every generated artifact is produced from a **written spec**, not from a builder script alone.
> Mandatory for every analyze project, in every domain and every project type.
>
> Extracted from `shared/OUTPUTS.md` on 2026-08-29 so it can be adopted (and exported) on its own.
> It **extends** the stage-provenance manifest defined in `shared/OUTPUTS.md` § Stage Provenance — manifest v2
> is additive over v1, so read that first if you are adopting both.

---

Every generated artifact is produced from a **written spec**, not from a builder script alone. The spec is the source of truth; the script is one implementation of it. This applies to **every analyze project, in every domain and every project type** — `.xlsx`, `.docx`, `.drawio`, `.pdf`, a generated site, a report set.

**Why this is mandatory.** A builder script encodes *how* and never *what the contract is* or *why*. Three failures follow from script-only artifacts, all observed in production:

1. **The script is lost** — built in a session scratchpad and never persisted, so the artifact becomes unmaintainable and the next session reverse-engineers it or rebuilds from scratch.
2. **Nothing records ownership.** For an artifact edited **in place** — a live workbook, a shared document — where some units belong to the user and must never be rewritten, a script says nothing about which those are. A new session can destroy user data while believing it is doing a routine regeneration.
3. **Hard-won derived facts evaporate.** The forensics behind a column ("this total already includes the installment, so living cost = bills − installment") lives only in the conversation that produced it, and the next session silently re-derives it wrongly.

The spec fixes all three: it is persisted, it declares ownership per unit, and it carries the reasoning.

### Layout

```
0-source/ | 0-records/                     inputs (user-dropped, never rewritten)
        │
        ▼   (a command targets an update)
1-analysis/
└── spec_<artifact-slug>/                  ← one folder per generated artifact
    ├── _README.md                         what the artifact is · unit ownership map
    ├── _manifest.json                     binding: sources → spec → unit → builder → output
    └── <unit-name>.md                     one spec per addressable unit
        │
        ▼   (implemented by)
0-script/                                  builders + shared helpers + their data
        │
        ▼
2-generated/ | 4-generated/
└── <artifact-file>                        the artifact …
    or <artifact-slug>.deploy.md           … or its deploy record, when the live copy sits outside the repo
```

- **`<artifact-slug>`** is the generated file's name, lowercased, with every non-alphanumeric run collapsed to `-`: `Budget Model.xlsx` → `spec_budget-model-xlsx/`, `Team Handbook.docx` → `spec_team-handbook-docx/`. Deterministic, so the spec↔artifact link is derivable in **both** directions without consulting the manifest.
- **Unit** = the smallest independently-regenerable part of the artifact: a **sheet** in a workbook, a **top-level section** in a long document, one **diagram** in a set, one **endpoint group** in an API doc. An artifact with a single unit gets a single spec file named for the artifact — the folder shape does not change.
- **`0-script/`** already exists as the production-script stage (`shared/PROJECTS.md` § "Production scripts"). Builders live there, **not** in `1-analysis/`, and resolve their data relative to their own file so they run from any working directory.

### What a unit spec MUST contain

| § | Section | Content |
|---|---------|---------|
| 1 | **Purpose** | what this unit answers, in one or two sentences |
| 2 | **Ownership & cadence** | `claude` or `user`; how often it is refreshed and what triggers it |
| 3 | **Structure** | every column / section, **in order**, with type, meaning, and grouping |
| 4 | **Derivation** | for each derived value, the formula or rule — the *contract*, not the code |
| 5 | **Presentation** | palette, header tiers, table ranges, conditional formats, naming |
| 6 | **Inputs** | the data files and upstream sources it reads |
| 7 | **Invariants** | what must never change or be violated |
| 8 | **Known gaps** | ⚠ what is unfinished, stale, or deliberately not done |

§8 is not optional. A spec that implies completeness it does not have is worse than one that names its holes.

### Manifest extension

The stage-provenance schema above gains these fields. **v1 manifests stay valid** — the fields are additive, and a single-unit artifact with a repo-local output needs none of them beyond `spec`.

| Field | Scope | Meaning |
|-------|-------|---------|
| `spec` | generated entry | Path to the unit's spec file, or to the `spec_<slug>/` folder for a composite artifact. **Required on every `generated` entry.** |
| `units` | generated entry | Composite artifacts only — maps unit name → unit record (below). Absent for single-unit artifacts. |
| `owner` | unit record | `claude` (regenerable) or `user` (❗ never written). |
| `policy` | unit record | For `owner: user` — the handling rule, normally `never-write`. |
| `cadence` | unit record | When this unit is refreshed (`monthly`, `on-renewal`, `one-off`, `on-actuals`). |
| `builder` | unit record | Repo-relative path to the script implementing the spec. Absent for `owner: user`. |
| `data` | unit record | Data files the builder reads. |
| `edit_mode` | generated entry | `regenerate` (artifact rebuilt whole) or `in-place` (surgical edit; foreign units preserved byte-for-byte). |
| `live_target` | generated entry | Absolute path when the deployed artifact lives **outside** the repo (OneDrive, a server, a shared drive). Pairs with a `<slug>.deploy.md` record in the output stage. |

```json
{
  "version": 2,
  "stage": "4-generated",
  "revision": 1,
  "built_from": { "commit": "e87da99", "generated": "2026-08-29" },
  "files": {
    "budget-model-xlsx.deploy.md": {
      "kind": "deploy-record",
      "artifact": "Budget Model.xlsx",
      "edit_mode": "in-place",
      "live_target": "C:/Users/<user>/OneDrive/Finance/Budget Model.xlsx",
      "spec": "1-analysis/spec_budget-model-xlsx/",
      "units": {
        "🤖Forecast": {
          "owner": "claude",
          "cadence": "on-actuals",
          "spec": "1-analysis/spec_budget-model-xlsx/🤖Forecast.md",
          "builder": "0-script/build_forecast.py",
          "data": ["0-script/_data/forecast-rows.json"],
          "sources": ["0-records/statements/2026-H1.md"]
        },
        "Manual Notes": { "owner": "user", "policy": "never-write" }
      }
    }
  }
}
```

### Root alignment — the checkable invariants

"Root alignment" means the spec tree, the manifest, the builders and the artifact all agree. These are **mechanically checkable**; each violation is reported as `⚠ DRIFT`, never silently repaired:

1. **Spec ⇄ artifact** — every `spec_<slug>/` has a matching `generated` entry in an output stage, and every `generated` entry carries a `spec` that resolves.
2. **Unit ⇄ spec** — every Claude-owned unit in the live artifact has a spec file, and every spec file corresponds to a unit that actually exists. An extra spec means a deleted unit; a missing spec means undocumented output.
3. **Unit ⇄ builder** — every `owner: claude` unit names a `builder` that exists on disk; every `owner: user` unit has **no** builder (a builder pointed at a user unit is a data-loss hazard and is an error, not a warning).
4. **Paths resolve** — every `spec`, `builder`, `data` and `sources` path exists. `live_target` is reported as unverifiable rather than broken when it is off-repo and absent.
5. **Slug matches** — `spec_<slug>/` derives from the artifact's filename by the rule above.
6. **No orphan scripts** — every script in `0-script/` is named by some unit's `builder`, or is a shared helper under `_lib/`, or is explicitly marked do-not-run in the stage `_README.md`.

7. **Lineage claims resolve** — see § Value lineage above: every `documented` record names a source path that exists.

**Who runs the check:** `sync` (as part of structure validation), `review` / `validate` (QA Engineer), and any command that regenerates the artifact — before writing, so a stale spec is caught rather than propagated.

## Value lineage — where each NUMBER came from

The spec above records how an artifact is **shaped** and the manifest records which **files** fed a unit. Neither answers the question a later session actually has when it opens the artifact and distrusts a figure: **"where did this number come from, and how was it computed?"**

Value lineage closes that. It is **required for any generated artifact whose figures come from source documents** (statements, payslips, returns, contracts, meter readings, survey exports); optional where every value is self-evident from the inputs already named in the manifest.

### The rule that does the work

**The builder records lineage AS IT WRITES EACH CELL, in the same transaction.** A ledger maintained separately drifts from the artifact; one emitted at write time cannot. This is the same principle as writing the spec in the same transaction as the artifact — one step, not two.

### Confidence is a closed vocabulary

Every record carries exactly one:

| | meaning |
|---|---|
| `documented` | a source document states the figure outright — **must** name a path that resolves |
| `derived` | computed from documented figures by the **stated method** |
| `estimated` | the user's own record or a working figure, with no source document |
| `assumed` | a forward-looking input the user can edit |

❗ **`documented` is a checkable claim, not a label.** Root-alignment rule 7 fails the build when a `documented` value names a source that does not exist on disk.

**Why this field exists.** In the case that produced this standard, an artifact shipped figures described as "documented" and "traced to source docs" which were really inherited from an earlier *summary of itself* — the generator read the previous output instead of the sources. Nothing in the system could contradict the claim, because "documented" was prose. Making it a field with an enforced obligation turns it into something a check can refute. **The first `--audit` run failed all 243 claims** (recorded paths were folder-relative rather than repo-relative) and simultaneously exposed two data scripts writing to the working directory instead of their data folder.

### Ledger shape

`_data/_lineage.json`, keyed by the address a reader actually sees:

```json
{
  "sheets": {
    "🤖Salary": {
      "stamped": "2026-08-30",
      "cells": {
        "C20": {
          "value": 87300.0,
          "confidence": "documented",
          "source": "employment-records/0-records/7-Armaris/Slip/2025-06.pdf",
          "method": "payslip earnings, BASE component (the recurring salary line)",
          "inputs": ["_data/_payslip_detail.json#2025-06"],
          "chain": ["payslip PDF", "_payslip_sweep.py", "_slips.json",
                    "_payslip_detail_build.py", "_payslip_detail.json", "build_salary.py"]
        }
      }
    }
  }
}
```

`method` and `chain` are what answer *how it was processed* — without them the ledger says where a number lives, not how it got there.

### The query tool is part of the deliverable

A ledger nobody can query is a file nobody reads. Ship a lookup beside it (`spec-lineage-reference.py` is the reference implementation):

```
_where.py "<Unit>!<Cell>"    one value — confidence, source (checked on disk), method, chain
_where.py <number>           every recorded cell holding that value
_where.py --audit            every `documented` claim, source-verified; exit 1 on failure
_where.py                    coverage summary
```

❗ **An unrecorded value must report as UNVERIFIED, never as absent-therefore-fine.** Partial coverage is normal and honest; silence that reads as assurance is not.

### Root alignment — rule 7

7. **Lineage claims resolve** — every `documented` record in `_data/_lineage.json` names a source path that exists. Prose sources (not paths) are exempt; a path that does not resolve is `⚠ DRIFT`. Coverage itself is **not** mandated per-value — an artifact may record some values and not others — but the ledger must state which, and unrecorded values must never be reported as documented.

### Maintenance rules (lineage)

- **Never hand-edit the ledger.** It is builder-written output; editing it by hand is the same category of error as hand-editing a generated artifact.
- **Re-emit on every rebuild.** A builder rewrites its own sheet's block, so stale records cannot survive a regeneration.
- **A value that changes confidence is a finding, not a tidy-up.** `estimated → documented` means a source was found; `documented → estimated` means a claim was withdrawn. Both belong in the spec's known-gaps section.
- **Record the method even when it is obvious.** "SUM over the month rows" costs one line and saves the next session re-deriving it.

---

### Maintenance rules

- **Spec first, then builder.** Changing what a unit contains means editing its spec in the same turn as the builder. A builder that no longer matches its spec is drift.
- **Specs are current-truth, overwritten in place** — they describe what the unit *is now*, never a dated history of what it was. Dated records stay in `_history.md`.
- **A new unit is not "done" until** its spec exists, its builder is in `0-script/`, and the manifest names both.
- **Deleting a unit** removes its spec, its builder, and its manifest record together — the check in §2 exists because these three drift apart otherwise.
- **In-place artifacts declare every foreign unit**, not just the owned ones. The `owner: user` records are the guard rail; omitting them leaves the next session with no way to know what it must not touch.

