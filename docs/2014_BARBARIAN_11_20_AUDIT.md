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
| 14 | Retaliation | Declarative `DamageReactionAttack(source_feature="retaliation")` from level 14; source range 5 ft; melee-only | Shared Python/browser post-damage reaction chain resolves against the true damaging source and spends Reaction only | Supported on the full producer/browser integration stack |
| 15 | Persistent Rage | `persistent_rage_2014=True`; 1-minute maximum remains | Isolated shared Rage primitive is implemented/tested in Python and browser; Rage no longer ends early for lack of attack/damage and ignores other incapacitation; it still ends on unconsciousness/death or maximum duration | Supported and certified through the level-20 progression |
| 16 | ASI | Canonical choice: +2 Constitution (16 -> 18); Rage damage becomes +4 | No new mutable state | Supported and certified |
| 17 | Brutal Critical (3 dice), 6 Rages | `brutal_critical_dice=3`; finite Rage count = 6 | Existing critical-hit/resource state | Numeric/profile spine staged and regression-tested; not exposed while level 14 is unsupported |
| 18 | Indomitable Might | Strength-check result has a floor equal to Strength score | Generic ability-check minimum rule plus auditable total replacement; wired into every currently supported check family in Python/browser | Supported and certified |
| 19 | ASI | Canonical choice: +2 Constitution (18 -> 20) | No new mutable state | Numeric/profile spine staged and regression-tested; not exposed while level 14 is unsupported |
| 20 | Primal Champion; unlimited Rage | Strength and Constitution +4 to 24 are staged explicitly after legal ASIs; Rage is an explicit unlimited resource ID with no counter | Generic Python/browser resource helpers treat unlimited resources as always available and non-decrementing | Supported and certified |

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

Rokhan level 15 is now generated from the canonical certified level-15 template; the earlier synthetic-only staging guard has been removed on the full certification stack.

### Indomitable Might (level 18)

A reusable `AbilityCheckMinimum` rule now declares the affected ability and source feature. The shared resolver compares the completed ability-check total with that ability's score, preserves the original dice/modifier, and records an audit `total_replacement` when the floor changes the accepted total. Python and browser integrations cover both current ability-check families: grapple escape and spell-effect removal. A synthetic level-18 Rokhan regression proves the Strength floor without exposing or registering an invalid level-18 template.

The certified level-18 template now carries this primitive directly.

### Unlimited Rage (level 20)

Unlimited resources are modeled without a fake counter. A combatant declares an `unlimited_resource_ids` entry; the shared Python/browser resource helpers report that resource as always available, spending it returns no remaining count, and no mutable finite resource state is created. The staged level-20 Rokhan binding uses `rage` this way. Finite resources retain their existing counters unchanged.

The certified level-20 template uses this unlimited-resource representation directly.

## Level-14 Retaliation integration state

The shared engine now provides the state-first schema, runtime eligibility gate, and Python source-bound attack dispatcher. Rokhan's level-14 binding is staged declaratively through `DamageReactionAttack(source_feature="retaliation")`. A focused synthetic encounter regression proves the shared dispatcher:

1. binds the reaction to the actual damaging source rather than normal target order;
2. enforces the 5-foot source range;
3. spends the defender's Reaction without spending the Action;
4. selects Rokhan's declared legal melee attack;
5. resolves the counterattack immediately through the normal encounter attack resolver;
6. disables Reckless Attack on the off-turn counterattack.

On the stacked certification branch, producer call sites and browser parity are present and Rokhan's public builder is widened through level 20.

Do not approximate the remaining work with an `onHit` hook, because damage can arrive through other supported families and `onHit` does not mean "took damage from a creature."

## Certification boundary

The full stacked certification lane registers Rokhan levels 1-20. The resulting 2014 hero registry contains **70 certified snapshots**:

- Fighter 1-20
- Barbarian 1-20
- Rogue 1-10
- Monk 1-10
- Paladin 1-10

Generated repository state remains authoritative. The certification flip is intentionally stacked on the unmerged shared producer/browser reaction work and must not merge ahead of those dependencies.
