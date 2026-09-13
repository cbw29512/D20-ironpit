# Iron Pit Arena Profile

This file is the authoritative arena-policy layer for Iron Pit. It applies to monsters and pregens in every ruleset unless a later explicit product decision changes it.

When this arena profile conflicts with older wording in `docs/IRON_PIT_RULES_CONTRACT.md`, this profile controls the arena-specific behavior until the older wording is folded into the main contract.

## 1. Universal architecture

- Monster and pregen cards preserve immutable source data and declare capabilities.
- The shared combat engine resolves those capabilities. Do not add monster-name, hero-name, class-name, or stat-block-name runtime branches when a universal mechanic can represent the behavior.
- Arena policy is universal. A mechanic disabled by the Iron Pit is disabled for every combatant, not only the creature that first exposed the mechanic.
- An arena-disabled or arena-out-of-scope mechanic is preserved in source provenance where practical but is not a certification blocker.
- A combat-relevant mechanic that is neither supported nor explicitly disabled/out-of-scope continues to fail closed.

## 2. Pocket-dimension boundary

The Iron Pit is a closed pocket dimension built for direct combat. Combatants cannot leave the battlefield during a match.

The following are arena-disabled:

- teleportation and teleport-like repositioning;
- Misty Step, Dimension Door, Teleport, Plane Shift, Word of Recall, and similar travel abilities;
- ethereal travel or phasing through the arena boundary;
- banishment or other temporary removal from the battlefield;
- escape, fleeing, surrender, morale retreat, or travel outside normal battlefield movement.

Forced movement may move a combatant only to the last legal space inside the arena. Contact with an arena wall causes no extra damage unless the source effect explicitly deals such damage.

## 3. Movement modes

Normal tactical movement remains relevant, subject to these arena rules:

- Burrowing is arena-disabled. The Iron Pit floor is impenetrable.
- Flight is allowed, but altitude can never make a combatant unreachable by melee.
- Climb and Spider Climb remain usable movement capabilities, but wall position can never make a combatant unreachable by melee.
- Swim and other ordinary source-derived movement modes may be preserved, but the arena does not create special environmental terrain merely to make them tactically advantageous.
- No combatant voluntarily kites, flees, or moves toward an arena edge for self-preservation.

## 4. No additional combatants

A match never creates an additional combatant after deployment.

Arena-disabled mechanics include:

- summoning or conjuring creatures;
- spawning minions;
- creating duplicate combatants;
- animating reinforcements;
- splitting one creature into additional creature instances;
- any equivalent mechanic whose primary result is adding another combatant.

A source ability may retain independently valid non-creation effects only when its source wording supports resolving those effects separately.

## 5. No destructible environment

The Iron Pit itself cannot be damaged or destroyed.

The following are arena-out-of-scope:

- Siege Monster bonuses against objects or structures;
- attacks whose only combat purpose is damaging doors, walls, buildings, terrain, or other objects;
- destructible cover, bridges, doors, structures, traps, or terrain unless a future Iron Pit mode explicitly adds them.

The standard arena provides no environmental cover, pits, lava, natural difficult terrain, trees, doors, weather, or similar adventure terrain.

## 6. Lair and regional mechanics

Lair Actions and Regional Effects are arena-disabled. The Iron Pit is not the creature's lair.

Legendary Actions and Legendary Resistance remain enabled and must use the shared universal timing/resource engine.

## 7. Combat-only consequence window

Effects whose first meaningful consequence occurs only after the match are arena-out-of-scope. Examples include delayed diseases, infections, aging, curses, or transformations that have no effect during the current fight.

If such an effect also has an immediate combat consequence, the immediate combat consequence remains relevant and must be resolved.

All combatants are restored by the Iron Pit after the match; post-match persistence is not simulated.

## 8. Information and subjective behavior

The Arena AI has authoritative combat-state knowledge. It does not simulate uncertainty that has no deterministic combat rule.

- Invisibility remains enabled as a mechanical Advantage/Disadvantage and targeting effect. AI knowledge does not cancel its rules effects.
- Subjective deception, disguises, mimicry, social manipulation, languages, telepathy, infiltration, and noncombat utility are arena-out-of-scope unless a deterministic combat rule changes the fight.
- Deterministic combat illusions such as effects that directly alter attack rolls, defenses, targeting, or damage remain eligible for universal support.
- The AI does not invent generic Help, Search, Ready, Shove, or Grapple tactics unless a supported printed combat capability or fallback policy specifically calls for them.

## 9. Control and fear

Hard control that effectively ends the automated fight by transferring command or removing a combatant from meaningful participation is arena-disabled, including domination, possession, forced team switching, and equivalent control.

Charm and Fear may remain only as deterministic Iron Pit combat debuffs. They may not force a combatant to leave the arena. Exact universal break/save behavior must be defined once before certification relies on those effects.

## 10. Supported combat identity

The engine should spend its complexity budget on mechanics that can materially change the winner inside the Pit, including:

- attacks, Multiattack, Extra Attack, and action economy;
- saving throws and deterministic combat conditions;
- damage, resistance, immunity, vulnerability, reduction, absorption, and Temporary HP;
- healing and regeneration;
- ongoing effects using their exact printed timing;
- normal and forced movement inside the arena;
- Grappled, Restrained, Prone, Swallow, and Engulf mechanics;
- reactions and projectile interception such as Rock Catching;
- Recharge and other limited resources;
- area effects and combat spellcasting;
- transformations and forms;
- Legendary Actions and Legendary Resistance;
- death, zero-HP replacement, and on-death effects.

## 11. Certification rule

For certification, classify mechanics using this order:

1. If universally supported, resolve them through the shared engine.
2. If explicitly arena-disabled or arena-out-of-scope by this profile, preserve source provenance and do not block certification.
3. Otherwise, if the mechanic can change an Iron Pit combat outcome, fail closed and keep it as a blocker.

Do not implement a disabled mechanic merely to increase the ready count. Do not silently ignore an outcome-changing mechanic that this profile has not explicitly removed.
