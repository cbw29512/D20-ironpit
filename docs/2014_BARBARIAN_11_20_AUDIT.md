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
| 15 | Persistent Rage | `persistent_rage_2014=True`; 1-minute maximum remains | Isolated shared Rage primitive is implemented/tested in Python and browser; Rage no longer ends early for lack of attack/damage and ignores other incapacitation; it still ends on unconsciousness/death or maximum duration | Primitive staged safely; Rokhan level 15 remains uncertified because level 14 Retaliation is missing |
| 16 | ASI | Canonical choice: +2 Constitution (16 -> 18); Rage damage becomes +4 | No new mutable state | Numeric/profile spine staged and regression-tested; not exposed while level 14 is unsupported |
| 17 | Brutal Critical (3 dice), 6 Rages | `brutal_critical_dice=3`; finite Rage count = 6 | Existing critical-hit/resource state | Numeric/profile spine staged and regression-tested; not exposed while level 14 is unsupported |
| 18 | Indomitable Might | Strength-check result has a floor equal to Strength score | Generic ability-check minimum rule plus auditable total replacement; wired into every currently supported check family in Python/browser | Primitive staged safely; level 18 remains uncertified because level 14 Retaliation is missing |
| 19 | ASI | Canonical choice: +2 Constitution (18 -> 20) | No new mutable state | Numeric/profile spine staged and regression-tested; not exposed while level 14 is unsupported |
| 20 | Primal Champion; unlimited Rage | Strength and Constitution +4 to 24 are staged explicitly after legal ASIs; Rage ceases to be finite | Stat propagation is tested; Unlimited Rage still requires explicit non-finite resource semantics | **Remaining blocker: unlimited-resource semantics** |

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

## Safe staged primitive above the certification boundary

### Persistent Rage (level 15)

The existing Rage engine now accepts a ruleset-scoped declarative `persistent_rage_2014` flag.
When active, a 2014 Rage begins with its full one-minute expiry instead of the normal next-round
early-expiry checkpoint. The ordinary maximum duration, unconsciousness/death cleanup, Frenzy exhaustion,
and fresh-combat reset behavior are unchanged. Python and browser regression coverage exercise
this primitive with a synthetic level-15 state derived from the certified level-13 template.

This does **not** make Rokhan level 15 runnable or certifiable. The builder remains capped at 13
because exposing any level 14+ template before Retaliation exists would silently omit a mandatory
combat feature and violate fail-closed certification.

### Indomitable Might (level 18)

A reusable `AbilityCheckMinimum` rule now declares the affected ability and source feature. The shared resolver compares the completed ability-check total with that ability's score, preserves the original dice/modifier, and records an audit `total_replacement` when the floor changes the accepted total. Python and browser integrations cover both current ability-check families: grapple escape and spell-effect removal. A synthetic level-18 Rokhan regression proves the Strength floor without exposing or registering an invalid level-18 template.

This does **not** widen certification beyond level 13 because level 14 Retaliation is still a mandatory cumulative blocker.

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

This tranche registers levels 11-13 only. The connected branch registry therefore contains 63
certified 2014 snapshots (Fighter 1-20, Barbarian 1-13, Rogue/Monk/Paladin 1-10). Level 15's
Persistent Rage primitive is staged and tested but intentionally does not widen the registered
Rokhan progression. Levels 14-20 remain unregistered until their cumulative outcome-changing
mechanics are supported. Generated counts are authoritative; no hand-authored manifest count
should be changed.
