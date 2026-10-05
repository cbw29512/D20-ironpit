# Universal Combatant Architecture

This is the durable implementation contract for D20 Iron Pit.

## KISS principle

Build the character or monster first. Combat reads that finished creature.

Do not build separate combat systems for classes, subclasses, weapon styles, heroes, or monsters. A combatant is data plus a small set of shared capabilities.

`RAW source -> class/monster data -> subclass specialization -> finished combatant -> shared engine`

## Combatant truth

A finished combatant owns the facts needed by combat:

- ability scores and derived modifiers;
- HP, AC, Speed, initiative, saves, and relevant skills;
- Action, Bonus Action, Reaction, movement, and limited resources;
- armor, shield, weapons, weapon properties, and selected Weapon Masteries;
- Fighting Styles and combat-relevant feats/features;
- spells, spell slots/resources, and spellcasting numbers;
- resistances, vulnerabilities, immunities, conditions, and concentration;
- declared attacks/actions and any other RAW outcome-changing fact.

The engine does not infer rules from a class name, subclass name, hero name, monster name, or display text when the needed fact can be stored directly.

## One universal combat engine

Every normal combatant uses the same baseline:

- one Action;
- one Bonus Action opportunity;
- one Reaction, refreshed at the normal time;
- movement equal to effective Speed.

Features modify that baseline; they do not create another turn engine.

Examples:

- Extra Attack changes the number of attacks in the Attack action.
- Action Surge grants another eligible Action.
- Multiattack is a declared monster action containing its attacks/effects.
- Nick changes the timing/cost of the normal Light extra attack.
- Legendary Resistance changes an eligible failed save into success using a resource.

Saving throws are always shared math:

`d20 + creature save modifier + shared modifiers vs DC`

Post-roll D20 replacement is also a shared primitive. Source data declares the resource, replacement natural roll, eligible D20 Test kinds, and exact source name; the attack/save/check resolver remains generic. A rule that replaces a failed D20 roll with 20 is **not** mechanically equivalent to a rule that merely converts a missed attack into a normal hit. Preserve that distinction rather than forcing both through one named-feature shortcut.

Attack rolls, ability checks, AC, damage defenses, conditions, concentration, and movement follow the same rule: one resolver, different creature data.

## Mandatory semantic reuse workflow

This workflow is required for every content implementation, regardless of whether the source is a class, subclass, species, feat, spell, item, monster, legendary action, or other combat rule.

`source wording -> semantic decomposition -> existing primitive search -> bind/parameterize/compose -> new primitive only if unavoidable -> source-name log label`

The semantic decomposition is based on what the ability **does**, not what it is called. Compare:

- trigger and timing;
- action/reaction/resource cost;
- target/range/geometry;
- attack/check/save/recharge mechanics;
- damage/healing/state effects;
- conditions and modifiers;
- duration and lifecycle;
- use limits and reset rules;
- interrupts/overrides.

Two differently named abilities with the same semantics use the same engine capability. A hero ability and monster ability with the same semantics use the same engine capability. A 2014 and 2024 ability with the same semantics use the same engine capability. Minor differences become parameters or ruleset data.

A named ability that consists of multiple known effects must be assembled from the corresponding universal primitives. Do not create a monolithic ability-specific resolver simply to preserve the source name. Preserve the exact source name in event metadata and logs so the player sees the correct ability name while the engine executes reusable mechanics underneath.

The content card owns **parameters**, not mechanics. For example, a monster action that knocks a target Prone supplies the source ability name, attack/save trigger, save ability, DC or DC formula, damage, range, duration, and resource/recharge facts. It invokes the same universal Prone behavior used by a hero feature, spell, mastery, or another monster. Do not create separate `monster-prone`, `rogue-prone`, or `spell-prone` implementations.

Before new mechanic code is allowed, record why existing primitives cannot represent the behavior. If that cannot be shown, reuse wins.

## Mandatory preflight before touching any ability

**STOP AND READ THIS SECTION BEFORE IMPLEMENTING OR MODIFYING ANY CLASS, SUBCLASS, FEAT, SPELL, ITEM, MONSTER, LEGENDARY ACTION, LAIR ACTION, OR OTHER COMBAT ABILITY.**

This checklist is mandatory on every implementation pass:

