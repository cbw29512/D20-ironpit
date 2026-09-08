# Iron Pit Completion Ledger

This ledger is a human-readable checkpoint only. The authoritative machine state remains:

- `data/monster_certification_manifest.json`
- `data/canonical_progression_engine_audit.json`
- `data/roster_combat_mechanics_v1.json`
- `data/combat_engine_coverage_v1.json`
- exact-head CI

Do not mark content complete from this file alone. Regenerate and verify the authoritative artifacts first.

## Current checkpoint

Branch: `feat/usable-roster-warlock-l1`

Re-anchored generated head before this checkpoint: `f9d76efe36ef0587e90c54306da117b9763a9910`

### Monsters

- Canonical SRD monsters: **330**
- Public-ready in the current generated manifest: **119**
- Blocked: **211**
- Latest earned promotion: **Killer Whale**, after removing the obsolete aquatic-only arena defer. Its printed movement modes remain intact; the Iron Pit's magical hospitality changes eligibility only, not combat movement data.

### Canonical pregen progression

- Canonical classes: **12**
- Level snapshots audited: **240** (12 classes × levels 1–20)
- Certified pregen snapshots at this checkpoint: **24 / 240**
- Level-1 engine-ready classes in the regenerated progression audit: **9 / 12**
- Current genuine Level-1 blockers: `martial-arts`, `hunters-mark`, `innate-sorcery`
- `bardic-inspiration` is explicitly classified from canonical Bard metadata as `arena_out_of_scope` for Iron Pit's solo duel rather than being falsely treated as a missing runtime mechanic.

### Progression-audit correction

The progression audit previously calculated canonical `arena_ignored` metadata but did not use it when assigning feature status or blockers. That made arena-excluded features appear as planned engine gaps.

The exporter gives canonical arena-exclusion metadata precedence when deriving effective audit status, and treats `supported` plus `arena_out_of_scope` as non-blocking. A regression test locks this behavior. Bard Level 1 correctly advances from blocked to engine-ready without adding a Bard-specific runtime branch or claiming a mechanic that the arena never uses.

Regenerated audit summary:

- canonical classes: **12**
- level slots: **240**
- unique combat features: **226**
- Level-1 engine-ready classes: **9**
- feature statuses: `arena_out_of_scope=1`, `planned=183`, `supported=42`
- unique blocking features: **183**

### Capability matrix

The capability matrix remains the authoritative declaration layer. No readiness total in this ledger overrides its source/runtime evidence or certification manifests.

### Environmental eligibility correction

The Iron Pit is magically hospitable to every combatant. Aquatic, flying, atmospheric, breathing, and comparable biological/environmental requirements do not block arena eligibility unless they directly change combat math or combat state. Printed movement modes and combat-relevant environmental interactions remain authoritative data; magical hospitality does not rewrite speeds, create exploitable terrain, or approximate a combat mechanic.

The obsolete `Killer Whale -> aquatic-only` defer and swim-only movement rejection were removed as a universal eligibility correction. `Hold Breath` was already classified as combat-irrelevant by the trait source audit, so no monster-specific resolver branch was introduced. Python and browser certification regressions now require the generated Killer Whale while preserving its exact movement and attack fingerprints.

### CI diagnosis

Human implementation head `ceed750bcec598d82223853c06398338480f96af` removed the obsolete environment defer and added Python/browser regressions. The generated-content workflow then promoted the authoritative artifacts at `f9d76efe36ef0587e90c54306da117b9763a9910`, advancing the monster manifest from **118 / 330** to **119 / 330**. GitHub classified CI for that bot-authored promotion as `action_required` before creating certification jobs, matching the repository's prior bot-head behavior.

This checkpoint is intentionally human-authored so normal exact-head PR CI can execute against the already-generated state. No runtime behavior, capability declaration, fingerprint, resource audit, or readiness flag is changed by this ledger commit.

Monster readiness is **119 / 330** because the generated authoritative manifest earned that result. Certified pregen snapshots remain **24 / 240**.

## Locked implementation rules

1. One universal combat engine; no class-name or monster-name resolver branches when a generic capability can model the rule.
2. Monster and pregen cards are immutable source data. Fight state is temporary and discarded after combat.
3. 2024 / SRD 5.2.1 is the current certified ruleset. Unsupported outcome-changing mechanics fail closed.
4. Python is the certification oracle; browser production behavior requires parity and permanent regressions.
5. Step, Watch, Replay, and Turbo consume the same canonical resolver/event path.
6. Exact timing, resource use, conditions, buffs/debuffs, reactions, damage defenses, lethal overrides, summons/forms, and boss mechanics remain auditable.
7. Certification is earned from source/runtime/build/fingerprint/resource evidence; never by flipping readiness flags.
8. Environmental or utility-only requirements are omitted when they cannot alter combat math/state; printed combat movement and actual combat effects are never discarded merely for convenience.

## Next priority

Do not add mechanic scope until exact-head CI executes cleanly on this human checkpoint. Once green, re-run blocker yields under the hospitable-environment rule. The likely next data-only/combat-irrelevant tranche is `Water Breathing` for the five trait-only shark/piranha blockers, but it must be source-audited and earned through the same generation, parity, manifest, and exact-head CI gates before counting.