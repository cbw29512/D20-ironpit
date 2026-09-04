# Iron Pit damage-scope policy

This file is durable program memory and is authoritative for spell, class ability, subclass ability, feat, monster ability, and similar combat-feature implementation unless the user explicitly changes scope.

## Core rule

Iron Pit models the **damage-affecting component** of spells and abilities. Secondary tabletop riders do not block certification when they are not required to determine damage.

Implement and certify:

- attack rolls, saving throws, target count/area only as needed to determine whether damage applies;
- damage dice, flat damage, damage type, critical-hit interaction, damage scaling, and slot-level damage scaling when Iron Pit supports that scaling;
- multiple damage components and per-type resistance/immunity where those change actual damage received;
- healing, temporary HP, resistance, immunity, and damage reduction only when the selected combat package intentionally uses them for survival/damage math;
- resource/action costs, recharge, limited-use counts, reactions, Bonus Actions, and Legendary Action costs only when needed to prevent illegal repeated damage output or determine how much damage can occur in a round.

Do **not** require implementation of secondary riders merely because the printed spell or ability includes them. Unless a rider directly determines damage, ignore it for Iron Pit certification. This includes conditions, speed changes, forced movement, visibility, object/environment effects, terrain, exploration utility, summons, social effects, and other non-damage rider text.

Examples:

- **Ray of Frost:** implement the ranged spell attack and cold damage; ignore the Speed reduction.
- **Fireball:** implement the Dexterity save, fire damage, and half damage on success; ignore object ignition.
- **Cone of Cold:** implement the Constitution save and cold damage; ignore non-damage aftermath.
- **Shatter:** implement the Constitution save and thunder damage; object damage and creature-type side rules do not block Iron Pit unless they directly change damage against a runnable combatant under the chosen arena scope.
- A class/subclass ability that adds damage dice or a flat rider must implement that damage. A separate push, prone, speed, fear, charm, or movement rider does not block the ability's damage certification.
- A monster attack that deals damage and also Grapples, Poisons, Knocks Prone, Pushes, or Frightens implements the attack/save and damage math; the secondary rider does not block damage certification.
- A breath weapon or other monster save action implements recharge/usage rules when needed, save DC, damage dice/type, and success damage. Secondary conditions do not block it.
- A damaging Legendary Action, Bonus Action, Reaction, or limited-use ability must preserve the action/resource cost that determines legal damage frequency; unrelated riders remain out of scope.

## Monster damage audit

All 330 canonical SRD monsters are audited under the same policy as pregens. Do not treat a monster as a bespoke combat-engine project.

For every monster, inspect attacks, Multiattack, saving-throw actions, traits, Bonus Actions, reactions, Legendary Actions, limited-use/recharge abilities, spellcasting, and defenses. Extract only the portions that can alter HP/damage output or damage received. Group identical mechanics across the entire catalog before implementing anything.

Shared monster/pregen damage families include:

- ordinary attack-roll damage and critical-hit dice;
- multiple typed damage components and on-hit damage riders;
- save-for-half / save-for-no-damage actions and areas;
- automatic-hit/projectile damage;
- multi-projectile and multi-target damage;
- persistent/repeated damage when it actually changes HP over later turns;
- recharge and limited-use damage resources;
- damage-dealing Bonus Actions, reactions, and Legendary Actions;
- damage resistance, immunity, vulnerability, Temporary HP, healing, and damage reduction;
- damage-affecting spellcasting using the same spell primitives as pregens.

A monster is not blocked merely because source text contains a condition/control/non-damage trait. It remains blocked only when an unsupported **damage-affecting** mechanic prevents accurate damage resolution or legal damage frequency.

## Architecture

Keep the implementation universal and data-driven. Spell/ability/monster data declares the required damage mechanics; shared attack/save/damage/healing/defense/resource engines resolve them. Do not create per-spell, per-class, or per-monster resolvers when a shared primitive can express the damage math.

Heroes and monsters must share the same primitive whenever their damage behavior is equivalent. A dragon breath weapon and a spell that both use a Dexterity save for typed area damage should flow through the same saving-throw/damage machinery; only their source data and resource/recharge rules differ.

Unsupported **damage-affecting** mechanics fail closed. Unsupported **non-damage secondary riders** are intentionally out of scope and do not block certification.

## Program order

1. Audit all canonical pregens and all 330 monster stat blocks for damage-affecting mechanics.
2. Deduplicate the combined hero/monster damage mechanic set.
3. Implement the highest-reuse shared primitives first.
4. Complete canonical pregen class/subclass-only damage components.
5. Ignore noncombat and non-damage secondary riders.
6. Certify canonical hero levels toward 240/240 while continuously re-auditing monsters against newly supported primitives.
7. Certify monsters in bulk as soon as their remaining damage-affecting blockers reach zero, continuing toward 330/330.
