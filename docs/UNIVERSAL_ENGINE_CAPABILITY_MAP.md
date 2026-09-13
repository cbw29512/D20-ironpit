# Universal Engine Capability Map

This file is the implementation map for D20 Iron Pit combat. It supplements `UNIVERSAL_COMBATANT_ARCHITECTURE.md` with an engine-first build order and test contract.

## Core rule

Combat rules belong to the universal engine. Monsters, pregens, classes, subclasses, weapons, spells, and traits declare immutable facts that feed those rules.

Examples:

- Slashing is always `slashing`, regardless of source.
- Frightened is always the same condition, regardless of source.
- Recharge is always the same resource lifecycle, regardless of action.
- A Saving Throw is always the same d20 + modifiers vs. DC resolver.
- A Reaction is always the same action-economy resource; triggers and responses are data.

Do not add a name-specific combat branch when existing primitives can express the effect.

## Resolution architecture

`RAW source -> declarative content -> capability compiler -> universal primitives -> shared resolver -> audit event`

The capability compiler may translate source-specific wording into primitive configuration. It must not duplicate combat resolution.

## Primitive families

1. **D20 resolution** — attacks, saves, ability checks, Advantage, Disadvantage, rerolls, replacements, critical rules.
2. **Damage** — typed components, bonus components, reduction, Resistance, Immunity, Vulnerability, absorption, temporary HP, HP loss.
3. **Healing** — healing rolls, regeneration, maximum-HP restoration where legal, temporary HP.
4. **Conditions** — application, immunity, stacking identity, linked conditions, removal, repeat saves, expiry.
5. **Modifiers** — AC, Speed, attack/save/check bonuses, damage bonuses/penalties, target-scoped Advantage/Disadvantage.
6. **Resources** — spell slots, class resources, X/day uses, Recharge, Legendary Resistance, legendary-action pools.
7. **Action economy** — Action, Bonus Action, Reaction, extra actions, restrictions, denial, replacement.
8. **Movement** — voluntary movement, closing, push, pull, teleport, forced movement, collision, Opportunity Attack interaction.
9. **Targeting** — self, single target, ally/enemy filters, range, size, conditional legality.
10. **Areas** — cone, line, radius/sphere, target collection, independent saves, shared damage roll where required.
11. **Attack-action composition** — Extra Attack, Multiattack, mixed attack/save slots, substitutions, ordered actions.
12. **Triggers** — on hit, on miss, failed save, successful save, damage taken, start/end turn, bloodied, zero HP, source death.
13. **Persistent lifecycle** — duration, source identity, effect-family identity, repeat-save timing, automatic recovery, cleanup.
14. **Periodic effects** — start/end-turn damage or healing, attached-drain effects, recurring wounds.
15. **Reactions** — trigger grammar plus a primitive response: attack, damage reduction, movement, teleport, save replacement, condition removal.
16. **Auras** — proximity membership plus a primitive effect; entering/leaving range changes membership rather than creating a separate rules engine.
17. **Attachment** — source/target link, movement relationship, periodic effects, detach rules, source cleanup.
18. **Transformations** — temporary state/template overlays, resource preservation/reset rules, revert conditions.
19. **Spellcasting** — shared spell definitions using the same attacks, saves, damage, conditions, modifiers, resources, concentration, and targeting primitives.
20. **Legendary timing** — shared after-turn opportunity windows and resource spending; legendary actions still resolve through normal primitives.
21. **Zero-HP/death lifecycle** — monster death, character Unconscious/Stable/death saves, on-zero and on-death triggers.
22. **Arena policy** — chooses among legal supported actions only. It never implements a combat rule.

## Required testing layers

Every new primitive or meaningful primitive extension must earn support at all four layers.

### 1. Primitive test

Test the rule without a named monster/class when possible.

Examples: `10 slashing vs resistance -> 5`; failed Wisdom save applies Frightened; Recharge 5-6 restores exactly one expended use.

### 2. Composition test

Combine primitives to prove resolution order and interaction.

Examples: critical mixed damage + resistance + temporary HP; grapple + restrained + timed condition; forced movement + Opportunity Attack eligibility; concentration + damage + zero HP.

### 3. Binding/compiler test

Prove source data compiles to the correct primitive configuration. Do not retest the primitive's mathematics here.

Example: a breath weapon compiles to `DEX save + cone + fire damage + half on success + Recharge 5-6`.

### 4. End-to-end parity test

Run at least one representative combatant through Python and browser paths and compare outcome-relevant state/events. Step, Watch, Replay, and Turbo must consume the same rules path/event semantics.

## Cross-product regression strategy

High-risk primitives require representative cross-source tests:

- damage type x defense x attack/spell/save source;
- condition x monster/spell/class-feature source;
- resource lifecycle x Recharge/X-per-day/class resource;
- modifier x attack/save/check/damage target;
- trigger timing x start/end/source/target turn;
- reaction trigger x response primitive.

This prevents source-specific implementations from silently diverging.

## Content binding rule

A monster or pregen should normally require data only. If binding content requires new resolution code, stop and classify the missing behavior as either:

1. an existing primitive with a new trigger/configuration; or
2. a genuinely missing universal primitive.

Only case 2 justifies new engine behavior.

## Current high-yield build order

1. Restore exact-head Python/browser CI parity.
2. Finish composable persistent attack/save riders.
3. Complete generic modifiers, including ability-check modifiers and stacking/expiry interactions.
4. Complete condition semantics and condition/control composition.
5. Generalize limited-use resources beyond Recharge.
6. Generalize forced movement and teleport semantics.
7. Add periodic damage/healing and regeneration through lifecycle triggers.
8. Add aura membership/effect application.
9. Generalize reaction trigger/response grammar.
10. Complete monster/pregen spell surface through shared spell primitives.
11. Add Legendary Resistance and legendary-action timing/resources.
12. Add attachment and transformation/splitting only after their lifecycle primitives are explicit.

After each primitive lands, re-run the full monster and pregen audits and bind every newly qualifying combatant automatically.

## Certification invariant

No capability is `supported` unless:

- its data schema is explicit;
- its state transitions are explicit;
- Python resolution exists;
- browser resolution exists;
- permanent primitive/composition/binding/parity evidence exists;
- unsupported combinations fail closed;
- generated artifacts are current;
- exact-head CI is green.

Ready counts are outputs of engine coverage. They are never targets that justify special-case code.
