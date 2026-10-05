# D20 Iron Pit — SOUL

This file defines the product's non-negotiable design philosophy. Read it before changing combat behavior, source bindings, pregens, monsters, homebrew support, or certification.

## The one-engine rule

Iron Pit has one universal combat engine.

A source ability's **name is presentation and logging metadata**. It is never sufficient reason for a new resolver, effect type, or code path.

The engine cares about what an ability **does**:

- trigger and timing;
- target and range/geometry;
- attack/check/save;
- damage and damage type;
- healing;
- condition/buff/debuff;
- resistance/immunity/vulnerability;
- movement;
- resource/use/recharge;
- duration/expiry;
- lifecycle such as zero HP, death, turn start/end, or concentration.

Every ability is decomposed into the smallest existing semantic primitives that can represent it correctly.

If two abilities do the same thing mechanically, they use the same primitive even when:
- they have different names;
- one comes from a monster and one from a pregen;
- one is a spell and one is a class feature;
- they appear in different editions;
- one is RAW and one is future homebrew.

Different numbers are data, not different mechanics.

## Source card owns parameters; engine owns resolution

The card/source definition supplies facts such as:
- display name;
- attack bonus or save DC;
- save ability;
- dice and flat modifiers;
- damage type;
- range/radius/target count;
- condition;
- duration/repeat-save timing;
- recharge/use/resource;
- qualifiers and exceptions.

The universal engine supplies:
- hit/miss;
- d20/check/save resolution;
- damage rolling;
- resistance/immunity/vulnerability;
- healing;
- condition immunity/application/removal;
- action economy;
- timing/lifecycle;
- resource consumption;
- movement and geometry;
- logging/audit events.

## Composition before creation

Before adding any engine effect:

1. Ignore the printed ability name.
2. Describe the exact semantics.
3. Search the complete hero, monster, spell, item, and ruleset primitive inventory.
4. Reuse existing primitives.
5. Parameterize differences.
6. Compose multiple primitives when needed.
7. Add a new universal primitive only for the semantic remainder that truly cannot be represented.

A source-specific resolver is a last resort and must be justified in the architecture contract.

## Resolution chains stop when prerequisites fail

Downstream effects resolve only when their trigger actually happened.

Example homebrew ability:

**Psychic Push** — once per round, make an attack; on hit deal 1d10 Psychic damage and force a DC 15 fear save.

Correct composition:

1. Universal attack roll.
2. Miss -> stop. No damage and no fear rider.
3. Hit -> roll 1d10 Psychic damage.
4. Run Psychic damage through universal immunity/resistance/vulnerability.
5. Because the hit occurred, evaluate the fear rider.
6. If target is immune to the relevant fear/frightened effect -> stop that rider.
7. Otherwise use the universal saving throw resolver against DC 15.
8. Success -> no condition.
9. Failure -> apply the universal Frightened/fear debuff using source-defined duration/expiry.
10. Once-per-round is declarative timing/resource data.

There must not be a `PsychicPushResolver`.

## Universal identity examples

Prone is Prone.
Grappled is Grappled.
Restrained is Restrained.
Frightened is Frightened.
Poisoned is Poisoned.
Advantage is Advantage.
Resistance is Resistance.
A saving throw is a saving throw.
Regeneration is Regeneration.
Recharge is Recharge.

The origin does not change the primitive.

## Edition order and reuse

Finish 2014 monster mechanics first.

For mechanics that also exist in 2024:
- reuse the certified universal primitive;
- bind the 2024 card's own parameters;
- add edition-specific behavior only when the printed semantics truly differ.

Do not build a second engine because the edition changed.

## Arena-neutral does not mean delete the ability

Printed abilities stay on the monster or pregen card/source data.

If an ability cannot affect the standard Iron Pit arena, classify its runtime effect as arena-neutral while preserving the printed name and source text.

Examples:
- no rocky terrain -> Stone Camouflage has no arena effect;
- no water/underwater context -> Underwater Camouflage has no arena effect;
- aquatic creatures can still breathe, swim, move, attack, and fight normally because the Pit magically supports their biology;
- environmental viability does not create the missing terrain/context.

## Future homebrew

Homebrew cards use this exact same engine.

The homebrew form must select/compose supported universal primitives and provide their parameters. It must not create arbitrary executable rules text or bespoke resolvers.

The long-term goal is the **smallest practical universal effect vocabulary that can express all supported RAW combat possibilities from pregens and monsters, plus future homebrew combinations**.

## Enforcement

Runtime behavior must not branch on:
- monster name;
- hero name;
- class name;
- subclass name;
- display ability name;

when equivalent semantic capability data can drive the result.

Identity may be used for:
- source parsing/binding;
- card display;
- logs;
- audit/certification evidence;
- deterministic canonical-build selection outside combat resolution.

If runtime needs to ask “is this a Fighter/Cleric/Troll/etc.?” to decide a mechanic, treat that as architecture debt and replace it with capability/data-driven resolution.