1. Read `docs/IRON_PIT_RULES_CONTRACT.md`, `docs/PREGEN_AND_CONTENT_RULES_CONTRACT.md`, and this universal architecture section relevant to the mechanic.
2. Ignore the source ability's name when deciding engine behavior. First determine what the ability actually does.
3. Decompose it into semantic pieces: trigger/timing, action cost, target/range, attack/check/save, DC/formula, damage/healing, condition/state change, duration/expiry, resource/recharge, and reaction/override behavior.
4. Search the complete existing hero **and monster** capability inventory for each semantic piece.
5. Reuse an existing universal primitive whenever the mechanical effect is equivalent.
6. Minor differences belong in source/card parameters: DC, save ability, dice, damage type, range, duration, target count, resource count, recharge, timing, ruleset, and similar data.
7. If the named ability combines several known effects, compose those existing primitives. Do not create a monolithic resolver for the source name.
8. **Prone is Prone. Grappled is Grappled. Advantage is Advantage. Resistance is Resistance. A saving throw is a saving throw.** The mechanic does not change because it came from a monster, hero, spell, item, subclass, or another edition.
9. The source/card owns the exact source ability name and parameters. The universal engine owns resolution.
10. Player-facing logs/cards use the accurate source ability name. Internal audit/certification may also store the generic capability IDs used underneath.
11. Only after proving no current primitive or composition can represent the behavior may `ENGINE_TRULY_MISSING` justify new universal engine code.
12. After adding a genuinely new primitive, immediately re-audit heroes and monsters for other abilities that can now reuse it.

**2014-first pregen rule:** for overlapping class progressions, finish/reconcile the 2014 mechanic first, bind it to universal capabilities, then carry all mechanically compatible behavior into 2024 and implement only the true 2024 differences.

If there is uncertainty about whether two abilities are semantically the same, stop and ask Chris before creating new engine behavior.

## Primitive versus trigger contract

Before adding any new resolver, combat subsystem, or special handler, classify the source behavior first:

1. **Engine primitive:** the universal rule being resolved, such as Advantage/Disadvantage, damage, a Saving Throw, a condition, healing, a resource, concentration, or movement.
2. **Trigger/source/configuration:** the declarative fact that says when or how that existing primitive applies.

If an existing engine primitive can express the outcome, do not create another mechanic. Add data or a small source predicate that feeds the existing resolver.

Examples:

- Advantage is one engine primitive. Hidden, Pack Tactics, Vex, a target missing any HP, and legal Prone attack geometry are Advantage sources/triggers; they do not get separate Advantage engines.
- Disadvantage is one engine primitive. Poisoned, Frightened, long range, or a live source-owned environment context such as sunlight with matching target-owned reaction data are Disadvantage sources/triggers.
- Damage is one engine primitive. Slashing, Piercing, Fire, and similar values are damage types; resistance, immunity, and vulnerability modify that same damage pipeline.
- Saving Throw is one engine primitive. Ability, DC, success/failure effect, repeat timing, and recharge/use limits are declarative parameters around the shared save resolver.
- Contextual save defenses stay defender-owned and declarative. A source may require semantic effect tags such as `poison`; the incoming save/effect supplies those tags, and the shared save modifier stack performs the match alongside magical/spell/source-creature qualifiers. Never branch on race, class, monster, spell, or feature names to grant that Advantage.

A helper dedicated to determining whether a source is active is allowed, but it must not roll dice, choose a separate roll mode, duplicate the primitive's resolution rules, or bypass the canonical resolver.

Permanent tests for a new trigger must prove that it contributes to the existing primitive and that cancellation/stacking/expiry still use the shared engine behavior.

If it is not completely clear whether source wording represents a genuinely new primitive or only another trigger/configuration for an existing one, stop and ask Chris before coding. Record the answer in the appropriate authoritative repository document before implementation.


## Sequencing primitive contract

Turn and attack timing are shared engine primitives, not ability-specific call chains.

The browser sequencing surface is a fixed phase registry defined by `browser-ability-hooks.js`. Ability modules may register into canonical phases, but the shared turn/attack orchestrators must not accumulate named ability branches after a phase is migrated.

Each hook registration must declare its supported ruleset scope explicitly. A shared registration names both `2014` and `2024`; an edition-specific registration names only that edition.

