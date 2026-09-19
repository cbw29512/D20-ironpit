# Universal JSON Combatant Refactor Checklist

This checklist is the execution queue for the JSON combatant authoring path in `docs/CANONICAL_HERO_DATA_ARCHITECTURE.md` and `docs/UNIVERSAL_COMBATANT_ARCHITECTURE.md`.
It does not replace `docs/IRON_PIT_RULES_CONTRACT.md`. Pit rules, house rules, and Arena healing/threat policy stay in that contract.

`feat/2024-fighter-15-reanchored` is parked. It mixed live Fighter 15–17 Python builders with a JSON compiler whose "class table" was actually Karnok. This branch starts from current `main` and keeps only the universal JSON path, with source facts split.

## Phase 0 — Split source facts (this branch)

- [x] `docs/IRON_PIT_RULES_CONTRACT.md` remains the Pit rules authority; JSON source split does not rewrite it.
- [x] Class progression JSON contains class deltas only (no ability scores, HP, species, or origin feats).
- [x] Species JSON exists (`data/heroes/2024/species/orc.json`).
- [x] Persistent character track JSON exists (ASIs, canonical HP, mastery picks, origin feats).
- [x] Subclass JSON remains sparse Champion deltas.
- [x] Build/loadout JSON remains equipment + fighting style + attacks.
- [x] Fold merges class + subclass + species + track.
- [x] Hero JSON compiles to `CombatantDefinition` then `CombatantTemplate` (same boundary as monsters).
- [x] Edition-mismatch rejection at fold and compile.
- [x] Compare JSON-compiled Karnok 1–14 against the certified Python fingerprints already on `main`.
- [ ] Do not add more Python per-level Fighter builders.

## Phase 1 — Finish 2024 Fighter migration

- [x] Report every fingerprint mismatch as source-data, compiler, or capability-registry work.
- [x] Derive AC from armor + Dex + Fighting Style once fingerprints prove the inputs.
- [x] Reconcile `hp_by_level` with hit-die math or record why the canonical numbers differ.
- [x] Audit levels 18–20 and list actual unsupported universal capability IDs.
- [x] Implement only genuinely missing reusable capabilities, with Python/browser parity.
- [x] Compile/certify 2014 Fighter 1–20 from JSON.
- [ ] Compile/certify 2024 Fighter 1–20 from JSON. JSON now compiles 1–20 with SRD Survivor and Boon of Combat Prowess. Certified runtime registration is still 1–14 until fingerprints/profiles are extended.
- [x] Switch Fighter runtime/certification registration to the JSON path for currently certified levels.
- [ ] Delete obsolete Fighter per-level builders only after permanent parity tests are green.

### 2024 Champion 15–20 RAW audit

JSON now derives Karnok HP/AC from RAW inputs. Certified fingerprints for 1–14 match that math. Remaining blockers are not HP/AC:

- **15 Superior Critical:** same expanded-critical primitive as Improved Critical (`critical_hit_minimum` 18). JSON compiles. Not yet certified; Python runtime registration still stops at 14.
- **16 ASI/feat:** recorded on Karnok's track as Dexterity 15→17. Same combat-role ASI already stored in `FIGHTER_COMBAT_LEVELS`.
- **17 Action Surge (2) / Indomitable (3):** already in the class table.
- **18 Survivor (SRD 5.2.1):** Defy Death is Advantage on Death Saves and 18–20 counts as a 20. Heroic Rally is start-of-turn heal of 5 + Con while Bloodied and at least 1 HP; it reuses the existing Survivor heal primitive. Implemented with Python/browser parity.
- **19 Epic Boon of Combat Prowess (SRD 5.2.1):** +1 Dexterity (15/17/18 already on the level table) and Peerless Aim (one miss becomes a hit, once per turn; Iron Pit natural 1 still misses). Implemented with Python/browser parity.
- **20 Extra Attack (3):** `attack_count` 4 is already in the class table.

Champion 7 Additional Fighting Style is a character choice. Karnok's Great Weapon Fighting is still stored as a subclass capability rather than a track fighting-style pick; that is a later source-data cleanup, not a new engine.

### Derived-stat contract

- HP = class Hit Die max at 1 + average (die/2 + 1) each later level + current Constitution modifier × level.
- Worn AC uses the shared armor catalog, Dexterity cap, Defense Fighting Style, and shield.
- Barbarian Unarmored Defense = 10 + Dex + Con, shield allowed. Monk = 10 + Dex + Wis, no shield.
- Fingerprints stay in the track only to fail closed if derivation drifts.

## Phase 2 — Normalize monster authoring

- [ ] Define/validate edition-scoped monster source schema: stat-block facts + universal capability references.
- [ ] Preserve current SRD source/audit metadata.
- [ ] Compile monster JSON to the same `CombatantDefinition` boundary (already true for the capability registry).
- [ ] Derive values only when RAW inputs make derivation authoritative; retain printed monster values when the stat block is authoritative.
- [ ] Prove representative simple attack, multiattack, save-action, reaction, spellcaster, recharge, resistance/immunity, and condition monsters.
- [ ] Replace generated/legacy monster construction in batches only after parity evidence.
- [ ] Keep 2014 and 2024 monster source data isolated while reusing genuinely identical primitives.

## Phase 3 — Migrate all pregens as data

- [x] 2024 Fighter JSON source + certified fingerprint match for 1–14
- [x] 2024 Barbarian JSON source + certified fingerprint match for 1–6
- [x] 2024 Cleric JSON source + certified fingerprint match for 1–4
- [x] 2024 Rogue JSON source + certified fingerprint match for 1
- [ ] 2024 Bard — class/subclass tables only; no certified HP/weapon track
- [ ] 2024 Druid — class/subclass tables only; no certified HP/weapon track
- [ ] 2024 Monk — class/subclass tables only; spine has no HP
- [ ] 2024 Paladin — class/subclass tables only; spine has no HP
- [ ] 2024 Ranger — class/subclass tables only; spine has no HP
- [ ] 2024 Sorcerer — class/subclass tables only; spine has no HP
- [ ] 2024 Warlock — class/subclass tables only; spine has no HP
- [ ] 2024 Wizard — class/subclass tables only; spine has no HP
- [x] 2014 Fighter JSON source + certified fingerprint match for 1–20
- [x] 2014 Barbarian JSON source + certified fingerprint match for 1–13
- [x] 2014 Monk JSON source + certified fingerprint match for 1–10
- [x] 2014 Paladin JSON source + certified fingerprint match for 1–10
- [x] 2014 Rogue JSON source + certified fingerprint match for 1–10
- [ ] 2014 Bard — no certified Python track; do not invent
- [ ] 2014 Cleric — no certified Python track; do not invent
- [ ] 2014 Druid — no certified Python track; do not invent
- [ ] 2014 Ranger — no certified Python track; do not invent
- [ ] 2014 Sorcerer — no certified Python track; do not invent
- [ ] 2014 Warlock — no certified Python track; do not invent
- [ ] 2014 Wizard — no certified Python track; do not invent

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
