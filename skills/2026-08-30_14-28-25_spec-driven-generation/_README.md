# spec-driven-generation

> **Exported:** 2026-08-30 14:28:25 UTC
> **Bundle spec version:** 3.2 · **Tier:** full
> **Supersedes:** `2026-08-29_14-38-14_spec-driven-generation` (that snapshot stays in place — v3.2 snapshots accumulate)

Every generated artifact is produced from a **written spec**, never from a builder script alone — and every **figure** in it can be traced back to the document it came from.

**What's new in this snapshot:** ★ **value lineage**. The original shipped the contract, the alignment checker and the Stop hook. Those answered *how is this artifact shaped* and *which files fed it*. They did not answer the question a later session actually has: **"where did this number come from, and how was it computed?"** This snapshot adds the ledger, the query tool and a seventh alignment invariant that makes `documented` a checkable claim rather than a label.

## Role inventory

| Role | Count | Files |
|---|---|---|
| spec | 1 | `specs/SPEC_DRIVEN_GENERATION.md` |
| workflow | 1 | `workflows/spec-check-reference.py` |
| workflow | 1 | `workflows/spec-lineage-reference.py` |
| workflow | 1 | `workflows/spec-where-reference.py` |
| template | 1 | `templates/guard-spec-sync.mjs` |

## What's inside

| File | Role | Capability |
|---|---|---|
| `specs/SPEC_DRIVEN_GENERATION.md` | spec | spec-driven-generation-standard |
| `workflows/spec-check-reference.py` | workflow | spec-alignment-checker |
| `workflows/spec-lineage-reference.py` | workflow | value-lineage-ledger |
| `workflows/spec-where-reference.py` | workflow | value-lineage-query |
| `templates/guard-spec-sync.mjs` | template | spec-sync-stop-gate |

## Why value lineage exists

In the case that produced this standard, an artifact shipped figures described as "documented" and "traced to source docs" that were really inherited from an **earlier summary of itself** — the generator read its own previous output instead of the sources. Nothing in the system could contradict the claim, because "documented" was prose.

Making it a **field with an enforced obligation** turns it into something a check can refute. The first `--audit` run failed **all 243 claims** (recorded paths were folder-relative, not repo-relative) and simultaneously exposed two data scripts writing to the working directory instead of their data folder. Both were invisible until the claim became checkable.

## Confidence vocabulary (closed)

| | meaning |
|---|---|
| `documented` | a source document states it — **must** name a path that resolves |
| `derived` | computed from documented figures by the stated method |
| `estimated` | own record, no source document |
| `assumed` | an editable forward-looking input |

## The one rule worth copying verbatim

❗ **The builder records lineage AS IT WRITES EACH CELL, in the same transaction.** A ledger maintained separately drifts from the artifact; one emitted at write time cannot.

❗ And: **an unrecorded value must report as UNVERIFIED**, never as absent-therefore-fine. Partial coverage is honest; silence that reads as assurance is not.

## Portability

| Piece | Portable? |
|---|---|
| `specs/SPEC_DRIVEN_GENERATION.md` | ✅ universal — a written contract |
| `workflows/spec-check-reference.py` | ✅ generic — reads the output stage's `_manifest.json`; Python 3 (`openpyxl` only for the optional `--live` check) |
| `workflows/spec-lineage-reference.py` | ✅ generic — a `Ledger` class a builder imports; no artifact-specific logic |
| `workflows/spec-where-reference.py` | ✅ generic — reads the ledger; keyed by whatever address your artifact uses |
| `templates/guard-spec-sync.mjs` | ⚠ **Claude Code only** — a `Stop` hook wired via `.claude/settings.json`, needs Node |

**Non-markdown frontmatter** ships as a comment block (`# ---` / `// ---`) so the scripts stay runnable; `MANIFEST.md` is authoritative. `specs/` and `templates/` extend the spec's documented `agents/ prompts/ workflows/` bundle folders to the `spec` and `template` roles.

## How to use

**External (any Claude):** read `specs/SPEC_DRIVEN_GENERATION.md`, adopt the contract against whatever output layout you have, then `workflows/spec-check-reference.py <project-root>` to verify alignment. For lineage, have your builder import `Ledger` from `spec-lineage-reference.py` and query with `spec-where-reference.py`.

**Native (Claude Code root-master):** `command-import <bundle> --mode=native`. ❗ Then move the hook to `.claude/hooks/` and wire it under `Stop` in `.claude/settings.json` — role-based placement cannot know about your hook directory. Hook config snapshots at session start, so it arms from the next session.

**depends-on:** `folder-structure-workflow` — not inlined (manifest v2 is additive over its v1 provenance schema).