Hook results separate emitted events from action-window consumption. Producing an event never implicitly consumes an Action or Bonus Action. Exclusive phases are consumed only by an explicit `claimed=true` result from the resolver that actually uses that opportunity.

Hook priority is deterministic evaluation order, not tactical preference. Existing Arena AI / action-selection policy remains responsible for choosing among independent legal actions.

Main Action selection therefore uses a separate candidate/selection contract. Action-family modules discover legal candidates; an explicit opportunity profile chooses among categories in the already-certified Arena order. Provider registration order is never tactical policy, and Action Surge or other extra Action opportunities must supply an explicit allowed-category profile rather than inheriting every normal Action family. See `docs/MAIN_ACTION_SELECTION_CONTRACT.md`.

Nested riders stay nested when they are not independent action choices. For example, a feature triggered only by another feature remains part of its parent feature's resolution instead of registering as a competing action.

Before any browser phase migration changes live behavior, identify the equivalent Python reference resolution point, action-economy lifecycle, ruleset data, and permanent parity tests. The detailed contract and migration sequence live in `docs/ABILITY_HOOK_ENGINE_PROPOSAL.md`.

## Arena movement policy

Movement mechanics and movement policy are separate.

The movement engine owns legal squares, footprints, pathfinding, movement cost, difficult terrain, collision, Opportunity Attacks, forced movement, and other rules. Arena AI only chooses the simplest legal destination needed to use the combatant's actions.

Default Iron Pit voluntary movement policy is intentionally simple:

1. The combatant's goal is to engage and defeat a living opponent; it does not wander around the arena without an action-driven reason.
2. If a legal melee attack can be made this turn after useful legal approach movement, the combatant closes to that melee reach, then uses the highest-damage option that can actually land from there. A landable area/save Action or damage spell beats weaker melee. Multiattack printed damage includes every landable slot.
3. Front-row combatants are melee. They make useful legal progress toward melee even when a backup thrown/ranged attack could already land. After that approach, if melee still cannot land, they use the highest-damage option that can land.
4. Back-row combatants are ranged and/or casters. They stay in place when a legal ranged or spell option can already land. A back-row melee creature with no ranged attack steps to the front when the last front-row ally dies, or Dodges until that step-up is legal.
5. If a ranged combatant is already in melee and has a legal melee option, it uses the legal melee option rather than retreating merely to preserve range.
6. A caster does not retreat or hold range merely to preserve a spell. It casts from its current square when that spell is the highest-damage option that can land, including after it has already closed.
7. A mixed combatant uses the landing-damage rule after row policy: the highest-damage option that can actually land; melee when in reach instead of a ranged weapon; Dodge only if nothing lands.
8. Default Arena AI does not voluntarily kite, circle, run to map edges, seek cover, disperse, or retreat merely for positional optimization.
9. Specific printed features, conditions, forced movement, explicit retreat effects, or other RAW mechanics may require movement that overrides this default policy; those effects still use the same universal movement engine.

The 24 x 16 arena therefore uses a capable pathfinder with deliberately simple destination policy. Pathfinding solves **how to reach a legal action position**; it does not invent tactical goals.

### Offensive exhaustion before Dodge

Dodge is the final legal-action fallback, never a substitute for a legal offensive option and never a way to hide an engine error.

Before the Arena AI may choose Dodge, it must establish that the combatant cannot produce a legal offensive action this turn in any supported offensive family, including after legal movement that can make the action usable:

1. no legal melee attack;
2. no legal ranged attack;
3. no legal offensive spell;
4. no other legal offensive attack, SavingThrowAction, Multiattack/signature action, or supported damaging/control ability.

This checklist is the Dodge fallback gate. Arena Action selection is the landing-damage rule: take the highest-damage option that can actually land; if melee can land, do not spend the Action on a ranged weapon; if no supported offensive family can be used or made legal, Dodge. Control loses to raw damage. Dodge is never a substitute for a legal offensive option and never hides an engine error.

If the combatant is physically blocked, lacks sufficient movement, has no valid path, has no target in usable range after movement, or otherwise cannot make any supported offensive option legal without violating RAW, it takes the shared Dodge action if its Action is available. This is an ordinary combat outcome, not an engine exception.

