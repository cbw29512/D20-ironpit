# Current operating status

Updated 2026-10-15. This is a short navigation/status page, **not** a second monster queue or a certification manifest. Use the [documentation map](DOCUMENTATION_MAP.md) and [execution manual](IRON_PIT_IMPLEMENTATION_PLAYBOOK.md) for the operating path.

## Authoritative sources

- [SOUL.md](../SOUL.md) — universal combat philosophy and source/engine ownership.
- [Monster ability work queue](MONSTER_ABILITY_WORK_QUEUE.md) — approved decisions and **current implementation cursor**.
- [Generated 2014 monster blockers](MONSTER_BLOCKERS_2014.md) — currently blocked source monsters and reasons; never hand-edit.
- [Generated universal mechanic inventory](UNIVERSAL_MECHANIC_INVENTORY.md) — supported and unresolved universal capabilities; never hand-edit.
- [Monster implementation guide](playbooks/MONSTERS.md) — implementation, throughput and certification protocol.
- [Two-agent coordination](TWO_AGENT_COORDINATION.md) — branch ownership and collision avoidance.

If this page conflicts with the generated reports or current source/CI, **the reports and current source/CI win**.

## Current monster admission and blockers

The admission count is generated and changes after merges; do not use this document as a live count. Read [MONSTER_BLOCKERS_2014.md](MONSTER_BLOCKERS_2014.md) and [UNIVERSAL_MECHANIC_INVENTORY.md](UNIVERSAL_MECHANIC_INVENTORY.md) at the exact `main` commit being audited. Source admission is **not** whole-match certification. Python is the reference oracle; the browser is the production combat engine. Netlify publication remains locked.

## Implementation order

1. Read the canonical queue and source blocker report. Skip merged work and existing active PRs.
2. Prioritize source-approved, one-blocker combat monsters and shared semantic families that can unblock several creatures.
3. Before edits, reconcile open PR ownership; duplicate source files or universal resolvers must not be implemented in parallel.
4. For the selected ability: verify pinned 2014 source; decompose behavior; reuse universal mechanics; bind immutable card parameters; retain printed source names in logs.
5. Test Python and browser behavior, verify fight-state reset, regenerate owned artifacts, and certify the **exact final PR head**.
6. After merge, measure resolved source obligations and whole-monster admissions against the previous generated inventory. Only then advance the queue.

No artificial blocker exemptions, removal of outcome-changing RAW abilities, runtime dispatch on source names, weakening of certification checks, or automatic production deployment.
