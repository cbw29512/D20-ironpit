# Iron Pit Curated Spell Policy

This document is durable project policy for spell selection and spell AI in Iron Pit. It supplements `IRON_PIT_UNIVERSAL_COMBAT_DOCTRINE.md`. If a future implementation or older checkpoint conflicts with an explicit rule here, this policy controls unless the user later changes it.

## Core rule

Iron Pit does not attempt to reproduce the complete tabletop spell catalog.

> A spell with no effect on the mathematical outcome of an Iron Pit fight is not used by autonomous combat AI and cannot block certification.

Examples of arena-neutral utility magic include Zone of Truth, Detect Magic, Detect Evil and Good, Tongues, and similar exploration/social spells when they produce no supported combat consequence.

If a utility spell contains a combat-relevant component, decompose it exactly like any other mixed feature: keep the combat-math consequence and ignore the utility-only portion.

## Curated package philosophy

Caster packages must stay intentionally small, deterministic, and easy to resolve through universal engine primitives.

For a normal non-cleric caster package:

- normally include one straightforward combat buff;
- normally include one straightforward combat debuff;
- use direct damage spells for most remaining combat choices;
- theme the damage package to the caster when appropriate, such as fire-focused, cold-focused, or mixed damage;
- prefer spells resolved by existing universal attack-roll, saving-throw, damage, healing, AC, Advantage/Disadvantage, condition, reaction, resource, and concentration primitives;
- avoid spells that require bespoke simulation, unusual targeting mini-games, large terrain systems, summons, duplicate bodies/images, or other edge-case machinery when a simpler legal spell fills the same tactical role;
- complex spells can be considered later after the core monster and pregen program is complete.

Mirror Image is deliberately excluded from the current curated Iron Pit spell pool because it adds duplicate-image targeting/depletion logic without enough value for the present simplified combat model. Prefer mathematically simpler defensive spells such as Shield, Shield of Faith, direct AC modifiers, or other effects already representable through universal primitives.

## Magic Missile simplification

When Magic Missile is used in Iron Pit, all missiles from that casting strike one target. Iron Pit does not implement per-missile multi-target allocation at this stage.

The spell still resolves through the shared damage/resource system; this is a targeting simplification only.

## Counterspell and Dispel Magic

Counterspell and Dispel Magic are combat-relevant because preventing or ending an important spell can materially change the fight.

Their AI policy is deliberately selective and universal:

- use against substantial direct damage;
- use against domination or strong action-denial/control effects;
- use against strong buffs or debuffs when preventing/removing them is materially valuable;
- use against similarly high-impact combat effects;
- do not spend Counterspell or Dispel Magic on trivial nuisance effects or small modifiers, such as a minor `-1 to hit`;
- do not create different thresholds for individual monsters, classes, subclasses, or named abilities;
- keep the selection logic simple rather than building a full spell-theory planner.

The engine should compare the practical combat value of preventing/removing the effect, not merely whether the spell is technically legal to counter or dispel.

## Cleric role packages

Cleric spell selection is determined by combat role and evaluated per spell level.

### Healing cleric

For each spell level available to the cleric:

- select the healing spells appropriate to that level for the curated package;
- add exactly one non-healing combat choice for that spell level;
- that one non-healing choice may be a straightforward buff or a straightforward damage spell;
- avoid filling the healing cleric with additional offensive/control complexity beyond that one choice per spell level.

The intended identity is strongly healing-focused while still retaining one simple useful non-healing combat option at every spell level.

### Damage cleric

For each spell level available to the cleric:

- include exactly one healing spell for that spell level;
- use the remaining curated selections for straightforward damage/offense;
- prefer direct damage and simple combat math over complicated control or utility interactions.

The intended identity is strongly damage-focused while preserving one reliable healing option at every spell level.

### War cleric / balanced combat cleric

War clerics and other balanced combat-oriented cleric packages should use an approximately even mix of healing/support and damage/offense across their curated spell package.

The package does not need artificial exact symmetry if one spell level has a clearly better simple legal option, but the overall identity should remain balanced rather than drifting into healer-only or damage-only behavior.

## Bard packages

Bards follow the same curated Iron Pit spell path rather than carrying a full tabletop spell list.

- keep the package small and deterministic;
- favor a simple mix of one useful buff, one useful debuff/control option, and straightforward damage choices as spell levels permit;
- prefer buffs/debuffs that resolve through universal AC, attack/save modifier, Advantage/Disadvantage, condition, healing, or damage primitives;
- exclude social/exploration-only bard spells from runtime selection and certification blockers;
- avoid mechanically elaborate illusion, charm, summon, terrain, or multi-entity spells when a simpler legal bard spell provides a comparable combat role;
- add more exotic bard magic later only as a deliberate engine-expansion project.

The Bard should still feel like a support/control caster, but Iron Pit expresses that identity using a small set of mathematically clean combat spells rather than reproducing every tabletop option.

## Paladin packages

Paladins also follow the same curated Iron Pit spell path.

- keep the package small, deterministic, and combat-only;
- prefer straightforward healing, buffs, defenses, and damage/smite-style effects that reuse universal engine primitives;
- do not include utility-only paladin spells merely because they appear on the tabletop class list;
- avoid complicated aura, summon, terrain, or special-targeting spell machinery when a simpler legal paladin spell fills the same combat role;
- preserve the Paladin's hybrid martial/support identity without turning spell selection into a separate tactical subsystem;
- add harder paladin spells later only when deliberately selected for future engine expansion.

Paladin attacks, smites, healing, AC effects, Advantage/Disadvantage, conditions, and resources should reuse the same universal combat primitives used by monsters, clerics, bards, and every other Iron Pit combatant.

## Spell-level progression

Caster progression extends one deterministic class/role package over time rather than inventing a new spellbook at every level.

When a character gains access to a new spell level:

1. choose from the approved simple Iron Pit spell pool for that class/theme/role;
2. preserve the role ratios or class identity rules above;
3. prefer already-supported universal mechanics;
4. avoid introducing a complex new engine feature merely to match a tabletop spell when a simpler legal spell can fill the same combat role;
5. add harder spells later only when deliberately selected for a future engine-expansion tranche.

This progression rule explicitly applies to full casters and partial/half casters, including Cleric, Bard, Paladin, and other spellcasting classes represented in Iron Pit.

## Certification consequence

A monster or pregen is not blocked because its printed or class spell list contains arena-neutral utility magic that the Iron Pit AI will never select.

A selected curated combat spell must either resolve accurately through supported universal primitives or remain a real blocker.

Spell support is therefore a deliberate Iron Pit product surface, not an obligation to implement every RAW tabletop spell interaction.