Unsupported mechanics, malformed state, mixed position authority, impossible source data, and other engine/rules errors must still fail closed; they must never be converted into Dodge.

## Class -> subclass -> specialization

A class is built once through the levels before subclass choice.

At the subclass level, each chosen subclass gets one coherent combat specialization that makes sense for that subclass. Do not create several weapon clones inside one subclass just to exercise different weapons.

For a martial/hybrid specialization the data is intentionally small:

- subclass id;
- role;
- ability priority;
- armor and shield;
- primary weapon and a few backups;
- Fighting Style priority when the class grants one;
- Weapon Mastery priority when the class grants mastery;
- optional spell package for hybrids.

The specialization does **not** contain Nick, Graze, Vex, Sap, or similar rule implementations. It only selects weapons/masteries/styles. The weapon catalog and shared mechanics do the rest.

### Fighter target

The 2024 Fighter branches into four Player's Handbook subclasses, with one arena specialization each:

1. **Champion -> two-handed**: Greatsword, Strength, Great Weapon Fighting; Champion's later second Fighting Style is another data choice.
2. **Battle Master -> dual wield**: Shortsword + Scimitar, Dexterity, Two-Weapon Fighting; Vex/Nick come from those weapons when mastered.
3. **Eldritch Knight -> sword and shield**: Longsword + Shield, Strength/Intelligence emphasis, defensive Fighting Style, plus its legal spell package.
4. **Psi Warrior -> ranged**: Longbow, Dexterity/Intelligence emphasis, Archery, and appropriate ranged mastery choices.

The exact equipment/feat/spell choices remain auditable data and may be improved when a more legal/effective option is proven. Changing a loadout must not require a new combat engine.

### Other classes

For every other class:

1. build one base character through levels 1-2;
2. choose three useful, distinct subclasses at level 3;
3. give each subclass one coherent specialization;
4. level each subclass specialization through 20 using the same class progression table plus the subclass's feature table.

Do not invent three artificial variants of the same subclass.

## Weapon specialization contract

Weapon specialization is data.

Example:

```text
Battle Master
primary weapon = Shortsword
secondary weapon = Scimitar
style = Two-Weapon Fighting
mastered weapons include Shortsword and Scimitar
```

The catalog already says:

```text
Shortsword: Light, Finesse, Vex
Scimitar: Light, Finesse, Nick
```

The engine asks only:

`mastery active = weapon has mastery property AND weapon id is in combatant.weapon_masteries`

Then it dispatches the tiny shared handler:

- Graze -> miss effect;
- Vex -> target-scoped next-attack Advantage after the qualifying hit;
- Sap -> next qualifying attack Disadvantage;
- Nick -> move the existing Light extra attack into the Attack action.

No Fighter/Battle Master/Champion/Rogue/Ranger name check belongs in those handlers.

If the weapon or mastery is absent, skip the mastery code path entirely.

## Caster specialization contract

Casters use the same idea, with spell packages doing most of the specialization work.

A caster specialization declares:

- subclass/theme;
- casting ability priority;
- focus/weapon or magic-item slot;
- legal cantrip/spell package;
- optional precombat buff priorities;
- deterministic combat priority.

Examples of useful themes, when supported by the actual subclass/spell list:

- fire-focused damage;
- cold/frost-focused damage/control;
- elemental/generalist damage and control;
- enchantment/mind-control;
- healing/support;
- summoning or battlefield control.

The spell package contains desired spells, but the level compiler exposes only spells the character can legally know/prepare/cast at that level.

Arena AI is deterministic policy, not a new rule system. A simple default is:

1. apply exactly one legal opening buff under the pit rule below;
2. if a legal melee attack can land this turn, use the highest-damage melee option;
3. otherwise prefer the highest-damage landable option, with the highest-level damage spell first among spells;
4. fall back through remaining landable damage options;
5. use cantrips when leveled damage is exhausted;
6. use charm or other control only when no damaging option can land.

RAW determines what the caster **can** do. Arena policy determines which legal option it **chooses**.

## Leveling contract

Levels should be data rows, not twenty bespoke implementations.

A class progression row changes only what that level changes, for example:

- proficiency bonus;
- HP from the class Hit Die/Constitution progression;
- resource counts;
- ASI/feat/boon choices;
- Extra Attack count;
- new class features;
- new subclass features;
- new spell slots/spell access;
- new mastery count.

