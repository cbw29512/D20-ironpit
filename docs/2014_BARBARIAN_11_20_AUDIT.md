# 2014 Berserker Barbarian levels 11-20 audit

Branch lane: `feat/post-damage-reaction-trigger-v2`.

Rules authority: D&D Basic Rules 2014, Barbarian and Path of the Berserker.
Repository combat contracts remain authoritative for implementation and certification.

## State-first progression

Rokhan Stonefury remains the same Human Path of the Berserker, greataxe-first
canonical build. Levels are cumulative and are now represented through level 20.

| Level | RAW combat delta | Immutable template/profile state | Runtime state / lifecycle | Status |
|---|---|---|---|---|
| 11 | Relentless Rage | Effect-bound survival save: Rage required, Constitution DC 10, +5 per attempt, success sets HP to 1 | Existing per-fight survival-save attempt map; fresh combat resets attempts | Implemented and tested |
| 12 | ASI | +1 Constitution, +1 Wisdom; derived AC, HP, saves, attacks and Rage count recomputed | No new mutable state | Implemented and tested |
| 13 | Brutal Critical (2 dice) | `brutal_critical_dice=2`; PB +5 | Existing critical-hit resolution | Implemented and tested |
| 14 | Retaliation | `DamageTriggeredMeleeReaction(id="retaliation", trigger_range_ft=5)` | After actual applied damage from a creature within 5 feet, spend Reaction and immediately resolve one legal melee weapon attack against that source | Implemented in Python/browser universal dispatch and tested |
| 15 | Persistent Rage | `persistent_rage_2014=True`; one-minute maximum remains | No ordinary attack/damage maintenance; unconsciousness/death or maximum duration still ends Rage | Implemented and tested |
| 16 | ASI | CON 18; Rage damage +4 | No new mutable state | Implemented and tested |
| 17 | Brutal Critical (3 dice), 6 Rages | `brutal_critical_dice=3`; finite Rage count 6 | Existing critical-hit/resource state | Implemented and tested |
| 18 | Indomitable Might | Strength-check floor equal to Strength score | Generic auditable ability-check total replacement | Implemented and tested |
| 19 | ASI | CON 20 | No new mutable state | Implemented and tested |
| 20 | Primal Champion; Unlimited Rage | STR/CON 24; `unlimited_resource_ids=["rage"]` with no fake finite counter | Shared Python/browser resource helpers treat Rage as always available and non-decrementing | Implemented and tested |

## Universal Retaliation primitive

Retaliation is not an `onHit` callback. The trigger is taking actual damage
from a creature within 5 feet, regardless of which supported damage family
produced that event.

The reusable schema is `DamageTriggeredMeleeReaction`. The dispatcher:

1. measures damage actually applied after defenses, using per-component
   `applied_total` when present and HP/Temporary HP deltas as fallback evidence;
2. preserves the source creature from the triggering event;
3. uses authoritative encounter distance and the rule's five-foot trigger range;
4. checks and spends the defender's Reaction through the shared action economy;
5. chooses the first legal declared melee weapon attack in normal template order;
6. resolves the reaction through the ordinary attack resolver with
   `spend_action=False`, `off_turn=True`, and Reckless Attack disabled;
7. inserts reaction events immediately after the triggering damage event;
8. recursively opens the same post-damage window, allowing a legal
   counter-Retaliation while naturally terminating once Reactions are spent.

Python dispatch covers normal/Extra Attack and Multiattack attacks, Charge and
follow-up attacks, Cleave, Light/Nick attacks, Frenzy, 2014 Monk bonus strikes,
Opportunity Attacks, saving-throw damage, spell attacks, and spell-save damage.

Browser dispatch mirrors those same damage-producing wrappers through
`browser-damage-triggered-reactions.js` and
`browser-damage-reaction-dispatch.js`. A configured reaction fails closed if
the production dispatcher is absent; old templates without such a reaction can
still run isolated legacy unit harnesses.

## Other high-level primitives

### Persistent Rage

The 2014 Rage engine uses the ruleset-scoped `persistent_rage_2014` flag. The
ordinary one-minute maximum, unconsciousness/death cleanup, Frenzy Exhaustion,
and fresh-combat reset behavior remain unchanged.

### Indomitable Might

`AbilityCheckMinimum` declares the affected ability and source feature. The
shared resolver preserves the original roll and records an auditable
`total_replacement`. Both current ability-check families—grapple escape and
spell-effect removal—use the same primitive in Python and browser runtimes.

### Primal Champion and Unlimited Rage

The canonical ASI spine reaches STR 20 / CON 20 before Primal Champion, then
Primal Champion raises both to 24. Unlimited Rage is represented as an explicit
unlimited resource ID, not a large fake counter. The independent combat
fingerprint and resource audit now represent the same non-finite state.

## Ruleset isolation

- All Rokhan 2014 templates remain `ruleset="2014"`.
- No 2024 Weapon Mastery or 2024 Brutal Strike state is introduced.
- Retaliation is declarative combatant data; the universal resolver contains no
  Rokhan, Barbarian, Berserker, class, or hero-name branch.
- The shared post-damage primitive can be reused by any future combatant that
  declares the same reaction shape.

## Certification boundary

The branch registry now targets Fighter 1-20, Berserker 1-20, and
Rogue/Open Hand Monk/Devotion Paladin 1-10: **70 registered 2014 snapshots**.

That count is a target derived from the registry, not a hand-authored
certification claim. Generated artifacts and exact-head certification workflows
remain authoritative; the branch is not ready to merge until they independently
prove the 70-snapshot state and all required Python/browser gates are green.
