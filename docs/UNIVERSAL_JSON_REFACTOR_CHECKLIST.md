# Universal JSON Combatant Refactor Checklist

This checklist is the execution queue for the refactor mandated by `docs/IRON_PIT_RULES_CONTRACT.md`.
It is intentionally ordered so future work can resume from repository state rather than chat memory.

## Phase 1 — Lock the common boundary

- [x] Highest-authority universal data-driven combat contract exists.
- [x] Edition-scoped hero progression/subclass JSON schemas exist.
- [x] Generic hero level folding exists.
- [x] Hero build/loadout JSON schema exists.
- [x] 2024 Fighter/Champion/Karnok seed data exists.
- [x] Hero JSON can compile to `CombatantDefinition`.
- [x] Hero `CombatantDefinition` uses the existing `compile_combatant` boundary used by declarative monsters.
- [ ] Add explicit parity proof: representative JSON hero and representative JSON monster both compile to `CombatantTemplate` and expose the same engine-facing field families.
- [ ] Add edition-mismatch rejection test at the common boundary.
- [ ] Add immutable-source/fresh-fight-state regression around compiled JSON combatants.

## Phase 2 — Finish 2024 Fighter migration

- [ ] Compare JSON-compiled Fighter levels 1–17 against the existing audited/certified Fighter fingerprints.
- [ ] Report every mismatch as source-data, compiler, or capability-registry work; do not hide differences.
- [ ] Resolve supported-capability naming/parameter gaps without hero-specific resolvers.
- [ ] Audit levels 18–20 and list their actual unsupported universal capability IDs.
- [ ] Implement only genuinely missing reusable capabilities, with Python/browser parity.
- [ ] Compile/certify Fighter 1–20 from JSON.
- [ ] Switch Fighter runtime/certification registration to the JSON path.
- [ ] Delete obsolete Fighter per-level builders only after permanent parity tests are green.

## Phase 3 — Normalize monster authoring

- [ ] Define/validate edition-scoped monster source schema: stat-block facts + universal capability references.
- [ ] Preserve current SRD source/audit metadata.
- [ ] Compile monster JSON to the same `CombatantDefinition` boundary.
- [ ] Derive values only when RAW inputs make derivation authoritative; retain printed monster values when the stat block is authoritative.
- [ ] Prove representative simple attack, multiattack, save-action, reaction, spellcaster, recharge, resistance/immunity, and condition monsters.
- [ ] Replace generated/legacy monster construction in batches only after parity evidence.
- [ ] Keep 2014 and 2024 monster source data isolated while reusing genuinely identical primitives.

## Phase 4 — Migrate all pregens as data

- [ ] 2024 Barbarian
- [ ] 2024 Bard
- [ ] 2024 Cleric
- [ ] 2024 Druid
- [ ] 2024 Monk
- [ ] 2024 Paladin
- [ ] 2024 Ranger
- [ ] 2024 Rogue
- [ ] 2024 Sorcerer
- [ ] 2024 Warlock
- [ ] 2024 Wizard
- [ ] 2014 Fighter
- [ ] 2014 Barbarian
- [ ] 2014 Bard
- [ ] 2014 Cleric
- [ ] 2014 Druid
- [ ] 2014 Monk
- [ ] 2014 Paladin
- [ ] 2014 Ranger
- [ ] 2014 Rogue
- [ ] 2014 Sorcerer
- [ ] 2014 Warlock
- [ ] 2014 Wizard

For each track: identity/build JSON + class deltas + subclass deltas -> compile 1–20 -> capability audit -> parity/certification -> remove superseded builders.

## Phase 5 — Homebrew/import contract

- [ ] Validate homebrew against the same character/monster schemas.
- [ ] Reject unknown executable behavior/capability IDs.
- [ ] Permit existing universal capability IDs with legal parameters.
- [ ] Provide validation errors that name unsupported/malformed capabilities.
- [ ] Prove official-vs-homebrew, homebrew-vs-homebrew, pregen-vs-monster, PvP, and monster-vs-monster all enter the same engine.

## Phase 6 — Browser/runtime generation

- [ ] Generate browser-ready immutable combatant records from the same compiled source.
- [ ] Verify Python/browser derived-stat and capability parity.
- [ ] Ensure Step/Watch/Replay/Turbo consume the same canonical event stream.
- [ ] Ensure source data is never mutated by a fight.
- [ ] Ensure a new fight restores HP/resources/slots/conditions from immutable compiled source.

## Phase 7 — Certification and cleanup

- [ ] Batch certification reports unsupported capability IDs and every affected combatant.
- [ ] One blocked combatant never stalls unrelated migration/certification work.
- [ ] Regenerate hero and monster manifests from compiler output.
- [ ] Remove duplicate builders, stale snapshots, hand-maintained readiness bookkeeping, and dead adapters after parity.
- [ ] Run technical-debt/source-size pass.
- [ ] Exact-head CI green.
- [ ] 2014 + 2024 pregens complete.
- [ ] 2014 + 2024 monster rosters complete.

## Definition of done

Iron Pit is on the target architecture when official pregens, monsters, and validated homebrew are declarative data that compile into the same immutable combatant representation, create fresh mutable fight state, and resolve through one RAW engine plus explicit Iron Pit arena policy. No combat behavior is selected by a hero, class, subclass, or monster name.