The compiler derives AC, attacks, damage modifiers, saves, spell DCs, resources, and legal actions from the finished level snapshot.

A new level that only changes numbers should normally require no new combat mechanic.

## Combat-relevant-only runtime

Keep full character truth where useful, but do not implement noncombat text in the arena engine unless it can change an Iron Pit outcome.

For every feature:

```text
Can this feature alter an Iron Pit combat result?
NO  -> retain as profile/source data if desired; no runtime combat handler.
YES -> represent the needed fact and use/add one shared mechanic.
```

Arena-out-of-scope is a deliberate product-scope classification, never a substitute for an outcome-changing RAW rule.

## Permanent passive buff compilation

Always-on combat protections are declarative source data, not bespoke turn resolvers.

- A permanent source-owned buff that maps to existing modifier semantics is stored as passive modifier grants on the immutable combatant template.
- Fresh combat state compiles those grants into the same universal active-modifier stack used by spells and other buffs.
- The grant supplies only source identity and parameters such as modifier kind, condition id, and qualifying source creature types.
- Existing attack, saving-throw, condition-immunity, buff/debuff, and lifecycle rules consume the compiled modifiers without checking class, subclass, monster, spell, or feature names.
- Passive modifiers are rebuilt from the template for every match; combat never mutates the source template.
- Player-facing logs/cards retain the printed source ability name while internal runtime/audit data may retain the generic modifier kind.

## Shared capability pattern

For any new combat mechanic:

1. identify the minimum facts that prove the creature has it;
2. store those facts in character/monster data;
3. add one small generic predicate/handler;
4. call it from the natural shared resolution point;
5. test Python and browser parity;
6. make CI execute that regression permanently;
7. re-audit all heroes and monsters that now meet the same conditions.

Do not begin with class-specific turn logic.

## Monsters

Monsters follow the same model:

`stat block -> declarative combatant -> shared runtime`

If a monster already uses supported mechanics, adding it should mostly be data and certification. A genuinely new outcome-changing trait justifies one new shared handler.

## Certification

A combatant is runnable only when:

- its source data/build is legal and audited;
- the compiled runtime matches the declared creature;
- every combat-relevant capability present on that creature is supported or explicitly arena-out-of-scope;
- Python and browser consume equivalent facts;
- permanent regression evidence exists;
- generated artifacts/manifests match;
- exact-head CI is green.

An incomplete subclass, spell package, weapon property, or feature stays blocked. Never approximate it just to increase the ready count.

## Migration from the older variant model

The older `four Champion variants / three variants per canonical subclass` structure is migration scaffolding, not the target architecture.

Migration order:

1. preserve already-certified shared mechanics;
2. make subclass specialization records authoritative;
3. map Champion to the two-handed Fighter specialization first;
4. add audited Battle Master, Eldritch Knight, and Psi Warrior subclass progression data;
5. compile each Fighter subclass specialization through 20 from the one Fighter class table;
6. retire the old multi-variant Champion files after equivalent tests/certification no longer depend on them;
7. research and select three coherent subclasses for each remaining class;
8. give each one a single weapon/spell specialization record;
9. compile all levels from class + subclass + specialization data;
10. keep reusing the shared mechanics inventory across heroes and monsters.

The roster migration is complete: twelve class spines now branch into thirty-seven class-owned
subclass specializations. `data/roster_combat_mechanics_v1.json` is the generated implementation
checklist. It is derived from those class spines, sparse subclass rows, specialization choices,
spell-package pointers, and loadout capabilities; CI rejects manual or stale checklist edits.

## Non-negotiable invariants

- KISS: specialization is mostly data.
- Characters and monsters are the source of combat truth.
- Names are not rule switches.
- The same mechanic is implemented once.
- Weapon mastery requires both the weapon mastery property and the combatant's mastery of that weapon.
- Casters receive only spells legal for their level/build.
- Noncombat rules do not bloat the arena engine.
- Unsupported outcome-changing mechanics fail closed.
- Python/browser parity stays mandatory.
- Production source-size limits stay enforced.
- Active means executable and certified.


## Opening buff pit rule

