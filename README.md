# claude-prompt-command-shared-v4

Portable skill-bundle repository produced by `command-export` (Export Bundle Spec **v3.2**). Each skill lives under `skills/<YYYY-MM-DD_HH-MM-SS>_<skill>/` as an independent, timestamp-prefixed snapshot — snapshots accumulate (prior ones are never modified or deleted), so a directory listing sorts chronologically and every export is recoverable at a stable path.

Every bundle is **self-contained** (all cross-references resolve inside its own folder) and **self-describing** (each file carries `role:`/`capability:`/`body:` frontmatter), so it works for any Claude consumer — drop it in verbatim (external mode) or weave it into a matching `shared/` layout via `command-import --mode=native`.

## Skills (latest snapshot per skill)

| Skill | Latest snapshot | Tier | Commands | Entry point |
|---|---|---|---|---|
| spec-driven-generation | `skills/2026-08-30_14-28-25_spec-driven-generation/` | full | (none) | [`_README.md`](skills/2026-08-30_14-28-25_spec-driven-generation/_README.md) |
| md-workflow | `skills/2026-08-02_21-02-18_md-workflow/` | full | `md-workflow` | [`_README.md`](skills/2026-08-02_21-02-18_md-workflow/_README.md) |

## How to consume

- **External (any Claude, any structure):** open the snapshot folder's `_README.md` and follow it. No setup.
- **Native (root-master with matching `shared/`):** `command-import <this-repo> --mode=native`.
- **Hybrid (partial match):** `command-import <this-repo> --map workflows=<path>`.

See each snapshot's `_README.md` for its role inventory and the command row to register.

## Snapshot history

| Timestamp (UTC) | Skill | Tier | Snapshot folder |
|---|---|---|---|
| 2026-08-30 14:28:25 | spec-driven-generation | full | `skills/2026-08-30_14-28-25_spec-driven-generation/` |
| 2026-08-29 14:38:14 | spec-driven-generation | full | `skills/2026-08-29_14-38-14_spec-driven-generation/` |
| 2026-08-02 21:02:18 | md-workflow | full | `skills/2026-08-02_21-02-18_md-workflow/` |
