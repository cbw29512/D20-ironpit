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
7. **Saving throws are not attack rolls.** Natural 1 or 20 behavior is never borrowed from attack rules unless a verified rule explicitly says so. When a rule lets the target choose between saves, the tactical layer may choose only from those legal abilities.
8. **Conditions are mechanical state.** A condition is not a label. Its movement, attack, save, targeting, and action consequences must be implemented before catalog coverage can call that condition fully supported.
9. **Damage rolls are never rewritten after the fact.** Raw damage remains auditable; resistance, vulnerability, immunity, temporary HP, and similar rules alter the applied result separately.
10. **Effects can change later choices in the same turn.** Forced movement, conditions, resource use, death, range changes, and other state changes require subsequent attacks/actions to re-check legality against live state.
11. **Unsupported rules fail closed.** Content that requires an unimplemented mechanic is marked unsupported or prevented from being battle-ready; the engine must not silently approximate it.

## Scaling architecture invariants

- **Keep combatants simple; make encounters general.** Character and monster templates describe verified capabilities, not bespoke encounter scripts.
- A template ID identifies reusable content; a runtime `instance_id` identifies one creature in one encounter. Multiple instances may use the same template.
- Encounter sides are data, not hard-coded `fighter` and `monster` roles. The long-term engine supports 1-v-1, 1-v-many, and many-v-many with the same combatant rules.
- Position belongs to encounter state, not the reusable combatant template. Target distance is derived from live positions.
- Initiative is rolled across the complete encounter roster.
- Target selection is a replaceable tactical policy. It must never create an illegal target or change what an ability does.
- Complexity is added only when a verified feature requires it. Low-level characters and low-CR creatures should remain mechanically small even though the encounter engine can scale.

## Initiative and turn order

- Every combatant rolls Initiative when combat starts.
- Turns proceed from highest Initiative to lowest and keep that order each round.
- SRD ties are a GM decision. Iron Pit uses Initiative bonus as the first deterministic arena tiebreaker and runtime instance ID as the final stable tiebreaker.

## Tactical policy contract

Tactical policy is intentionally replaceable and is not RAW. The baseline arena policy should be simple, deterministic, and visible in coverage reports.

- Choose only legal actions and legal targets.
- Prefer a simple legal damaging option rather than adding speculative tactical intelligence early.
- Re-evaluate after every attack/effect because range, conditions, HP, resources, targets, and positions may have changed.
- Use movement only within the creature's legal movement options and condition restrictions.
- Legal Grapple/Shove options exist independently of whether the baseline policy chooses them. Control mechanics must not be forced into every creature's tactics merely because the engine supports them.
- When a target legally chooses between Strength and Dexterity for a save, the baseline arena policy chooses its better legal modifier; this is a tactical choice, not a change to the save rule.
- Healing, defensive abilities, control effects, and spell-slot usage are policy decisions layered on top of exact rules legality.
- Casters must still obey the SRD rule that only one spell slot can be expended to cast a spell on a turn.
- Concentration is exclusive: starting another Concentration effect ends the prior one when the rules require it.

### Closing-combat baseline

The default arena does **not** use voluntary ranged kiting. For combatants with a melee-capable attack profile, the baseline policy is to close and engage.

1. Resolve start-of-turn rules, including condition expiry, recharge rolls, and action availability.
2. Spend legal normal movement toward the preferred melee reach before the final offensive action is chosen.
3. Re-check all legal abilities and attacks from the new live distance after that movement.
4. If melee reach is restored, prefer a legal melee use over a ranged weapon use.
5. If the creature is still outside melee after normal movement, it may use a legal ranged attack or legal ability from that distance.
6. If no useful Action is legal and the creature may approach, Dash toward melee rather than preserving range.
7. The policy never willingly increases distance merely to keep a ranged attack available.
8. Forced movement or knockback may reopen the range band. On the creature's next legal movement opportunity, the same closing sequence runs again: close, re-check melee, then use range only if melee is still unavailable.
9. A verified rule overrides this arena policy. Frightened approach restrictions, Speed 0, forced movement, explicit flee behavior, terrain restrictions, or another exact effect can prevent or require movement.
10. A creature with no melee-capable profile never invents a melee attack and is not required to retreat to maintain range.

## Build-up strategy

Iron Pit expands from the bottom of the rules tree upward:

1. Low-level martial characters and low-CR creatures with simple attacks.
2. Core conditions and saves: Prone, Grappled, Poisoned, Frightened, Restrained, Paralyzed, and related escape/repeat-save behavior.
3. Reactions, Opportunity Attacks, Disengage, Hide, and richer movement.
4. Low-level spellcasting, spell slots, spell attacks, save spells, Concentration, ongoing effects, and healing.
5. Encounter scaling: multiple characters against stronger monsters using shared instance, side, position, initiative, and targeting primitives.
6. Higher-level class features, multi-round control, summons, areas, and complex monsters.

Every new mechanic requires: verified source data, typed state/schema, rules resolution, BattleEvent audit output, deterministic unit tests, catalog coverage, and replay support when visible.

## Release gate

A mechanic is `fully_implemented` only when its legal triggers, resource/action costs, rolls or saves, success/failure outcomes, duration/end rules, condition interactions, and audit events are all represented and tested. Anything less remains `arena_assumption` or `unsupported`.