Before initiative, each combatant that has a legal combat buff uses **exactly one** as a free opening action. If more than one buff is legal, the shared precombat pipeline selects the **highest-level** option only; non-spell abilities compete as level 0, and same-level ties use declarative priority. The activation does not spend Action, Bonus Action, or Reaction. Do not apply every known buff. This is pit setup policy, not a seeded starting debuff. Production presets and player-loaded fights still start with an empty opening-condition list.

## Turn-start debuff answers

The start-of-turn phase reads the acting creature's live conditions before voluntary actions. Condition identity is absolute: Frightened is Frightened, Charmed is Charmed. A beneficial failed-save modifier of kind `condition-immunity` or `debuff-counter` answers the matching condition on a legal friend. Bloodied (current HP at or below half of maximum) is answered by healing. An already-active matching counter-buff keeps the printed condition instance in state but `has_condition` is false, and a new application of that same condition fails closed. Selection is by modifier kind and condition id, never by spell or monster name. A test harness may seed a starting buff or debuff. Player-loaded fights and website presets must pass an empty opening-condition list.

## Timed source-owned emanations

Timed self effects may declare a source-owned emanation that resolves against opposing combatants at a fixed lifecycle window. The source ability supplies declarative parameters such as trigger, radius, fixed damage, and damage type; engine dispatch must not branch on the source ability name.

For an `enemy_turn_start` emanation, the universal turn-start phase discovers active source-owned timed effects, evaluates shared battlefield distance/geometry, applies the normal typed damage-defense and zero-HP lifecycle, and emits the source ability name only as presentation/audit metadata. Expiry remains owned by the underlying timed-effect lifecycle, so ending the timed effect automatically ends its emanation and any source-owned modifiers.

Python and browser implementations must preserve behavioral parity. A new named class, spell, monster, or item feature that has the same timing/range/damage semantics binds to this component instead of adding another resolver.

## Finite modifier spells and threshold targeting (2014 audit correction)

HP-threshold source actions declare `requires_target_sight`; legality consumes the ordinary universal visibility predicate before any resource or Action spending. The browser serializers preserve the same flag. 2014 Power Word Kill/Stun require sight; other sources retain their independently audited parameters.

Finite nonconcentration defensive spells with modifier payloads register their spell identity in the existing source-owned timed-effect lifecycle. Source-turn-start expiration removes only the matching source/effect group, including its modifiers, and preserves other sources. Duration is derived from the spell or legal duration override; an opening cast expires after its allotted combat rounds. Concentration spells retain concentration-owned expiration, and explicit short modifier lifetimes remain authoritative. Every new match constructs fresh state.

## Encounter round context for nested saves (2026-09-30)

Temporary combat state owns `current_round` (initially null). Both engines set
it for every combatant at the start of each encounter round, before any turn
or reaction. Nested saving throws, including damage-triggered Concentration
checks, use an explicit round when supplied, otherwise this authoritative
state value. Finite D20 bonus dice still fail closed if neither context exists.
This preserves bonus-die expiry/consumption without guessing a round or dropping
a bonus. Fresh fight states reset the clock; immutable templates never own it.
Python: runtime schema, encounter/duel engines and saving_throw_rolls. Browser:
browser-state, browser-engine and browser-saving-throws. Existing shared
Concentration/damage and bonus-die resolvers remain the only resolution paths.


## Deferred save-effect activation variants

Deferred save effects remain one source-agnostic capability with immutable source parameters and fresh per-fight marks.

- A qualifying hit may arm one or more targets subject to the declared maximum and resource cost.
- Source data may permit an existing mark to end harmlessly when a different target is armed; re-hitting the already marked target never spends the arming resource again.
- Outcome data may express zero-HP replacement, success-only typed damage, or failed-save typed damage with optional half damage on success. Damage still routes through the shared typed-defense pipeline before HP mutation.
- The normal activation path may spend the combatant's Action.
- Source data may additionally permit activation by replacing one legal Attack-action slot. The Attack action is still spent once, the deferred effect consumes exactly one slot, and remaining legal slots continue normally.
- Arena candidate selection prefers the Attack-slot path over the full-Action path when both are legal because it preserves the source's remaining Attack-action slots. The full-Action path remains available when no Attack slot is legal.
- Python and browser use the same mark lifecycle, resource spending, save, damage, harmless-end, and activation-choice parameters.
- Source names remain audit/player-facing metadata. The deferred-effect runtime never branches on a class, subclass, hero, monster, or feature name.


