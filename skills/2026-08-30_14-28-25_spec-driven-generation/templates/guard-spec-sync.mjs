#!/usr/bin/env node
// ---
// skill: spec-driven-generation
// role: template
// capability: spec-sync-stop-gate
// ships-command: null
// bundle-id: spec-driven-generation-2026-08-30
// bundle-tier: full
// body: full
// native-hint: .claude/hooks/guard-spec-sync.mjs
// ---
// Stop hook — SPEC-SYNC GATE.
//
// Enforces the user's standing rule (2026-08-29): "everytime output file structure / format /
// pattern / formula update, spec also must be updated — please make sure this one always be."
//
// Prose cannot guarantee that; a hook can. The mechanical proxy: you cannot change a generated
// artifact's structure, format, pattern or formula WITHOUT changing its builder. So:
//
//   (1) DIFF CHECK  — if a builder under `**/0-script/` changed in the working tree but no file
//       under a `**/1-analysis/spec_*/` folder changed, the spec is stale. BLOCK.
//   (2) ALIGNMENT   — if `**/0-script/_lib/_spec_check.py` exists, run it (the six root-alignment
//       invariants from specs/SPEC_DRIVEN_GENERATION.md). Non-zero → BLOCK.
//
// Roots probed: the hook's cwd (the repo the session launched in) and the session's `target:`
// resolved from `.claude/sessions/session-memories-<session_id>.md` — same resolution as
// stop-quality-gate.mjs, because sessions launch in this master but do their work in a target.
//
// One-shot user override: create `<root>/.claude/allow-spec-drift` — consumed on use, so only
// the USER authorizes shipping a stale spec, and only once (mirrors guard-test-weakening.mjs).
//
// HONEST LIMITS (do not oversell):
//  - FAILS OPEN on any error, missing git/python, or timeout. A check that cannot run is not red.
//  - The diff check is a HEURISTIC at repo granularity: it verifies *some* spec changed, not that
//    the *right* spec was updated with the *correct* content. It kills the cheap failure (edit the
//    builder, forget the spec entirely); prose rules + review own semantic correctness.
//  - Config snapshots at session start — this hook applies from the NEXT session.
//  - Not bypass-proof (refuted 0-3). A strong backstop over the CLAUDE.md rules, not a guarantee.
import { readFileSync, existsSync, unlinkSync, readdirSync } from 'node:fs';
import { spawnSync } from 'node:child_process';
import { join } from 'node:path';

let input = {};
try {
  input = JSON.parse(readFileSync(0, 'utf8'));
} catch {
  process.exit(0);
}
if (input?.stop_hook_active) process.exit(0); // loop guard — we already blocked once

const TIMEOUT_MS = Number(process.env.SPEC_SYNC_TIMEOUT_MS || 60000);

const roots = new Set([process.cwd()]);
const sid = input?.session_id;
if (sid && /^[\w-]+$/.test(String(sid))) {
  try {
    const state = readFileSync(
      join(process.cwd(), '.claude', 'sessions', `session-memories-${sid}.md`),
      'utf8',
    );
    const m = /^target:\s*(.+?)\s*$/m.exec(state);
    if (m?.[1]) roots.add(m[1].trim());
  } catch {} // no state file / no target → cwd-only probe
}

const isBuilder = (p) =>
  /(^|\/)0-script\/[^/]+\.py$/.test(p) && !/(^|\/)0-script\/(_lib|_data)\//.test(p);
const isSpec = (p) => /(^|\/)1-analysis\/spec_[^/]+\//.test(p);

for (const root of roots) {
  if (!existsSync(join(root, '.git'))) continue;

  // ---- gather working-tree changes ----
  const st = spawnSync('git', ['status', '--porcelain'], {
    cwd: root, encoding: 'utf8', timeout: TIMEOUT_MS,
  });
  if (st.error || st.status !== 0) continue; // no git / not a repo → fail open

  const paths = [];
  for (const line of (st.stdout || '').split(/\r?\n/)) {
    if (!line.trim()) continue;
    let p = line.slice(3).trim();
    if (p.includes(' -> ')) p = p.split(' -> ').pop().trim(); // rename → destination
    if (p.startsWith('"') && p.endsWith('"')) p = p.slice(1, -1);
    paths.push(p.replace(/\\/g, '/'));
  }
  if (!paths.length) continue;

  const builders = paths.filter(isBuilder);
  const specs = paths.filter(isSpec);

  const override = join(root, '.claude', 'allow-spec-drift');
  const takeOverride = () => {
    if (!existsSync(override)) return false;
    try { unlinkSync(override); } catch {}
    process.stderr.write(
      `guard-spec-sync: one-shot override consumed at ${root} — spec drift allowed for this turn only.\n`,
    );
    return true;
  };

  // ---- (1) DIFF CHECK ----
  if (builders.length && !specs.length) {
    if (!takeOverride()) {
      process.stderr.write(
        `BLOCKED by guard-spec-sync hook: a generated artifact's BUILDER changed but its SPEC did not.\n\n` +
          `Changed builder(s) in ${root}:\n` +
          builders.map((b) => `  - ${b}`).join('\n') +
          `\n\nNo file under any 1-analysis/spec_*/ folder was touched. Per the user's standing rule and\n` +
          `specs/SPEC_DRIVEN_GENERATION.md, a change to an output's STRUCTURE, FORMAT, PATTERN\n` +
          `or FORMULA must update that unit's spec in the SAME turn — the spec is the contract, the builder\n` +
          `is only one implementation of it. A stale spec silently misleads the next session.\n\n` +
          `Fix: update the matching 1-analysis/spec_<artifact-slug>/<unit>.md — its §3 Structure, §4 Derivation\n` +
          `and §5 Presentation sections — to describe what the builder now produces. Then finish.\n` +
          `If the edit genuinely changed no output contract (a comment, a path fix, a refactor), the USER may\n` +
          `authorize skipping once by creating ${override}\n`,
      );
      process.exit(2);
    }
  }

  // ---- (2) ALIGNMENT CHECK ----
  // find every 0-script/_lib/_spec_check.py at the root or one level down (sub-project layouts)
  const cands = ['0-script/_lib/_spec_check.py'];
  try {
    for (const d of readdirSync(root, { withFileTypes: true })) {
      if (d.isDirectory() && !d.name.startsWith('.')) cands.push(`${d.name}/0-script/_lib/_spec_check.py`);
    }
  } catch {}
  for (const cand of cands) {
    const script = join(root, cand);
    if (!existsSync(script)) continue;
    const run = spawnSync('python', [script], {
      cwd: root, encoding: 'utf8', timeout: TIMEOUT_MS,
    });
    if (run.error || run.status === null) {
      process.stderr.write(
        `guard-spec-sync: alignment check at ${cand} did not complete (${run.error?.code ?? 'timeout'}) — failing open\n`,
      );
      continue;
    }
    if (run.status === 0) continue;
    if (takeOverride()) continue;
    const tail = `${run.stdout ?? ''}\n${run.stderr ?? ''}`
      .trim().split(/\r?\n/).filter((l) => /DRIFT|drift item/.test(l)).slice(-15).join('\n');
    process.stderr.write(
      `BLOCKED by guard-spec-sync hook: spec/artifact ROOT ALIGNMENT is broken in ${root}.\n\n${tail}\n\n` +
        `These are the six invariants in specs/SPEC_DRIVEN_GENERATION.md → "Root alignment".\n` +
        `Fix the drift — never auto-repair by deleting a spec; the correct fix may be the spec OR the\n` +
        `manifest OR the builder, and each rule names which. Then finish.\n`,
    );
    process.exit(2);
  }
}
process.exit(0);
