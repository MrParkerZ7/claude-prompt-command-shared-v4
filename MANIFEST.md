# Bundle Manifest

**Bundle name:** claude-skills-shared-v4
**Created:** 2026-08-02 21:02 UTC (latest export: 2026-08-29 14:38:14 UTC)
**Bundle spec version:** 3.2
**Bundle tier:** full

---

## Skill: spec-driven-generation

```yaml
bundle-tier: full
files:
  - bundle: skills/2026-08-29_14-38-14_spec-driven-generation/specs/SPEC_DRIVEN_GENERATION.md
    role: spec
    skill: spec-driven-generation
    capability: spec-driven-generation-standard
    ships-command: null
    body: full
    native-hint: shared/SPEC_DRIVEN_GENERATION.md
    sha256: c20253737af8c04258ffa7aca6260b9c7f2488f0b3a7aa199e973eaf2fe5087d
  - bundle: skills/2026-08-29_14-38-14_spec-driven-generation/workflows/spec-check-reference.py
    role: workflow
    skill: spec-driven-generation
    capability: spec-alignment-checker
    ships-command: null
    body: full
    native-hint: shared/workflows/spec-check-reference.py
    sha256: cf7c933dfc90e190b640e3c16bdea6f7e4bc654c0a9807318563042b36a6a53f
  - bundle: skills/2026-08-29_14-38-14_spec-driven-generation/templates/guard-spec-sync.mjs
    role: template
    skill: spec-driven-generation
    capability: spec-sync-stop-gate
    ships-command: null
    body: full
    native-hint: .claude/hooks/guard-spec-sync.mjs
    sha256: 42c2f037268df6af9ec6cd999bb93b8023ea6b4f7d768c4e54761db487f20fcc
```

**depends-on:** `folder-structure-workflow` — NOT inlined (manifest v2 extends its v1 provenance schema; upstream pointers ship as plain path text).

---

## Skill: md-workflow

```yaml
bundle-tier: full
files:
  - bundle: skills/2026-08-02_21-02-18_md-workflow/workflows/md-workflow.md
    role: workflow
    skill: md-workflow
    capability: markdown-workflow-doc
    ships-command: md-workflow
    body: full
    native-hint: shared/workflows/md-workflow.md
    sha256: e178f8e42292b981d33bdfce795ece621a427786b15912eed683249ee37a98e3
```
