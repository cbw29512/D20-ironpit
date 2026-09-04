# Iron Pit damage-scope policy

This file is durable program memory and is authoritative for spell, class ability, subclass ability, feat, monster ability, and similar combat-feature implementation unless the user explicitly changes scope.

## Core rule

Iron Pit models only the parts of D&D combat that change **Iron Pit combat math**. Heroes and monsters use the same mathematical engine; their abilities are data describing different inputs, triggers, resources, and damage formulas.

### Combat-math test

Before implementing any printed effect, ask one question:

> Does this effect change the probability, amount, frequency, timing, legality, prevention, or recovery of damage/HP in the Iron Pit combat loop?

If **yes**, it is in scope and must be modeled accurately. If **no**, it is ignored for runtime and does not block certification.

In scope includes effects that change:

- whether an attack or damaging ability can legally happen;
- attack rolls, saving throws, Advantage/Disadvantage, AC, save DC, or other math that changes whether damage lands;
- action economy when it changes how many damaging/healing actions can occur, including losing/gaining an Action, Bonus Action, Reaction, Extra Attack, Multiattack, Legendary Action, or similar damage opportunity;
- damage dice, flat damage, damage type, critical-hit interaction, damage scaling, multiple damage components, target count, or area only where needed to determine actual damage;
- resource/action costs, spell slots, recharge, limited-use counts, reactions, Bonus Actions, and Legendary Action costs when they constrain legal damage output;
- resistance, immunity, vulnerability, damage reduction, Temporary HP, healing, regeneration, or other HP/survival math;
- persistent/repeated damage and conditions whose ongoing state directly changes damage or available damaging actions.

Out of scope includes effects that only change tabletop state we do not simulate and therefore do not alter Iron Pit combat math, including:

- movement speed changes by themselves;
- forced movement by itself;
- terrain, exploration, social, object, environmental, visibility, or narrative effects that do not alter damage resolution in the Pit;
- conditions or riders whose only consequence is an out-of-scope state change;
- summons or utility effects not selected as part of the simplified Iron Pit damage model.

A printed label never decides scope by itself. The mathematical consequence does.

Examples:

- **Movement-only slow/curse:** ignore it if it only reduces Speed and the Pit combatant can still take the same legal damaging action under the arena model.
- **Slow/curse that removes or denies an Action:** model it because losing the Action changes legal damage output.
- **Ray of Frost:** implement the ranged spell attack and cold damage; ignore the Speed reduction.
- **Fireball:** implement the Dexterity save, fire damage, and half damage on success; ignore object ignition.
- **Cone of Cold:** implement the Constitution save and cold damage; ignore non-damage aftermath.
- **Shatter:** implement the Constitution save and thunder damage; object damage and creature-type side rules do not block Iron Pit unless they directly change damage against a runnable combatant under the chosen arena scope.
- A class/subclass ability that adds damage dice or a flat rider must implement that damage. A separate push, prone, speed, fear, charm, or movement rider does not block the ability unless that rider also changes Iron Pit damage math.
- A monster attack that deals damage and also Grapples, Poisons, Knocks Prone, Pushes, or Frightens implements the attack/save and damage math. Any secondary consequence is ignored unless it changes Iron Pit attack/save/damage/action math.
- A breath weapon or other monster save action implements recharge/usage rules when needed, save DC, damage dice/type, and success damage. Secondary conditions do not block it unless they change later damage math.
- A damaging Legendary Action, Bonus Action, Reaction, or limited-use ability must preserve the action/resource cost that determines legal damage frequency; unrelated riders remain out of scope.

## Ambiguity rule

If it is unclear whether an effect changes Iron Pit combat math, do **not** guess, broaden the engine, or silently ignore it. Stop that specific mechanic and ask the user a focused scope question before implementing it. Continue unrelated work that is already unambiguous.

## Monster damage audit

All 330 canonical SRD monsters are audited under the same policy as pregens. Do not treat a monster as a bespoke combat-engine project.

For every monster, inspect attacks, Multiattack, saving-throw actions, traits, Bonus Actions, reactions, Legendary Actions, limited-use/recharge abilities, spellcasting, healing, and defenses. Extract only the portions that can alter HP/damage output, legal damage frequency, or damage received. Group identical mechanics across the entire catalog before implementing anything.

Shared monster/pregen damage families include:

- ordinary attack-roll damage and critical-hit dice;
- multiple typed damage components and on-hit damage riders;
- save-for-half / save-for-no-damage actions and areas;
- automatic-hit/projectile damage;
- multi-projectile and multi-target damage;
- persistent/repeated damage when it actually changes HP over later turns;
- recharge and limited-use damage resources;
- damage-dealing Bonus Actions, reactions, and Legendary Actions;
- damage resistance, immunity, vulnerability, Temporary HP, healing, regeneration, and damage reduction;
- action-denial or action-granting effects only when they alter legal damage/healing frequency;
- damage-affecting spellcasting using the same spell primitives as pregens.

A monster is not blocked merely because source text contains a condition/control/non-damage trait. It remains blocked only when an unsupported **combat-math-affecting** mechanic prevents accurate Iron Pit resolution.

## Architecture

Keep the implementation universal and data-driven. Spell/ability/monster data declares the required combat-math mechanics; shared attack/save/damage/healing/defense/resource/action-economy engines resolve them. Do not create per-spell, per-class, or per-monster resolvers when a shared primitive can express the math.

Heroes and monsters must share the same primitive whenever their in-scope behavior is equivalent. A dragon breath weapon and a spell that both use a Dexterity save for typed area damage should flow through the same saving-throw/damage machinery; only their source data and resource/recharge rules differ.

Unsupported **combat-math-affecting** mechanics fail closed. Unsupported **non-Iron-Pit secondary effects** are intentionally out of scope and do not block certification.

## Program order

1. Audit all canonical pregens and all 330 monster stat blocks for combat-math-affecting mechanics.
2. Deduplicate the combined hero/monster mechanic set.
3. Implement the highest-reuse shared mathematical primitives first.
4. Complete canonical pregen class/subclass-only combat-math components.
5. Ignore noncombat and non-Iron-Pit secondary effects.
6. Certify canonical hero levels toward 240/240 while continuously re-auditing monsters against newly supported primitives.
7. Certify monsters in bulk as soon as their remaining combat-math blockers reach zero, continuing toward 330/330.
