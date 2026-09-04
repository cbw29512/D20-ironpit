# Iron Pit damage-scope policy

This file is durable program memory and is authoritative for spell, class ability, subclass ability, feat, and similar combat-feature implementation unless the user explicitly changes scope.

## Core rule

Iron Pit models the **damage-affecting component** of spells and abilities. Secondary tabletop riders do not block certification when they are not required to determine damage.

Implement and certify:

- attack rolls, saving throws, target count/area only as needed to determine whether damage applies;
- damage dice, flat damage, damage type, critical-hit interaction, damage scaling, and slot-level damage scaling when Iron Pit supports that scaling;
- multiple damage components and per-type resistance/immunity where those change actual damage received;
- healing, temporary HP, resistance, immunity, and damage reduction only when the selected combat package intentionally uses them for survival/damage math;
- resource/action costs only as needed to prevent illegal repeated damage output.

Do **not** require implementation of secondary riders merely because the printed spell or ability includes them. Unless a rider directly determines damage, ignore it for Iron Pit certification. This includes conditions, speed changes, forced movement, visibility, object/environment effects, terrain, exploration utility, summons, social effects, and other non-damage rider text.

Examples:

- **Ray of Frost:** implement the ranged spell attack and cold damage; ignore the Speed reduction.
- **Fireball:** implement the Dexterity save, fire damage, and half damage on success; ignore object ignition.
- **Cone of Cold:** implement the Constitution save and cold damage; ignore non-damage aftermath.
- **Shatter:** implement the Constitution save and thunder damage; object damage and creature-type side rules do not block Iron Pit unless they directly change damage against a runnable combatant under the chosen arena scope.
- A class/subclass ability that adds damage dice or a flat rider must implement that damage. A separate push, prone, speed, fear, charm, or movement rider does not block the ability's damage certification.

## Architecture

Keep the implementation universal and data-driven. Spell/ability data declares the required damage mechanics; shared attack/save/damage/healing/defense engines resolve them. Do not create per-spell, per-class, or per-monster resolvers when a shared primitive can express the damage math.

Unsupported **damage-affecting** mechanics fail closed. Unsupported **non-damage secondary riders** are intentionally out of scope and do not block certification.

## Program order

1. Audit all canonical pregens.
2. Deduplicate shared damage/healing/defense primitives.
3. Implement shared primitives first.
4. Add class/subclass-only damage components second.
5. Ignore noncombat and non-damage secondary riders.
6. Certify canonical hero levels toward 240/240.
7. Reuse the same damage primitives for monsters.