## Universal friendly auras

Passive and timed ally auras share the same live-position synchronization layer.

### Saving-throw auras

- Passive flat-bonus auras declare source id/name, radius, flat bonus, and source-state deactivation rules.
- The runtime recomputes eligible same-side recipients from current grid positions whenever aura state is synchronized; recipients are never snapshotted.
- Overlapping flat-bonus auras use only the strongest eligible bonus.
- Source-specific lifecycle differences are parameters. For example, 2014 Aura of Protection is inactive while its source is unconscious, while 2024 Aura of Protection is inactive while its source is Incapacitated.
- Python and browser runtimes must consume the same declarative aura data. Ability names remain display/audit metadata and do not select resolver behavior.

### Condition-immunity auras

Passive friendly condition-immunity auras declare source id/name, live radius, one universal condition id, and source-state deactivation rules. The synchronization layer recomputes same-side recipients from current positions and installs the existing generic `condition-immunity` modifier; it does not create a feature-specific condition resolver.

- 2014 Aura of Devotion binds Charmed immunity and 2014 Aura of Courage binds Frightened immunity with the printed unconscious-only shutdown behavior.
- 2024 Aura of Devotion binds Charmed immunity inside its 10-foot Aura of Protection Emanation and is inactive while the source is Incapacitated.
- Leaving the radius or disabling the source removes the aura-owned modifier on the next synchronization; innate condition immunity remains untouched.
- Python and browser runtimes consume the same declarative grant. Source names are player/audit metadata only.


## Capped multi-target saving-throw actions

A source may declare a normal `SavingThrowAction` with `max_targets > 1`. The shared selector chooses up to that many legal hostile targets using the existing target order, range, sight, immunity, save, resource, and action-economy rules. Every selected target resolves an independent save, while the source Action and source resource are spent exactly once after all selected targets have been validated. The resolver is source-neutral; class, spell, feature, and monster names remain presentation/audit metadata only.

## Single-activity timed turn behavior

A timed effect may declare `turn_behavior="single_activity"`. On each affected turn, the first voluntary category actually used—movement, Action, or Bonus Action—becomes that turn's sole voluntary category. Choosing movement removes Action and Bonus Action availability; choosing an Action removes Bonus Action availability and voluntary movement; choosing a Bonus Action removes Action availability and voluntary movement. Reactions are not affected. Multiple attacks that belong to one Attack action remain inside the chosen Action, but an effect that grants an additional Action cannot bypass the single-Action limit. The claim resets at the start of each turn and disappears when the owning timed-effect group expires or is removed.

## Committed timed activities

A `DelayedResourceRefill` is a committed timed activity, not an end-of-turn auto-timer. The creature spends its Action to begin. Fresh per-fight state records the start and completion rounds. While that state exists, the shared suppression helpers block Action, Bonus Action, and voluntary movement; they do not block Reactions. End-of-turn resolution restores the declared resources only at the recorded completion round, and only if the creature is still able to perform the activity. Incapacitated or dead creatures stop without restore. The printed source name remains presentation and audit metadata; engine dispatch uses the declarative activity, not a class or feature-name branch.


## Finite healing pools and named condition removal

`HealingAction.healing_from_resource_pool` binds a fixed, single-target resource pool to the existing pooled-healing capacity calculation. Resolution makes a temporary action allocation of the lesser of current pool points and missing effective HP; resource cost equals that allocation. Immutable action data and resource maximum stay unchanged. Both 2014 and 2024 Lay On Hands bind this parameter with their own Action or Bonus Action cost.

Condition-removal requests validate distinct condition ids, source-specific restrictions, maximum count, actual requested affordability, action economy, and live footprint distance before spending anything. Arena priority selects a useful subset but never limits which affordable legal subset the resolver accepts. Removal ends the requested condition instances through the timed lifecycle, preserves other conditions from the same source group, and removes group-owned modifiers when no sibling remains. Heroes and monsters share the same selector, resolver, lifecycle, and fresh-state reset. Restoring Touch widens the existing Lay On Hands removal data; Arena AI selects removal without optional simultaneous HP healing.
