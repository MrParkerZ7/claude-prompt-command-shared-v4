# md-workflow

> **Exported:** 2026-08-02 21:02:18 UTC
> **Bundle spec version:** 3.2
> **Bundle tier:** full

Author a styled Markdown **workflow document** for a process / skill / pipeline — not one diagram but a complete, self-contained doc: a theme-safe Mermaid **mind map** (branch graph) + a **process flowchart** (decision nodes + the real failure/retry loops) + supporting tables (method/engine · pitfalls · **key paths as ABSOLUTE paths**) + a non-negotiables/invariants section grounded in the source skill. The durable "how X works, end-to-end" reference a human opens once to understand or re-run a process.

**Commands shipped:** `md-workflow`
**Self-contained:** yes — the single workflow file cross-references no other file; the one upstream pointer (`shared/SKILLS.md`, describing how the `<process>` arg resolves) is de-linkified to plain path text.
**Portable:** yes — works for any Claude consumer without requiring this repo's `shared/` layout.

## Role inventory

| Role | Count | Files |
|---|---|---|
| workflow | 1 | `workflows/md-workflow.md` |

## What's inside

### Canonical files (define the skill)

| File | Role | Capability |
|---|---|---|
| `workflows/md-workflow.md` | workflow | markdown-workflow-doc |

### Auto-inlined dependencies (other skills' files this skill needs)

(none — fully self-contained construction skill)

## How to use

### Option A — External (any Claude, any structure)
Read this `_README.md`, then open `workflows/md-workflow.md`. It has no external references — invoke it directly against a process/skill/topic and it produces one `<slug>-workflow.md`. **No setup required.**

### Option B — Native (Claude Code root-master with matching `shared/` layout)
Run `command-import <path-to-this-bundle> --mode=native` from your root-master. The importer reads `MANIFEST.md`, places `workflows/md-workflow.md` into your `shared/workflows/`, and registers the skill + `md-workflow` command per the block below.

### Option C — Hybrid (root-master with partial structure match)
Run `command-import <path-to-this-bundle> --map workflows=<your-workflows-path>`.

## Command to register (CLAUDE.md row — copy-paste block)

The skill ships one command. Add this row to your command surface (e.g. a generic-commands table). Diagrammer is the lead role in the source master:

```markdown
| `md-workflow <process>` | **Author a styled Markdown WORKFLOW DOCUMENT** for a process / skill / pipeline — not one diagram but a complete doc: a theme-safe Mermaid **mind map** (branch graph) + a **process flowchart** (decision nodes + the real failure/retry loops) + supporting tables (method/engine · pitfalls · **key paths as ABSOLUTE paths**) + a non-negotiables/invariants section grounded in the source skill. Diagrams follow the diagrams-skill theme-safe standard (every `classDef` carries `color:#1f2937` on a pastel fill; labels quoted; consistent shapes—difference by colour not bespoke shape; no reserved `end` id; balanced fences). Args: `<process>` (quoted topic · skill/command name · path) `[output-path]` (defaults to `<scope>/docs/` or `focus`/`target`) → writes one `<slug>-workflow.md`, then opens it. Use for "document how X works as a workflow"; use `diagram-mindmap-md`/`diagram-flowchart-md` for a single standalone diagram. See `shared/workflows/md-workflow.md`. | Diagrammer |
```
