# D20 Iron Pit — SOUL

This file is the first-read architecture rule for every agent and contributor working on Iron Pit.

## Core principle

**The engine models what an effect does, not what the source calls it.**

Printed names exist for cards, player-facing logs, source provenance, audits, and certification. They are not combat-dispatch keys.

A class feature, subclass feature, feat, spell, item, monster trait, legendary action, lair action, or homebrew ability must be decomposed into universal mechanics before implementation.

Examples of universal identity:

- Prone is Prone.
- Grappled is Grappled.
- Restrained is Restrained.
- Blinded is Blinded.
- Charmed is Charmed.
- Frightened is Frightened.
- Poisoned is Poisoned.
- Advantage is Advantage.
- Disadvantage is Disadvantage.
- Resistance is Resistance.
- Immunity is Immunity.
- Vulnerability is Vulnerability.
- Damage is typed damage.
- Healing is healing.
- A saving throw is a saving throw.
- An attack roll is an attack roll.
- A resource is a resource.
- Recharge is recharge.
- Movement is movement.
- A buff/debuff is semantic state plus timing and qualifiers.

The source supplies parameters such as ability name, source id, ruleset, DC, save ability, attack bonus, damage dice/type, range, duration, target count, timing, recharge threshold, resource limits, qualifiers, and logging text.

The engine supplies behavior.

## Mandatory implementation sequence

Before writing any combat mechanic:

1. Ignore the printed name temporarily.
2. Describe the exact RAW behavior.
3. Break it into trigger/timing, action/resource cost, attack/check/save, damage/healing, condition/state change, range/geometry, duration, movement, recharge/use limit, and lifecycle/reset.
4. Search both hero and monster implementations for equivalent behavior.
5. Reuse an existing universal primitive whenever semantics match.
6. Parameterize differences in source data.
7. Compose multi-effect abilities from existing primitives.
8. Add a new universal primitive only when the existing engine cannot represent the behavior accurately.
9. Keep the exact printed source name in player logs and source/audit records.
10. Re-audit pregens and monsters after widening a primitive so all equivalent content can bind to it.

## Forbidden architecture

Do not add combat behavior that dispatches on:

- class name or class id;
- subclass name or subclass id;
- monster name or monster id;
- spell name;
- feature/ability name;
- hero identity;
- presentation text.

Those identifiers may select content or source data, but they must not decide how a universal combat mechanic resolves.

Do not create a second resolver because a differently named source produces the same mechanical outcome.

Do not copy same-name 2014 and 2024 behavior across editions without source evidence. Edition source data stays isolated even when both editions bind to the same universal primitive.

Do not invent or backport combat capability for a source creature that explicitly has no effective attack or combat action. Keep the source record in the audit corpus and classify it `ARENA_NEUTRAL`/non-runnable unless product policy explicitly removes it.

## Universal runtime model

Combat behavior follows:

`checks -> modifiers -> result -> state update -> audit event`

Source templates/cards are immutable. Fight mutation belongs only to temporary combat state.

Python is the rules-reference/certification oracle. Browser JavaScript is the production fight engine. A capability is not supported until the required Python/browser behavior is equivalent and permanently tested.

Unsupported outcome-changing mechanics fail closed.

## Homebrew requirement

Future homebrew cards use the same engine. A homebrew ability does not receive a custom resolver merely because it is new or uniquely named. It must bind to existing universal mechanics and provide declarative parameters. A genuinely new behavior may introduce a new primitive only after the semantic-reuse search proves no existing composition can represent it.

## Authority

This file defines the product philosophy and semantic-engine rule. Detailed rules remain in:

- `docs/IRON_PIT_RULES_CONTRACT.md`
- `docs/UNIVERSAL_COMBATANT_ARCHITECTURE.md`
- `docs/COMBAT_RESOLUTION_PIPELINE.md`
- `docs/PREGEN_AND_CONTENT_RULES_CONTRACT.md`
- `docs/CANONICAL_COMBAT_BUILD_POLICY.md`
- `docs/TWO_AGENT_COORDINATION.md`

When implementation conflicts with this principle, refactor the implementation rather than creating another source-specific exception.
