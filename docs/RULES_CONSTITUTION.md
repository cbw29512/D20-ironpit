# Iron Pit Rules Constitution

This document is the non-negotiable contract for combat behavior in Iron Pit.

## Source of truth

- Licensed rules content comes from **SRD 5.2.1** under CC-BY-4.0.
- A rule is implemented only after its exact SRD 5.2.1 text/stat block has been verified.
- Memory, legacy 2014 behavior, community shorthand, and tactical preference never override verified SRD 5.2.1.
- If the SRD leaves a decision to the GM, Iron Pit may adopt a deterministic arena policy, but that choice must be labeled `arena_assumption` rather than presented as a rules requirement.

## Hard engine invariants

1. **Rules and tactics are separate.** The rules engine determines what is legal and what an effect does. Tactical policy chooses only among legal options.
2. **No undeclared abilities.** A combatant can use only actions, attacks, spells, reactions, resources, traits, movement modes, saves, resistances, immunities, and conditions granted by its verified template.
3. **Action economy is enforced.** Actions, Bonus Actions, Reactions, movement, spell slots, per-rest uses, concentration, and once-per-turn limits are consumed exactly when the rule says they are.
4. **Range and targeting are enforced before resolution.** Reach, normal/long range, line-of-effect requirements that are modeled, target type/size, and required conditions are checked before an option can resolve.
5. **Every d20 consequence is auditable.** Initiative, attack rolls, ability checks, saving throws, Advantage/Disadvantage sources, selected dice, DCs, and resulting effects belong in the BattleEvent stream.
6. **A failed or successful save must do exactly what the source says.** Damage, half damage, conditions, duration, repeat saves, escape checks, and end conditions are not optional flavor.
7. **Conditions are mechanical state.** A condition is not a label. Its movement, attack, save, targeting, and action consequences must be implemented before catalog coverage can call that condition fully supported.
8. **Damage rolls are never rewritten after the fact.** Raw damage remains auditable; resistance, vulnerability, immunity, temporary HP, and similar rules alter the applied result separately.
9. **Effects can change later choices in the same turn.** Forced movement, conditions, resource use, death, range changes, and other state changes require subsequent attacks/actions to re-check legality against live state.
10. **Unsupported rules fail closed.** Content that requires an unimplemented mechanic is marked unsupported or prevented from being battle-ready; the engine must not silently approximate it.

## Initiative and turn order

- Every combatant rolls Initiative when combat starts.
- Turns proceed from highest Initiative to lowest and keep that order each round.
- SRD ties are a GM decision. Iron Pit may use a deterministic GM tie policy for reproducible simulations, and that policy must remain documented as an arena assumption.

## Tactical policy contract

Tactical policy is intentionally replaceable and is not RAW. The baseline arena policy should be simple, deterministic, and visible in coverage reports.

- Choose only legal actions.
- Prefer the legal damaging option ranked highest by the configured damage policy.
- Re-evaluate after every attack/effect because range, conditions, HP, and resources may have changed.
- Use movement only within the creature's legal movement options and condition restrictions.
- Healing, defensive abilities, control effects, and spell-slot usage are policy decisions layered on top of exact rules legality.
- Casters must still obey the SRD rule that only one spell slot can be expended to cast a spell on a turn.
- Concentration is exclusive: starting another Concentration effect ends the prior one when the rules require it.

## Build-up strategy

Iron Pit expands from the bottom of the rules tree upward:

1. Low-level martial characters and low-CR creatures with simple attacks.
2. Core conditions and saves: Prone, Grappled, Poisoned, Frightened, Restrained, Paralyzed, and related escape/repeat-save behavior.
3. Reactions, Opportunity Attacks, Disengage, Hide, and richer movement.
4. Low-level spellcasting, spell slots, spell attacks, save spells, Concentration, ongoing effects, and healing.
5. Higher-level class features, multi-round control, summons, areas, and complex monsters.

Every new mechanic requires: verified source data, typed state/schema, rules resolution, BattleEvent audit output, deterministic unit tests, catalog coverage, and replay support when visible.

## Release gate

A mechanic is `fully_implemented` only when its legal triggers, resource/action costs, rolls or saves, success/failure outcomes, duration/end rules, condition interactions, and audit events are all represented and tested. Anything less remains `arena_assumption` or `unsupported`.
