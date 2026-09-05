# Iron Pit MVP Combat Scope

This file is the durable scope rule for the base Iron Pit engine and monster/hero certification. It overrides older wording that accidentally treats every SRD battlefield detail as an MVP blocker.

## Core rule

**A source feature may block MVP readiness only when it can directly change the mathematical outcome of an Iron Pit fight.**

Iron Pit is intentionally narrower than a complete virtual tabletop. The base engine is being finished first. Deferred mechanics can be added later without forcing the initial 330-monster integration to model rules that do not matter to the current fight abstraction.

## In scope

Model and certify mechanics that directly change one or more of these outcomes:

- attack roll, attack availability, number of attacks, or critical-hit behavior;
- Advantage/Disadvantage on an Iron-Pit attack roll, saving throw, or initiative roll;
- saving-throw consequence when that consequence is itself in scope;
- damage amount or damage type;
- damage Resistance, Immunity, or Vulnerability;
- Armor Class;
- current HP, maximum HP, Temporary HP, healing, death, or stabilization;
- Action, Bonus Action, or Reaction availability when it changes what can be done in combat;
- combat-relevant conditions such as Blinded, Charmed, Frightened, Incapacitated, Invisible, Paralyzed, Petrified, Poisoned, Prone, Restrained, Stunned, Unconscious, or outcome-changing Exhaustion;
- target legality, cover, untargetability, or a source/target relationship that another in-scope mechanic explicitly depends on;
- ongoing combat damage/healing, concentration for an in-scope effect, summons/additional combatants, and limited-use/recharge state for an in-scope ability.

The implementation rule is always **one mechanic, one resolver**. Named monster traits declare sources, triggers, targets, values, and durations; they do not reimplement universal rules.

## Deferred and non-blocking for the MVP

Do not require runtime support, and do not block certification, when a feature only changes:

- Speed or a movement mode (walk, climb, fly, swim, burrow, hover);
- jump/leap distance;
- difficult terrain;
- movement through spaces, squeezing, or compression;
- teleportation or repositioning;
- push/pull distance;
- Grappled when its only current mathematical consequence is movement/Speed;
- Disengage/Dash or another movement-only choice under the current no-kiting arena policy;
- Deafened when it has no separate modeled mathematical consequence;
- illumination, languages, environmental travel, or senses that do not alter an Iron Pit attack/save/target result;
- shape-changing that does not change an in-scope statistic or action;
- a movement-only Bonus Action, Reaction, Legendary Action, limited-use feature, or trait.

These are **MVP out of scope**, not unsupported rules failures.

## Dependency exception

A normally deferred relationship becomes in scope when another direct-math effect depends on it.

Examples:

- `Grappled` only -> defer.
- `Grappled; while Grappled, Restrained` -> model Restrained and the relationship needed to maintain it.
- `one creature Grappled by this monster takes damage` -> the grapple relationship affects target legality, so it is in scope for that action.
- `push 15 feet` -> defer.
- `push 15 feet and Prone` -> ignore the push for MVP; model Prone.
- `Speed decreases by 10 feet` -> defer.
- `Speed decreases and the target loses its Action` -> ignore the Speed change; model the Action loss.

## Universal examples

### Typed damage

Every damage component carries one damage type. The same resolver handles every type:

1. matching Immunity -> 0 damage;
2. otherwise matching Resistance -> half damage using the engine's normal rounding rule;
3. otherwise matching Vulnerability -> double damage;
4. otherwise normal damage.

There is no separate Fire-resistance engine, Cold-resistance engine, and so on.

### Saving throws

Every saving throw uses the same d20 resolver:

`d20 + save modifier + applicable bonuses` compared with `DC`.

The result is `success` or `failure`; the feature data declares the consequence. A saving throw whose only consequence is deferred movement is itself non-blocking for the MVP.

### Conditions

A feature declares a condition. The shared condition engine decides immunity, applies the state, and supplies the universal mathematical consequences. A monster feature does not redefine what Poisoned, Prone, Restrained, or another condition means.

## Certification rule

For the base-engine program, `RAW-ready` means **RAW-correct for every mechanic that is in Iron Pit MVP scope**, with out-of-scope source semantics explicitly deferred rather than silently mistaken for implemented behavior.

A monster must not remain blocked merely because its stat block contains movement, exploration, environmental, sensory, or flavor rules that cannot change an Iron Pit MVP combat outcome.

Whenever this scope changes later, re-audit all 330 monsters and only add the newly activated shared mechanics and affected monsters.
