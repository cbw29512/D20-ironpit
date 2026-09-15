# Homebrew Capability Model

Iron Pit uses one combat capability model for pregens, SRD monsters, and homebrew combatants.

## Governing rule

**Combat mechanics are granted by explicit data and prerequisites, not by whether a combatant is a player character or a monster.**

If a rule can be represented by the universal engine, any combatant may use it when its compiled template explicitly grants the required capability.

Examples:

- A pregen with a Greatsword and Greatsword mastery can use Graze.
- A homebrew monster with a Greatsword and explicit Greatsword mastery can use the same Graze implementation.
- Removing the mastery assignment leaves the same Greatsword attack, but without Graze.
- A monster granted a spell, condition rider, recharge action, reaction, resource, resistance, or other supported mechanic uses the same resolver as a pregen granted that mechanic.

## Weapon mastery contract

2024 weapon mastery activates only when all of these are true:

1. The combatant uses the 2024 ruleset.
2. The combatant owns the weapon used by the attack.
3. The combatant explicitly has mastery assigned to that weapon.
4. The requested mastery effect matches the mastery property configured on that weapon.

`kind = character` and `kind = monster` are intentionally irrelevant to this decision.

2014 combatants never activate the 2024 weapon-mastery layer.

## Legitimate actor-kind differences

Actor kind may be consulted only when the game rules or Iron Pit lifecycle explicitly require different treatment. Current examples are zero-HP and death-save handling: player characters can remain downed and make death saves, while ordinary monsters are normally defeated at 0 HP unless another explicit capability changes that outcome.

Those lifecycle differences must not be reused as a shortcut for deciding whether a combatant can use attacks, weapon mastery, spells, conditions, reactions, resources, or other combat mechanics.

## Homebrew compiler requirement

Future homebrew tools should compile user choices into the same `CombatantTemplate` / browser runtime fields used by certified content. They should not generate homebrew-only combat branches.

The intended flow is:

`homebrew choice -> explicit template capability -> universal legality/policy check -> universal resolver -> combat log`

Ability names remain presentation metadata. The engine resolves the structured mechanic behind the name.
