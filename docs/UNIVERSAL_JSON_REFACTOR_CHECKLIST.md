# Universal JSON Combatant Refactor Checklist

This checklist is the execution queue for the refactor mandated by `docs/IRON_PIT_RULES_CONTRACT.md`.
It is intentionally ordered so future work can resume from repository state rather than chat memory.

`feat/2024-fighter-15-reanchored` is parked. It mixed live Fighter 15–17 Python builders with a JSON compiler whose "class table" was actually Karnok. This branch starts from current `main` and keeps only the universal JSON path, with source facts split.

## Phase 0 — Split source facts (this branch)

- [x] Highest-authority universal data-driven combat contract exists.
- [x] Class progression JSON contains class deltas only (no ability scores, HP, species, or origin feats).
- [x] Species JSON exists (`data/heroes/2024/species/orc.json`).
- [x] Persistent character track JSON exists (ASIs, canonical HP, mastery picks, origin feats).
- [x] Subclass JSON remains sparse Champion deltas.
- [x] Build/loadout JSON remains equipment + fighting style + attacks.
- [x] Fold merges class + subclass + species + track.
- [x] Hero JSON compiles to `CombatantDefinition` then `CombatantTemplate` (same boundary as monsters).
- [x] Edition-mismatch rejection at fold and compile.
- [ ] Compare JSON-compiled Karnok 1–17 against the certified Python fingerprints already on `main`.
- [ ] Do not add more Python per-level Fighter builders.

## Phase 1 — Finish 2024 Fighter migration

- [ ] Report every fingerprint mismatch as source-data, compiler, or capability-registry work.
- [ ] Derive AC from armor + Dex + Fighting Style once fingerprints prove the inputs.
- [ ] Reconcile `hp_by_level` with hit-die math or record why the canonical numbers differ.
- [ ] Audit levels 18–20 and list actual unsupported universal capability IDs.
- [ ] Implement only genuinely missing reusable capabilities, with Python/browser parity.
- [ ] Compile/certify Fighter 1–20 from JSON.
- [ ] Switch Fighter runtime/certification registration to the JSON path.
- [ ] Delete obsolete Fighter per-level builders only after permanent parity tests are green.

## Phase 2 — Normalize monster authoring

- [ ] Define/validate edition-scoped monster source schema: stat-block facts + universal capability references.
- [ ] Preserve current SRD source/audit metadata.
- [ ] Compile monster JSON to the same `CombatantDefinition` boundary (already true for the capability registry).
- [ ] Derive values only when RAW inputs make derivation authoritative; retain printed monster values when the stat block is authoritative.
- [ ] Prove representative simple attack, multiattack, save-action, reaction, spellcaster, recharge, resistance/immunity, and condition monsters.
- [ ] Replace generated/legacy monster construction in batches only after parity evidence.
- [ ] Keep 2014 and 2024 monster source data isolated while reusing genuinely identical primitives.

## Phase 3 — Migrate all pregens as data

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

For each track: identity + species + class deltas + subclass deltas + build -> compile 1–20 -> capability audit -> parity/certification -> remove superseded builders.

## Phase 4 — Homebrew/import contract

- [ ] Validate homebrew against the same character/monster schemas.
- [ ] Reject unknown executable behavior/capability IDs.
- [ ] Permit existing universal capability IDs with legal parameters.
- [ ] Provide validation errors that name unsupported/malformed capabilities.
- [ ] Prove official-vs-homebrew, homebrew-vs-homebrew, pregen-vs-monster, PvP, and monster-vs-monster all enter the same engine.

## Phase 5 — Browser/runtime generation

- [ ] Generate browser-ready immutable combatant records from the same compiled source.
- [ ] Verify Python/browser derived-stat and capability parity.
- [ ] Ensure Step/Watch/Replay/Turbo consume the same canonical event stream.
- [ ] Ensure source data is never mutated by a fight.
- [ ] Ensure a new fight restores HP/resources/slots/conditions from immutable compiled source.

## Phase 6 — Certification and cleanup

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
