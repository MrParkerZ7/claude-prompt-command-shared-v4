---
skill: md-workflow
role: workflow
capability: markdown-workflow-doc
ships-command: md-workflow
bundle-id: md-workflow-2026-08-02
bundle-tier: full
body: full
native-hint: shared/workflows/md-workflow.md
---

# Workflow: `md-workflow` — author a styled Markdown workflow document

## Purpose

Turn a **process / skill / pipeline** into a single, self-contained **Markdown workflow document** — not one diagram, but a structured doc that combines a **mind map**, a **process flowchart**, supporting tables, and a non-negotiables section, all in the diagrams-skill theme-safe style. The durable "how X works, end-to-end" reference a human opens once to understand or re-run a process.

## When to use vs neighbours

| Want | Use |
|---|---|
| One standalone diagram in a `.md` | `diagram-mindmap-md` / `diagram-flowchart-md` (parametric `diagram-<type>-md`) |
| The full diagram *set* for an analysis project | `analy-diagram` |
| Documenting the **command surface** (`📚docs/`) | `command-docs` |
| **A complete workflow doc for one process** (mind map + flow + tables) | **`md-workflow`** ← this |

## Inputs

```
md-workflow <process> [output-path]
```
- `<process>` — a quoted topic (`"editing a live OneDrive xlsx"`), a skill/command name (resolved via `shared/SKILLS.md` / command tables), or a path to document. Required.
- `[output-path]` — where to write. Defaults to `<scope>/docs/` (or `focus`/`target` when set). One file: `<slug>-workflow.md`.

## Output structure (fixed section order)

1. **Title + one-line intro** (blockquote) — what the doc covers + where it was distilled from.
2. **Key paths (absolute)** — a table of every file/folder the process touches, as **full absolute paths** (never relative fragments — a workflow doc is read out of context).
3. **The Mind Map** — a **styled `flowchart LR` branch graph** (the `mindmap` type doesn't honour per-branch `classDef`, so a branch graph is used to get theme-safe colour). Root → the process's phases → each phase's key points.
4. **The Process Flowchart** — a `flowchart TD` of the actual run, **including the decision nodes and failure/retry loops that really bite** (not just the happy path).
5. **Method / engine table** — the how-per-case (tool choice, guard, why).
6. **Pitfalls** — the walls + their workarounds.
7. **Non-negotiables / invariants** — the rules that must hold (grounded in the source skill, e.g. the `excel-edit` read-first contract).

Sections 5–7 are included when the process has that content; 1–4 are always present.

## Diagram style invariants (diagrams-skill, theme-safe — mandatory)

- Every `classDef` carries **`color:#1f2937`** on its pastel fill (root node may invert: dark fill + `color:#ffffff`) — so it reads in both light and dark Mermaid themes.
- **All node labels quoted** (`["…"]`, `{"…"}`); `<br/>` for line breaks; **no bare `<`/`>`** inside labels (Mermaid eats them as HTML — write "cached values", not `<v>`).
- **Consistent shapes; difference encoded by colour class, not bespoke shapes** (per the diagram-visual-consistency rule) — a shared semantic palette: `action`/`phase` indigo · `decision` amber · `danger` red · `verify` sky · `sync`/`good`/`success` green · `leaf` light-indigo.
- **No reserved `end` node id**; balanced code fences; dotted `-.label.->` for cross-lane hand-offs.

## Protocol

```
resolve <process> ──► outline phases + happy-path + failure loops ──► author mind map + flowchart (theme-safe) ──► fill tables + invariants ──► write <slug>-workflow.md ──► open it
```

1. **Resolve** the subject: read the source skill/command spec or inspect the process so the doc is **grounded, not invented** — every node/step maps to real behaviour; be terse where the source is thin.
2. **Outline** the phase list (mind-map branches) and the run sequence + its real decision/retry loops (flowchart).
3. **Author** both diagrams under the style invariants above.
4. **Fill** the method/pitfall tables and the invariants section from the source.
5. **Write** one `.md` at the output path and **open it** (produce-as-file rule) so the Mermaid renders in preview.

## Notes

- **Grounded, no invented behaviour** — if the process's detail is thin, keep the doc terse; do not fabricate steps.
- Read-only w.r.t. the process it documents; writes only the one `.md`.
- Adding/So-renaming this command makes `CMDs.md` + `📚docs/` stale — rerun `command-list` / `command-docs`.
