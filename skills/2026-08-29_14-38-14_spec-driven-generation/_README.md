# spec-driven-generation

> **Exported:** 2026-08-29 14-38-14 UTC
> **Bundle spec version:** 3.2
> **Bundle tier:** full

Every generated artifact — a workbook, a document, a diagram set, a generated site — is produced from a **written spec**, never from a builder script alone. The spec is the contract; the script is one implementation of it.

The standard ships three things: the **contract** (`1-analysis/spec_<artifact-slug>/<unit>.md`, eight mandatory sections; a **manifest v2** field set adding `spec`/`units`/`owner`/`builder`/`edit_mode`/`live_target`; six mechanically-checkable **root-alignment** invariants), a **generic alignment checker**, and a Claude Code **Stop hook** that refuses to end a turn when a builder changed but its spec did not.

**Commands shipped:** none — a standard plus an enforcement gate, consulted by every `generate*` / `sync` run rather than invoked.
**Self-contained:** yes — the three files cross-reference only each other; the two upstream pointers (`shared/OUTPUTS.md` § Stage Provenance, `shared/PROJECTS.md` § Production scripts) ship as plain path text, not links.
**Portable:** partly — see *Portability* below. The contract is universal; the Stop hook is Claude-Code-specific.

## Why it exists

Three production failures, all observed before the standard was written:

1. **Builders die with the session.** Written into a scratchpad, never persisted; the artifact becomes unmaintainable and the next session reverse-engineers it or rebuilds from scratch.
2. ❗ **Nothing records ownership.** For an artifact edited *in place* — a live workbook, a shared document — where some units belong to the user and must never be rewritten, a script says nothing about which those are. A new session can destroy user data while believing it is doing a routine regeneration.
3. **Hard-won derived facts evaporate.** The forensics behind a column lives only in the conversation that produced it, and the next session silently re-derives it wrongly.

The spec fixes all three: it is persisted, it declares ownership per unit, and it carries the reasoning.

## Role inventory

| Role | Count | Files |
|---|---|---|
| spec | 1 | `specs/SPEC_DRIVEN_GENERATION.md` |
| workflow | 1 | `workflows/spec-check-reference.py` |
| template | 1 | `templates/guard-spec-sync.mjs` |

## What's inside

### Canonical files (define the skill)

| File | Role | Capability |
|---|---|---|
| `specs/SPEC_DRIVEN_GENERATION.md` | spec | spec-driven-generation-standard |
| `workflows/spec-check-reference.py` | workflow | spec-alignment-checker |
| `templates/guard-spec-sync.mjs` | template | spec-sync-stop-gate |

### Auto-inlined dependencies (other skills' files this skill needs)

**(none inlined — deliberate.)** Manifest v2 is *additive over* the v1 stage-provenance schema owned by the `folder-structure-workflow` skill (`shared/OUTPUTS.md` § Stage Provenance), and the layout assumes that skill's stage tree. Inlining it would drag in the whole folder/project-file standard, which most receivers either already have or have their own version of. A receiver with **any** staged output layout can adopt this standard against it; a receiver with **none** should take `folder-structure-workflow` first.

## Portability

| Piece | Portable? |
|---|---|
| `specs/SPEC_DRIVEN_GENERATION.md` | ✅ universal — a written contract, no tooling assumptions beyond a staged output layout |
| `workflows/spec-check-reference.py` | ✅ generic — reads the output stage's `_manifest.json` and validates whatever it declares; no project-specific logic. Needs Python 3 (+ `openpyxl` only for the optional `--live` check) |
| `templates/guard-spec-sync.mjs` | ⚠ **Claude Code only** — a `Stop` hook wired via `.claude/settings.json`, needs Node. A non-Claude-Code receiver should drop it and enforce the rule in review, or port the two checks it performs |

**Non-markdown frontmatter:** `.py` / `.mjs` files carry their bundle frontmatter as a **comment block** (`# ---` / `// ---`) so they stay runnable. `MANIFEST.md` carries the same fields authoritatively — the spec does not define frontmatter for non-markdown files, so this is a documented extension. Likewise `specs/` and `templates/` extend the spec's documented `agents/` `prompts/` `workflows/` bundle folders to the `spec` and `template` roles.

## How to use

### Option A — External (any Claude, any structure)
Read this `_README.md`, then `specs/SPEC_DRIVEN_GENERATION.md`. Adopt the contract against whatever output layout you already have: create one spec per addressable unit of each generated artifact, record `spec` / `owner` / `builder` in your output manifest, and run `workflows/spec-check-reference.py <project-root>` to verify alignment. **No setup required.**

### Option B — Native (Claude Code root-master with matching `shared/` layout)
`command-import <path-to-this-bundle> --mode=native`. The importer reads `MANIFEST.md` and places files by `role:` — the spec to `shared/`, the checker to `shared/workflows/`, the hook to `shared/templates/`. ❗ **Then move the hook yourself** to `.claude/hooks/guard-spec-sync.mjs` and wire it into `.claude/settings.json` under `Stop` — placement by role cannot know about your hook directory. Hook config snapshots at session start, so it arms from the **next** session.

### Option C — Hybrid
`command-import <path-to-this-bundle> --map spec=<your-standards-path> --map workflow=<your-scripts-path>`.

## Wiring it in (what the source master did)

The standard is inert unless something enforces it. In the source master it was wired at five points:

| Where | What |
|---|---|
| every project-type spec | a sync-target line requiring the alignment check |
| the `sync` workflow | runs the six checks, reports `⚠ DRIFT`, **never auto-repairs** |
| the execution protocol | the spec is written in the **same transaction** as the artifact — a generated file whose spec is missing or stale is an *incomplete write* |
| every `generate*` command | authors/refreshes the spec before writing |
| the `Stop` hook | blocks the turn when a builder changed but no spec did |

## The one rule worth copying verbatim

❗ For an artifact edited **in place**, declare **every** foreign unit as `owner: user` / `policy: never-write`. That record is the only thing standing between the next session and destroying the user's data. A builder declared on an `owner: user` unit is an **error, not a warning**.
