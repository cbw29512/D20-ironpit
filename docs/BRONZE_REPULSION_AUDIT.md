# 2014 Bronze Dragon Repulsion Breath Audit

## Scope

M-016 binds the 2014 Bronze Dragon Repulsion Breath family to the existing universal saving-throw and forced-movement engine.

No Bronze-specific resolver exists.

## Source-owned parameters

| Monster | Save | DC | Area | Failed-save push |
|---|---|---:|---|---:|
| Bronze Dragon Wyrmling | Strength | 12 | 30-ft cone | 30 ft |
| Young Bronze Dragon | Strength | 15 | 30-ft cone | 40 ft |
| Adult Bronze Dragon | Strength | 19 | 30-ft cone | 60 ft |
| Ancient Bronze Dragon | Strength | 23 | 30-ft cone | 60 ft |

The shared Breath Weapons resource uses the printed Recharge 5-6 rule.

These values stay in monster/source data. They are not universal-engine constants.

## Universal behavior reused

Repulsion Breath decomposes to:

`Action -> recharge-backed area save -> failed save -> forced movement away from source`

The engine already owns:

- saving-throw resolution;
- area/cone targeting;
- recharge/resource behavior;
- failed-save forced movement;
- grid movement legality and displacement.

The missing bridge was declarative propagation of `failure_push_ft` through the generic save capability/compiler path so Python and browser resolution receive the source-owned push distance.

Canonical flow:

`monster source -> SaveCapabilityDefinition.failure_push_ft -> SavingThrowAction.failure_push_ft -> browser serialization -> shared forced-movement resolver`

## Certification effect

When this binding is accepted:

- Bronze Dragon Wyrmling and Young Bronze Dragon lose their only remaining blocker;
- Adult and Ancient Bronze Dragons lose the Repulsion Breath blocker but remain independently blocked by their extra-action/Change Shape lane;
- no other source behavior is removed or approximated.

## Reuse rule

Any future source that says a failed saving throw pushes a target a specified distance should first bind to this same generic failed-save forced-movement field. A different DC, ability, area, or push distance is source data, not a new mechanic.

If a future effect differs semantically (for example pull, direction choice, collision damage, or movement with another condition), decompose that difference and reuse existing movement primitives before considering new engine behavior.
