# Bundle Manifest

**Bundle name:** claude-skills-shared-v4
**Created:** 2026-08-02 21:02 UTC (latest export: 2026-08-30 14:28:25 UTC)
**Bundle spec version:** 3.2
**Bundle tier:** full

---

## Skill: spec-driven-generation

```yaml
bundle-tier: full
files:
  - bundle: skills/2026-08-30_14-28-25_spec-driven-generation/specs/SPEC_DRIVEN_GENERATION.md
    role: spec
    skill: spec-driven-generation
    capability: spec-driven-generation-standard
    ships-command: null
    body: full
    native-hint: shared/SPEC_DRIVEN_GENERATION.md
    sha256: 4ecfaa5e10ae7a85703f2c78401eb238fea7ecca9872e789e9da2e23b85575b3
  - bundle: skills/2026-08-30_14-28-25_spec-driven-generation/workflows/spec-check-reference.py
    role: workflow
    skill: spec-driven-generation
    capability: spec-alignment-checker
    ships-command: null
    body: full
    native-hint: shared/workflows/spec-check-reference.py
    sha256: 5bb4018e12612f68b92d37593f799c702a37faba67c7f21fd6f1e2cb7a06417a
  - bundle: skills/2026-08-30_14-28-25_spec-driven-generation/workflows/spec-lineage-reference.py
    role: workflow
    skill: spec-driven-generation
    capability: value-lineage-ledger
    ships-command: null
    body: full
    native-hint: shared/workflows/spec-lineage-reference.py
    sha256: 49c9af468e81c931164fd638be1c7c2af8de94baa08561c3c163f2703dcde76b
  - bundle: skills/2026-08-30_14-28-25_spec-driven-generation/workflows/spec-where-reference.py
    role: workflow
    skill: spec-driven-generation
    capability: value-lineage-query
    ships-command: null
    body: full
    native-hint: shared/workflows/spec-where-reference.py
    sha256: f95a8f79696f554cb791c65479bfd482343478e4ccc52fdd76237664bf41019a
  - bundle: skills/2026-08-30_14-28-25_spec-driven-generation/templates/guard-spec-sync.mjs
    role: template
    skill: spec-driven-generation
    capability: spec-sync-stop-gate
    ships-command: null
    body: full
    native-hint: .claude/hooks/guard-spec-sync.mjs
    sha256: 9e22feafa40e9c443ec2039aa5451076830a6d87a715981798c3dc711fb63ebb
```

**depends-on:** `folder-structure-workflow` — NOT inlined.
**Supersedes:** the 2026-08-29 snapshot of this skill (prior snapshots are retained).

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
