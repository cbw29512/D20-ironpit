# 2014 Berserker Barbarian levels 11-20 audit

Branch lane: `feat/2014-barbarian-11-20`.

Rules authority: D&D Basic Rules 2014, Barbarian and Path of the Berserker.
Repository combat contracts remain authoritative for implementation and certification.

## State-first progression

Rokhan Stonefury remains the same Human Path of the Berserker, greataxe-first
canonical build. Levels are cumulative; a later level cannot certify while an
earlier outcome-changing feature is unsupported.

| Level | RAW combat delta | Immutable template/profile state | Runtime state / lifecycle | Status |
|---|---|---|---|---|
| 11 | Relentless Rage | Effect-bound survival save: Rage required, Constitution DC 10, +5 per attempt, success sets HP to 1 | Existing per-fight survival-save attempt map; fresh combat resets attempts | Supported and eligible for certification |
| 12 | ASI | +1 Constitution, +1 Wisdom; derived AC, HP, saves, attacks and resource count recomputed | No new mutable state | Supported and eligible for certification |
| 13 | Brutal Critical (2 dice) | `brutal_critical_dice=2`; PB increases to +5 | Existing critical-hit resolution | Supported and eligible for certification |
| 14 | Retaliation | Reaction trigger: damage from a creature within 5 feet, then one melee weapon attack against that creature | Must consume the Reaction and resolve immediately off-turn | **Blocked: missing universal damage-trigger dispatch** |
| 15 | Persistent Rage | Rage early-expiry policy changes; 1-minute maximum remains | Rage no longer ends early for lack of attack/damage; unconsciousness or voluntary end still ends it | Blocked cumulatively by level 14; do not add dead feature code before Retaliation is supported |
| 16 | ASI | Canonical combat ASI; Rage damage is +4 at this level | No new mutable state | Blocked cumulatively by level 14 |
| 17 | Brutal Critical (3 dice), 6 Rages | Existing brutal-critical dice field can represent 3 | Existing critical-hit/resource state | Blocked cumulatively by level 14 |
| 18 | Indomitable Might | Strength-check result has a floor equal to Strength score | Requires a shared ability-check result-replacement primitive | **Additional blocker: missing universal check-floor primitive** |
| 19 | ASI | Canonical combat ASI | No new mutable state | Blocked cumulatively by level 14 and level 18 |
| 20 | Primal Champion; unlimited Rage | Strength and Constitution +4, maxima become 24; Rage ceases to be finite | Unlimited resource must not be represented by a fake large use count | **Additional blockers: unlimited-resource semantics and feature-aware >20 ability cap audit** |

## Implemented parity map for levels 11-13

### Relentless Rage

- Shared immutable schema: `EffectBoundSurvivalSave`.
- Python resolution: `app.combat.undead_fortitude.resolve_effect_bound_survival_save`
  reached from the shared zero-HP pipeline.
- Browser resolution: `browser-undead-fortitude.js::resolveEffectBound`
  reached from `browser-zero-hp.js`.
- Mutable state: `survival_save_uses` and pending audit evidence on the fresh
  combat state; neither mutates source cards.
- 2014 binding: source `relentless-rage`, requires `rage`, Constitution,
  initial DC 10, increment 5, replacement HP 1.
- 2024 parameters remain independent; the 2014 binding does not alter them.

### Level 12 ASI

The established Strength-primary build already has Strength 20. The level-12
ASI repairs two odd scores with +1 Constitution and +1 Wisdom. This preserves
the build role while increasing Constitution 15 -> 16 and Wisdom 13 -> 14.
All dependent runtime values are derived from the finished scores.

### Brutal Critical

The existing shared 2014 primitive consumes declarative
`brutal_critical_dice`. Level 9 remains 1 die and level 13 becomes 2 dice.
No 2024 Weapon Mastery or 2024 Brutal Strike data is introduced.

## Level-14 architectural blocker

Retaliation cannot be implemented correctly as a weapon-hit-only callback.
The source trigger is **taking damage from a creature within 5 feet**, so the
universal engine must preserve damage-source creature provenance across every
supported damage family that can satisfy the trigger.

The required reusable primitive must:

1. dispatch after qualifying damage is actually applied;
2. identify the source creature without a Rokhan/Barbarian name check;
3. use authoritative grid distance and require the source within 5 feet;
4. check and spend the defender's Reaction;
5. select a legal melee weapon attack against that source;
6. resolve the reaction attack immediately through the normal attack resolver;
7. preserve Python/browser parity and audit ordering;
8. avoid recursive or duplicate trigger resolution.

Do not approximate this with an `onHit` hook, because damage can arrive through
other supported families and `onHit` does not mean "took damage from a
creature."

## Certification boundary

This tranche may register levels 11-13 only. Levels 14-20 remain unregistered
until their cumulative outcome-changing mechanics are supported. Generated
counts are authoritative; no hand-authored manifest count should be changed.
