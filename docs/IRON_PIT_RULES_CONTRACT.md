# Iron Pit Rules Contract

Chris-locked product decisions are indexed in `docs/IRON_PIT_LOCKED_RULES.md`. This file remains the detailed combat/product contract those locks cite. Do not copy the index into a second spec.

This is the authoritative product/rules contract for Iron Pit. It describes the intended combat model. Repository code, generated certification manifests, and exact-head permanent tests prove implementation status; they do not override this contract by silently changing a rule.

If implementation and this contract disagree, either fix the implementation or make an explicit product decision to revise this file. Historical milestone documents and conversational progress claims are not authority.

## Arena-entry buff casting

When a canonical combatant can legally cast a non-Concentration buff before combat and that buff is selected as its deterministic opening preparation, Iron Pit may mark that specific opening cast as **free at arena entry**. A free opening cast still requires the spell to be legally prepared or known and the combatant to have access to a slot of the printed spell level, but it does not consume that spell slot. This is an explicit arena setup rule, not a change to the spell's RAW casting rules. Runtime data must opt into the rule declaratively; existing opening spells continue to consume slots unless so marked.

## Weapon category versus attack delivery (2024 Paladin)

A printed Melee weapon remains a Melee weapon when its Thrown property delivers a ranged attack. The 2024 Divine Smite trigger and Radiant Strikes qualify hits using a Melee weapon or an Unarmed Strike; they do not require melee attack delivery. Aurelia's Longsword and Javelin both qualify. Keep ranged geometry, Disadvantage, and other delivery-dependent rules unchanged. The shared damage primitives receive declarative eligible attack IDs and on-hit components; no weapon-name logic belongs in a resolver.

This supersedes the old operating-status exclusion of Javelin from 2024 Smite and the old no-rider Javelin assertion. 2014 Divine Smite retains its separate melee weapon **attack** trigger and is not widened by this 2024 source correction. Sources: [2024 spell descriptions](https://www.dndbeyond.com/sources/dnd/br-2024/spell-descriptions#DivineSmite), [2024 Paladin](https://www.dndbeyond.com/sources/dnd/br-2024/character-classes#Paladin), and [2024 weapon table](https://www.dndbeyond.com/sources/dnd/br-2024/equipment#Weapons).

## 1. Core architecture

- Iron Pit is a rules-first automated D&D combat simulator.
- Implement combat mechanics as universal capabilities, not hero-, class-, monster-, or stat-block-name special cases.
- Monster and pregen definitions are declarative data wherever practical.
- Unsupported outcome-changing mechanics fail closed. Never approximate, silently ignore, or invent a combat-relevant mechanic merely to make a card runnable.
- Python is the reference/certification oracle. The browser engine is the production fight engine. Supported capabilities require behavioral parity and permanent regression coverage.
- Noncombat-only rules may be omitted from runtime only when they cannot alter an Iron Pit combat outcome.

### 1.1 Mandatory semantic-mechanic reuse gate

This gate applies to **every** class feature, subclass feature, species feature, feat, spell, item, monster trait, monster action, reaction, legendary action, lair action, and future homebrew mechanic.

Before writing a new resolver or special handler, decompose the source ability into its actual combat semantics:

- trigger/timing window;
- action-economy cost;
- legal target/range/geometry;
- attack/check/save/recharge/resource requirement;
- damage/healing/state change;
- condition/buff/debuff;
- duration/expiry/repeat-save timing;
- resource/charge/use limit;
- interruption/reaction/override behavior.

Then search the existing universal capability inventory and current engine implementation.

**Required decision:**

1. If the behavior is mechanically equivalent to an existing primitive, **reuse that exact primitive**.
2. If the behavior differs only by numbers, damage type, DC formula, range, duration, target count, resource count, trigger, or ruleset-specific parameter, **reuse the primitive and parameterize the difference**.
3. If one named source ability is a combination of existing mechanics, **compose it from those existing primitives** rather than creating a monolithic source-specific resolver.
4. Only the genuinely unmatched semantic remainder may justify a new universal primitive.
5. A new primitive is not permitted merely because the source ability has a different name, comes from a different class, comes from a monster instead of a hero, or appears in a different edition.

Ability names are **presentation and audit metadata**. The original RAW/source ability name must appear accurately in logs, cards, and audit evidence, but engine dispatch must not depend on that display name when the behavior can be expressed through universal capability data.

A capability discovered while implementing a hero must be reusable by monsters, spells, items, and other heroes when their semantics match. A capability discovered while implementing a monster must likewise be reusable by pregens and other content.

**State/effect identity is universal.** Prone is Prone, Grappled is Grappled, Restrained is Restrained, Blinded is Blinded, Frightened is Frightened, Poisoned is Poisoned, and so on, regardless of which class feature, spell, weapon property, item, or monster ability caused it. Source definitions supply parameters such as DC, save ability, duration, repeat-save timing, range, damage, resource cost, and source ability name. The shared condition/effect engine supplies the mechanical behavior.

**Buff/debuff interaction is universal.** Harmful combat states and penalties are represented as debuffs or debuff semantics; protective effects are buffs that may counter named debuffs. The engine resolves the counter by semantic identity plus declared qualifiers such as magical/nonmagical source, duration, resource requirement, or movement cost. A source ability must not receive a bespoke immunity/removal branch when the same result can be expressed as a reusable buff counter. Conditional counters pay their declared cost automatically when Arena policy has no meaningful reason to decline it; for example, a 5-foot movement cost that automatically clears a nonmagical Grappled/Restrained debuff is paid at the first legal opportunity.

Invisibility is one universal condition regardless of source. A spell, feature, item, monster ability, or self-buff that grants invisibility applies the same `invisible` condition; source-specific activation cost, resource cost, duration, and companion effects belong to declarative source data rather than a source-specific invisibility resolver.

Effective visibility is one universal, distance-aware predicate. It consumes observer and target live state, the distance between them, source-derived `truesight_ft` / `blindsight_ft` through an effective-sense layer, Invisible / invisibility-suppression, and Blinded. 2014 and 2024 Truesight is visual: it sees Invisible creatures and objects inside its declared range and does not function while Blinded. 2014 and 2024 Blindsight perceives without relying on sight: it functions while Blinded and perceives Invisible creatures inside its declared range. Outside a sense's effective range, ordinary Invisible and Blinded rules apply. Live sense suppressors may reduce effective range without mutating the immutable source value; they bind declaratively rather than through named-creature dispatch.

The player-facing combat log must preserve the exact source ability name. Internal audit/certification data should additionally record the generic capability/primitive IDs used underneath so engine reuse remains provable without exposing implementation jargon to the player.

Before adding new mechanic code, the implementation audit must classify the feature as one of:

- `ENGINE_EXISTS_BINDING_MISSING`
- `ENGINE_EXISTS_PARAMETER_DELTA`
- `ENGINE_EXISTS_COMPOSITION`
- `ARENA_NEUTRAL`
- `ENGINE_TRULY_MISSING`

`ENGINE_TRULY_MISSING` requires evidence that the existing primitive inventory cannot represent the outcome correctly. After adding any new universal primitive, re-audit all classes and monsters for additional content that can now bind to it.


### 1.2 Universal combat resolution pipeline

All outcome-changing combat must follow the same conceptual pipeline:

`source/action data -> legality checks -> context checks -> active modifiers -> roll/save/attack -> result -> state mutation -> audit event`

This is a mandatory architecture rule, not only an implementation preference.

1. **Source/action data** declares what is being attempted: source identity, action cost, target, range, tags, damage, condition, save/attack facts, resource cost, duration, and other printed parameters.
2. **Legality checks** answer whether the attempt can occur at all: action economy, resource availability, target validity, range/geometry, required state, concentration, recharge, and ruleset restrictions.
3. **Context checks** inspect only universal facts needed by the mechanic: attacker/defender state, creature type, damage type, magical/nonmagical source, condition identity, movement mode, effect tags, battlefield/environment context, and similar typed facts.

**Battlefield/environment context.** An active source-owned effect may emit a typed environment fact such as `sunlight`. That fact is declarative source data, not a name check, and is not implied by bright light alone. Geometry follows the emitting effect's live emanation and expires with that effect. The standard Iron Pit arena is not sunlight. A creature that reacts to a context owns declarative reaction data; matching reactions apply through the normal Advantage/Disadvantage modifier stack. Example: 2014 Sunlight Sensitivity imposes Disadvantage on attack rolls and on Wisdom (Perception) checks that rely on sight while the creature is inside a live sunlight context.
4. **Active modifiers** alter the pending mechanic through universal semantics: Advantage/Disadvantage, flat modifiers, resistance/immunity/vulnerability, buff/debuff counters, condition immunity, targeting gates, damage reductions, replacement effects, and other reusable modifiers.
5. **Resolution** performs the canonical attack/check/save/damage/healing/movement/resource operation.
6. **Result** is an explicit mechanical outcome such as legal/illegal, hit/miss, save success/failure, damage amount, condition accepted/rejected, movement allowed/blocked, resource spent/rejected, or effect replaced.
7. **State mutation** applies only the accepted result to fresh combat state.
8. **Audit event** records the source name plus the checks/modifiers that materially changed the result.

Named abilities must feed this pipeline as data/composition. They must not bypass it with source-name conditionals when universal facts can express the same rule.

Examples:

- Nature's Ward: incoming `charmed`/ `frightened` -> check source creature type -> matching Fey/Elemental immunity modifier -> reject debuff.
- Poison immunity: incoming poison damage or `poisoned` debuff -> matching immunity check -> reject the relevant result.
- Freedom of Movement: incoming movement debuff -> matching debuff counter -> prevent it or automatically pay the declared movement cost to remove it at the first legal opportunity.
- Resistance: incoming typed damage -> damage-defense check -> modified damage result -> HP application.
- Attack roll: legal attack -> roll-mode modifiers -> d20 resolution -> hit/miss result -> damage/rider pipeline.

**Refactor rule:** when existing code contains a class-, subclass-, spell-, monster-, or feature-name branch, first ask whether it is only selecting one of these universal checks/modifiers/results. If yes, migrate the branch into declarative source data plus the existing shared resolver. Preserve behavior and Python/browser parity during migration.

**Migration priority:**

1. conditions, immunities, buffs, and debuff counters;
2. attack/check/save modifiers;
3. damage/healing defenses and replacement effects;
4. movement/position legality and counters;
5. resources, recharge, and action-economy legality;
6. timing hooks/reactions and other interrupts.

Do not rewrite already-correct universal code merely for stylistic consistency. Refactor only named/special-case logic that duplicates universal semantics or prevents shared reuse.

## 2. Ruleset isolation

The current certified public ruleset is D&D 2024 / SRD 5.2.1.

The target architecture supports hard ruleset profiles:

- 2014 fights use only 2014 monsters, pregens, spells, features, items, and mechanics.
- 2024 fights use only 2024 monsters, pregens, spells, features, items, and mechanics.
- Never cross editions in one fight.
- A same-named spell, feature, item, or monster is **not** evidence that its mechanics are edition-identical. 2024 content must bind to 2024 source parameters and effect wording; 2014 content must bind to 2014 source parameters and effect wording. Universal resolvers may be shared only after the edition-specific data has been compared semantically.
- Spell certification must compare outcome-changing spell fingerprints (including action cost, range/targeting, attack vs save, save ability, dice/scaling, damage/healing type, concentration, duration, conditions/modifiers, and upcast behavior) against the selected edition. A 2024 pregen fails closed if a spell fingerprint is missing, inherited from 2014 without proof, or conflicts with 2024 source wording.
- Shared mechanics live in one universal core; edition differences live in explicit ruleset profiles/data rather than duplicated whole engines.
- Certification is ruleset-specific.

Until the 2014 profile is implemented and certified, the public product remains 2024-only.

## 3. Immutable cards and combat instances

- A monster/pregen card is immutable source data.
- Starting a fight creates a fresh temporary combat instance for every participant.
- Combat may change the instance: HP, Temporary HP, conditions, equipment access, spell slots, resources, death saves, concentration, forms, positions, and other combat state.
- Combat never permanently changes the source card.
- When a fight ends, the entire combat instance is discarded.
- The next fight starts every card completely fresh with full HP and all card-defined resources/items/charges restored.
- Fictionally, the Iron Pit deity fully restores every combatant between fights, regardless of how long the required recovery would normally take.
- Mundane ammunition is unlimited. Special ammunition/consumables exist only when explicitly part of the immutable loadout and reset to the card quantity after the match.

### 3.1 Printed 24-hour / rest immunities

Pit matches end when one side wins. The combat instance is discarded. The next fight starts every card completely fresh.

Printed 24-hour immunities from a successful save against a source ability — including 2014 Frightful Presence and 2014 Draconic Presence — map to **match-scoped source immunity** in the Pit. The target is immune to that source's effect for the rest of the current fight only. Do not simulate calendar 24 hours as a 14400-round timer. Do not persist immunity across fights. Cards stay immutable; only temporary in-fight state exists.

On a failed Wisdom save, Frightful Presence still applies Frightened for the printed in-fight duration and repeat-save window. Preserve the printed ability name in the combat log.

`source_effect_immunity_on_success`, `source_effect_immunity_on_end`, and hostile-aura `success_immunity` compile to that same match-scoped immunity. A successful save, or the Frightened effect ending where printed, grants immunity to that source until the match ends. Nature's Sanctuary and similar targeting-ward 24-hour success immunities also last only for the current fight instance.

## 4. One combat engine, four execution modes

All modes consume the same canonical resolution path:

- **Step:** resolve/display the next already-generated event and pause.
- **Watch:** play the same event stream automatically to completion.
- **Replay:** reproduce a completed seeded fight exactly.
- **Turbo:** run the same canonical fight engine X times with presentation overhead suppressed.

UI mode must never change combat mechanics.

Turbo requirements:

- Each run starts from a fresh combat instance.
- Each run receives a reproducible seed.
- Store lightweight per-fight summaries/seeds rather than thousands of full rendered logs.
- A selected fight can be regenerated from its seed for Step/Watch/full-log review.
- Engine/rule errors are not wins, losses, or draws. Preserve the seed, exclude the run from the win-rate denominator, and continue the batch.
- Batch statistics include at least valid fights, engine errors, hero wins, monster wins, draws, rates, and fight length summary.

## 5. Audit-grade event log

The combat log is part of the rules engine's evidence trail, not decoration.

For every mechanically relevant event, preserve enough evidence to answer “why did this happen?” including where applicable:

- original dice and accepted dice;
- Advantage/Disadvantage sources;
- rerolls, die replacements, and roll-twice/choose provenance;
- modifiers and final totals;
- AC or DC checked;
- hit/miss/save result;
- critical-hit status;
- individual damage components and types;
- resistance, immunity, vulnerability, reduction, absorption, Temporary HP, and HP application in exact order;
- resource/slot/charge spending;
- conditions/buffs/debuffs applied or removed;
- concentration start/end/checks;
- repeat saves and timing;
- relevant range/movement/position facts;
- zero-HP/death/stabilization/life-state transitions;
- ability sequence and why an action/target/effect was legal or illegal.

The card shows current combat truth. The log shows how that state was reached.

Audit annotation is evidence-only and must never change combat resolution.

## 6. Timing and specific-beats-general

- Preserve exact source ordering of combat-relevant sentences and subeffects.
- Resolve one event/step completely and update state before resolving the next.
- Specific rules/feature wording override generic pipelines when RAW says they do.
- Use shared lifecycle/timing windows such as start/end of turn, hit, miss, take damage, deal damage, save success/failure, enter/leave area, source death, and round boundaries.
- Durations retain their source semantics even when the engine also derives a convenient round count.
- Mandatory triggers, reactions, interrupts, expirations, repeat saves, and legendary timing occur at their exact legal windows.
- Do not add generic repeat saves to effects that do not grant them.


### 6.1 Delayed-effect arena policy

- Preserve explicit RAW in-combat timing when a feature names a specific start/end-of-turn, round, reaction, or other legal trigger.
- When a combat effect is armed now but has **no required minimum delay** and is resolved by a later voluntary action or activation, Arena AI uses it at the **next legal activation opportunity** when doing so is tactically meaningful. In ordinary turn flow this will usually be the creature's next turn/round.
- A long printed duration is an **expiry window**, not an instruction for Arena AI to wait that long. An effect that can remain armed for minutes, hours, or days may still be activated on the next legal turn when RAW allows it.
- If a printed delay or required trigger is genuinely longer than a plausible Iron Pit fight, classify and re-evaluate the mechanic before certification. Do not silently wait out combat, silently fire it early, or ignore an outcome-changing delayed effect.
- Delayed mechanics must use fresh per-fight runtime state and reset completely between matches.

### 6.2 Committed timed activities

- A printed activity that requires the creature to spend a duration performing it is a committed timed activity, not a delayed callback that leaves the creature free to fight.
- Starting it spends the declared Action. While it is being performed, the creature cannot take unrelated Actions, Bonus Actions, or voluntary movement that would contradict spending that time on the activity.
- Reactions remain available unless the printed rule removes them.
- The printed 2024 Magical Cunning text is: “You can perform an esoteric rite for 1 minute. At the end of it, you regain expended Pact Magic spell slots but no more than a number equal to half your maximum (round up).” It does not list a damage interrupt, Concentration, or any other cancellation trigger. This contract does not invent one.
- Slots or other declared resources return only if the creature performs the activity for the full printed duration. If the creature is Incapacitated or dead, it is not performing the activity, so the activity ends without restore. Damage alone does not cancel it.
- Arena AI does not start a multi-round committed activity while the creature still has a printed damaging option. Damage-first. A 1-minute rite is not a substitute for a landable attack.

## 7. Initiative

Initiative is a Dexterity check. Normal initiative bonuses and ruleset-specific Initiative mechanics apply, including Advantage and Disadvantage on Initiative.

- A natural 20 on Initiative has no special ordering rule. The check total is the initiative count.
- A natural 1 on Initiative remains in the bottom-priority bucket as an Iron Pit house rule. This is separate from the combat house rule that a natural 1 on an attack roll ends that attacker's current turn.
- Natural 20/1 Initiative does not grant or remove actions, attacks, or rounds.
- Surprise is resolved separately according to the selected ruleset; it does not automatically move a creature to the bottom of Initiative.

Tie policy (deterministic simulator equivalent of RAW decision ownership):

- 2024 and 2014 RAW give decision ownership rather than a reroll: players decide PC/PC ties; the DM decides monster/monster ties and PC/monster ties.
- Iron Pit has no live player or DM during resolution, so both engines use this deterministic equivalent and never reroll Initiative to break a tie.
- Higher initiative count acts first. On an exact tied count inside the same priority bucket: PC/PC uses earlier party/roster order; monster/monster uses earlier encounter order; PC/monster lets heroes act before monsters, then uses the same-side encounter order.
- Identical monsters that share one RAW group roll are one initiative count, not a tie.
- First-round extra turns keep their offset initiative count in the normal priority bucket and resolve after any normal turn at that same count.

## 7.1 Opening buff on arena entry

- Before initiative is rolled, each combatant that has a legal available combat buff **must activate exactly one** as its opening buff. This is an Iron Pit pit rule, not a seeded starting condition and not a starting debuff.
- If the combatant knows or can legally activate more than one combat buff, it uses the **highest-level** one only. Non-spell abilities compete as level 0. Same-level ties use the existing declarative priority, then registration order. Do not apply every buff the combatant knows.
- This opening activation is a free action in the pit: it does not consume the combatant's Action, Bonus Action, or Reaction, and it does not spend the first-turn Action.
- The buff still pays every other printed cost and requirement that remains meaningful in Iron Pit, including spell slots, charges, class resources, target/range legality, and Concentration.
- **Explicit Foresight arena exception:** when a Druid of level 17+ selects **Foresight** as its one opening buff, the precombat cast does **not** expend the level-9 spell slot. This is an Iron Pit arena override recorded here, not a change to 2024 RAW. The spell otherwise keeps its legal target, duration, and effect semantics. Other opening-buff spells continue to pay their printed spell-slot/resource costs unless this contract records another explicit exception.
- A combatant receives only one opening-buff activation per fight. A spell, class feature, subclass feature, species feature, item effect, or other source competes for that same single opening-buff opportunity when it is otherwise legal.
- The opening buff resolves in the precombat phase before initiative. Its normal duration/lifecycle begins there; source-turn timing continues normally once round 1 starts. An effect that lasts until the end of the source's next turn therefore expires at the end of that combatant's first turn.
- Opening-buff selection is universal Arena policy. Do not create class-, spell-, or source-name exceptions in resolver logic; explicit arena overrides recorded in this contract must be represented as declarative source parameters consumed by the shared precombat pipeline. The source ability supplies its exact player-facing name and parameters; the shared precombat buff pipeline supplies the activation.
- Production presets and player-loaded fights start with no debuffs. A test harness may seed a buff or debuff so a combination can be asserted. The opening-buff pit rule is not that harness.
- Buffs that require a separate combat entity, an unavailable target, an unsupported outcome-changing mechanic, or another illegal precondition remain unavailable and do not bypass normal certification gates.

## 8. Action economy

- Use the selected edition's RAW Action, Bonus Action, Reaction, movement, Extra Attack, Multiattack, and other action-economy rules.
- Extra Attack is multiple attacks inside the Attack action, not an extra Action.
- Multiattack uses exactly the printed number/types/options/sequence.
- Flexible Attack/Multiattack choices are narrowed by the current-row policy in §10 before landing-damage comparisons. Fixed printed slots remain fixed. Preview scoring and actual resolution must use the same narrowed choices.
- Bonus Actions exist only when a rule grants one.
- Reactions refresh according to RAW.
- Conditions suppress actions/reactions according to RAW.
- Once-per-turn, once-per-round, and once-on-each-of-your-turns are distinct limits.
- Dash/Disengage/Hide/Ready/Help/Search are not generic tactical spam; use them only when a supported combat identity or legal fallback requires them.
- After healing/support and signature Actions, heroes and monsters use the same landing-damage Action policy.
- Damage-first: compare every damaging option that can actually land this turn (a melee Attack/Multiattack, a damage spell, a damaging save or area Action) and take the one that deals the most printed damage. Multiattack printed damage includes every landable slot (weapon attacks and save actions), so a Bite-plus-Constrict Multiattack beats Constrict used alone. A recharge line/cone/area Action that can land from the current square is not kiting; it competes on damage even when melee can also reach.
- Melee when in reach: if a legal melee weapon or natural attack can land this turn, including after useful legal approach movement, do not spend the Action on a ranged weapon attack. Stay in the ring. Equal printed damage prefers the melee option.
- Among legal damage spells, cast the highest-level damage spell first, then work downward. Most damage still wins when comparing a spell to another landable option.
- Prefer raw damage that is easy to calculate over charm and other control. Control remains legal only when no damaging option can land.
- Dodge is the default when no supported offensive option can be used or made legal after any useful legal approach movement available this turn. Dodge is an ordinary combat outcome, not a skip and not a crash.
- A legal tactical dead end may resolve to Dodge. Unsupported mechanics, malformed state, impossible source data, mixed position authority, and engine/rules errors must fail closed and must never be converted into Dodge.

### Attack natural 1 — Iron Pit house rule

A natural 1 on an attack roll:

1. is an automatic miss;
2. immediately terminates that creature's current turn;
3. loses all remaining attacks, Bonus Action, and other voluntary turn actions;
4. does not undo anything already resolved earlier in the turn.

Turn termination must be a universal combat-state/control primitive consumed by Extra Attack, Multiattack, Light/Nick attacks, Action Surge follow-ups, spell follow-ups, and all other voluntary turn actions.

A flavor-only d6 may narrate the fumble; it has no additional mechanical effect.

### Attack natural 20

- Use the selected edition's RAW automatic-hit/critical behavior.
- Critical hits and automatic hits use the kept/selected natural die after Advantage or Disadvantage. A discarded 20 is never a critical or automatic hit.
- A flavor-only d6 may narrate the critical; it has no additional mechanical effect.
- Saving throw natural 1/20 values have no extra Iron Pit rule unless RAW for the specific rule says otherwise.

### Turn-start buff versus debuff

At the start of each creature's turn, the engine reads that creature's live debuffs before it acts. A legal matching buff answers the debuff:

- Bloodied (current HP at or below half of maximum) is answered by healing.
- Charmed or Frightened is answered by a condition-immunity or debuff-counter buff for that same condition.
- An already-active matching counter-buff suppresses the current condition and causes a new copy of that debuff to fail closed. It does not land.

Arena AI selects the answering buff only when the matching debuff is present on a legal friend. A printed suppression that would do nothing is not selected. Pairing is by condition identity and modifier kind, never by spell name, monster name, or class name.

A test harness may start a buff or debuff so a combination can be asserted. Purpose-built production fights and any matchup a player loads must not begin with a debuff. Seeded fear for Calm Emotions lives only in the engine test, never on the website legendary preset.

### Calm Emotions

2014 Calm Emotions binds the printed charm/frighten suppression option through the shared condition-immunity and debuff-counter primitives. Allies may choose to fail the save to receive that beneficial suppression. The printed indifference option is not a supported targeting-gate primitive. Do not apply Charmed or invent a hostility shutdown to fake the missing option.

## 9. Advantage and Disadvantage

- Track every source independently for audit and expiry.
- Any Advantage source + any Disadvantage source = normal roll, regardless of how many sources exist on either side.
- Only Advantage sources = Advantage.
- Only Disadvantage sources = Disadvantage.
- Removing one source must recompute from the remaining active sources.

## 10. Arena and movement

The standard Iron Pit is one persistent tactical battlefield. It is intentionally compact enough to prevent kiting/fleeing gameplay while preserving actual movement, creature size, reach, range, and area geometry.

Standard battlefield:

- 24 × 16 squares;
- each square is 5 ft × 5 ft;
- physical dimensions are 120 ft × 80 ft;
- heroes deploy in `x = 0..7, y = 2..13`, facing the center from the east edge of that zone;
- monsters deploy in `x = 16..23, y = 2..13`, facing the center from the west edge of that zone;
- `x = 8..15` is the central open Pit lane.

Permanent arena rules:

- Each combatant has one authoritative `x,y` grid position. Movement, reach, range, Opportunity Attacks, forced movement, and area geometry consume that same state.
- Printed creature size determines occupied footprint: Tiny/Small/Medium = 1×1, Large = 2×2, Huge = 3×3, Gargantuan = 4×4.
- The moving battlefield representation is the combatant's card/art presentation rendered inside that footprint; presentation never determines mechanics.
- Voluntary movement uses actual effective Speed and legal movement cost. The Pit deity no longer grants free ordinary closing or hidden movement distance.
- Default Arena AI does not voluntarily flee, kite, circle, run to map edges, seek cover, or reposition without an action-driven reason. If a supported offensive action is not yet reachable this turn but the pathfinder proves a legal eventual route to a usable position, the combatant advances as far as useful movement permits along that route. It does not stay still merely because it cannot attack this turn.
- A combatant may pass through creature spaces only when the selected ruleset permits it, pays any required Difficult Terrain cost, and may not willingly end normal movement overlapping another creature.
- Printed Walk, Fly, Climb, Swim, Burrow, Hover, and base-speed data remain source-derived and must not be rewritten merely to make a creature usable in the Pit.
- Movement modes never become roster-eligibility filters. The magical Pit remains hospitable to aquatic, flying, burrowing, climbing, unusual-biology, breathing, and atmosphere requirements. Every combatant may use its printed movement modes and make attacks as though the Pit were a valid native environment for those modes and its normal biology. Environmental hospitality removes habitat-only penalties such as underwater movement or attack penalties; it does not grant extra Speed, a movement mode the source does not have, free movement, altitude-based immunity, or protection from RAW combat effects that explicitly create Difficult Terrain, Speed penalties, conditions, or other debuffs.
- **Environmental viability is not environmental presence.** The standard Pit contains no water terrain/context. Aquatic creatures may still breathe, use printed Swim Speed, move, attack, and fight normally because the Pit magically supports their biology. That support does not count as being underwater and does not activate traits, actions, or bonuses that require actual water/underwater terrain, such as Underwater Camouflage, unless a supported combat effect explicitly creates a matching water context.
- The standard Pit also has no rocky-terrain context. Terrain-only traits such as Stone Camouflage remain inactive when their required terrain is absent. More generally, a terrain/environment-only trait is arena-neutral when its required context is absent and no supported combat effect creates that context.
- Flying movement remains horizontal-only in the standard Iron Pit. Flyers may use their printed Fly Speed across the battlefield but may not gain altitude to become permanently unreachable.
- Front row is melee. Back row is ranged and/or casters. Mixed melee-and-ranged cards on one side split: one starts in front as melee, extras start in back as ranged. **Attack/Multiattack choice policy is deterministic by row at Action selection, with that mode fixed for the Action:** when a printed attack slot offers both melee and ranged alternatives, a front-row combatant selects the melee alternative; a back-row combatant selects the ranged alternative while at least one living ally remains in the front row; when no living allied front-row combatant remains, that back-row combatant switches its flexible attack choices to melee and steps forward through the normal formation/movement policy. A fixed printed slot that offers only one attack kind remains that printed attack; row policy never invents or substitutes an attack not allowed by the source Multiattack. Front-row combatants do not randomly split later Multiattack slots into ranged shots. Creature names never assign rows.
- Starting placement is deterministic and footprint-aware. Future manual legal placement is authoritative when explicitly selected by the user.
- No environmental cover by default.
- Clear line of sight by default; only combat effects such as Darkness, Fog Cloud, Blindness, Invisibility, or similar supported mechanics alter visibility.
- No default pits, lava, traps, difficult terrain, water, or random arena hazards. A supported RAW effect may create an area/hazard.
- Flyers cannot use altitude to become permanently unreachable. A melee flyer must enter its legal reach to attack.
- Opportunity Attacks, forced movement, Disengage consequences, speed changes, Grappled/Prone movement effects, Frightened movement restrictions, and other combat-relevant movement rules remain RAW where applicable.

### 10.1 Iron Pit engagement, flying, and in-place teleport (2026-10-04)

The standard Iron Pit is a brutal ring. Monsters and pregens close and stay in melee. People come to watch carnage, not cowards. These are explicit arena overrides, not RAW changes outside the Pit.

- Voluntary movement planned relative to an opponent the combatant is already in melee reach of cannot increase that distance. The default engagement distance is 5 feet. Leaving one foe only to close on another remains legal and still provokes Opportunity Attacks. Forced movement may push a combatant out of melee.
- Flying, running, Dash, Disengage, circling, and leave-reach movement do not create a kiting exception. Arena AI and other voluntary planners cannot open distance from the engaged opponent. A flyer cannot leave melee and stay gone.
- Horizontal fly remains fly. There is no vertical flight, altitude band, or unreachable-by-height state.
- Flying is only a buff that counters **ground-contact** debuffs. Thorns, Entangle plants, temporary Difficult Terrain, and similar ground snares do not affect a combatant while it has an effective Fly speed. Flying grants no other combat benefit and does not change rows to escape.
- This overrides leave-reach Flyby behavior: an opportunity-attack exemption, if present, does not authorize leaving the engagement.
- Teleport, plane shift, and summoning remain banned as position-changing or entity-creating options.
- A teleport-class action such as Misty Step, Dimension Door, or Teleport may clear matching movement-impairment debuffs a teleport would cancel, including Grappled, Restrained, and other effects marked `ends_on_teleport` or applied as a ground snare. The combatant does not change its authoritative grid position.
- The teleport resolver itself must refuse grid relocation even when a non-origin destination is supplied. Arena AI preference for in-place destinations is not sufficient. These effects do not bounce around the Pit, pass through walls, or change x/y.
- The combat lens for every effect remains: a buff cancels the matching debuff. Do not add an escape ability merely because it could negate a state. If the matching buff is already present, the incoming debuff does not land. Debuffs are checked at the start of each creature's turn before it acts.
- Nothing a player can load starts with a debuff. A test harness may seed a buff or debuff to prove a combination; that seed must never ship.

Engine dispatch uses movement-mode, `ground_contact`, and `ends_on_teleport` facts. Printed names such as Fly, Flyby, Entangle, Thorns, and Misty Step remain card, log, and audit labels only.
- If the pathfinder proves a legal eventual route toward a supported offensive position, the combatant may spend this turn making useful progress even when it cannot reach attack range yet; after moving, if no supported offense is legal and its Action remains, it Dodges. If no such eventual legal route exists, or no useful legal progress can be made, it stays put and uses the same Dodge fallback after the other supported offensive families are exhausted.

### AoE/targeting arena simplification

- Offensive team AoE is ally-safe in the standard Iron Pit: affect valid opposing-team targets only.
- This does **not** convert every AoE into “all enemies.” Preserve printed radius/shape/range/target counts over actual occupied squares.
- Lines, cones, radii, emanations, and other supported shapes resolve from authoritative grid positions/footprints rather than fixed target counts.
- Selected-target buffs/heals preserve their printed target counts.
- Large areas may hit the whole opposing team only when their actual geometry covers it.

## 11. Damage pipeline

Resolve each damage component separately and preserve source qualifiers.

### Runtime damage-roll invariant

- When RAW/source damage is expressed with dice, actual combat resolution rolls those printed dice at runtime through the canonical dice provider. Do not substitute averages, expected values, static approximations, or precomputed damage for the resolved fight.
- Critical hits add the additional damage dice required by the selected ruleset/source; they do not replace rolled damage with an average.
- Rolled bonus damage and on-hit riders (for example Sneak Attack, Divine Smite, Frenzy, and equivalent universal riders) use the same runtime dice path when their source damage is expressed as dice.
- Expected/average damage may be used only by Arena AI to rank otherwise legal tactical choices. AI valuation never becomes the damage applied to combat state or the audit log.
- Genuinely fixed-damage rules remain fixed and do not fabricate dice. A source that says it deals a fixed amount must resolve that fixed amount, including any source-defined success/failure split.


Universal dimensions include:

- damage type;
- magical/nonmagical or other source qualifiers when relevant, including silvered and adamantine;
- weapon/spell/melee/ranged qualifiers;
- resistance, immunity, vulnerability;
- flat/rolled reductions;
- absorption/ward pools;
- Temporary HP;
- current HP;
- zero-HP/lethal consequences.

Never invent one global ordering when a specific feature defines a different order. Specific wording wins.

The log must show the complete application chain rather than only final HP lost.

## 12. Temporary HP and absorption pools

Temporary HP:

- is a dedicated `temp_hp` combat-state pool, not healing and not a generic stat buff;
- visually appears as a positive card effect while active;
- follows the selected edition's exact replacement/retention rule and normally does not stack;
- absorbs incoming damage before current HP when RAW says so;
- does not increase current HP;
- is not restored by healing;
- does not wake/revive a pregen at 0 HP;
- expires according to its source and resets after the fight.

Wards/barriers/Arcane-Ward-style mechanics are separate universal absorption pools, not Temporary HP. Each follows its own RAW interaction/order and remains visibly attached to the card while active.

## 13. HP, death, and combat life states

Pregens/PCs:

- use RAW player-character zero-HP and Death Saving Throw rules for the selected edition;
- massive-damage instant death applies;
- damage at 0, stabilization, natural-1/natural-20 death-save consequences, and legal healing apply normally.

Monsters:

- die at 0 HP by default;
- specific printed prevention/recovery/persistence mechanics override generic death when RAW requires it.

Universal life-state model must distinguish states needed by mechanics, including at least:

- ALIVE
- UNCONSCIOUS
- STABLE
- DEAD
- DISINTEGRATED
- PETRIFIED
- other temporary removal/form states when required.

Specific 0-HP replacement/prevention/lethal rules are checked before the generic death/death-save path.

Dead is a terminal fight debuff. Once a combatant is Dead, they are out of that deathmatch: no resurrection, rebirth, revive, return, ordinary healing, later stabilization, regeneration, or Death Saving Throw restores them. Death Saving Throws occur only while a character is Unconscious/dying at 0 HP and not Dead. Printed 0-HP replacements (Death Ward, Undead Fortitude, Relentless Endurance, poison riders that stabilize instead of death) intercept the drop to 0 in the same resolution and never leave the combatant Dead first. No current roster ability is a true instant self-resurrection; do not invent a revive path. Logs and UI keep Dead as Dead for the rest of the match. The Pit deity restores combatants only after combat.

### Disintegration

A source that says reaching 0 causes disintegration must intercept generic PC death saves first:

- set the combatant to DISINTEGRATED;
- no Death Saving Throws;
- ordinary healing cannot target/restore the combatant;
- remove it from normal active target pools;
- preserve the exact lethal source in the log.

### Petrification

Staged petrification effects use a universal progression/state machine with the exact source saves, stages, timing, and immunities. **Iron Pit arena override:** once the Petrified condition is successfully applied, the affected combatant is immediately Dead for the rest of the match. This consequence belongs to the universal condition engine, not to Cockatrice, Gorgon, Basilisk, or any other named source.

## 14. Conditions and effect lifecycle

Combat-relevant conditions are universal rules, not source-specific implementations. Sources apply/remove/configure them.

Support all selected-edition combat-relevant conditions as needed, including Blinded, Charmed, Deafened, Frightened, Grappled, Incapacitated, Invisible, Paralyzed, Petrified, Poisoned, Prone, Restrained, Stunned, Unconscious, and edition-appropriate additional conditions.

- Track multiple sources where source duration/removal matters.
- Do not multiply the mechanical severity of the same condition merely because multiple sources apply it unless RAW says so.
- Use exact source duration and repeat-save timing.
- Do not invent a default DC or default recovery save.
- Buffs/debuffs/conditions remain visibly attached to cards while active.

### 14.1 Parameterized Slow / Weaken riders

`slowed` and `weakened-strength` are timed rider identities, not `ConditionName` values. Bind each source from its own printed 2014 SRD stat block. Do not copy one Slow bundle onto every similarly named action.

- **2014 Copper Slowing Breath** (wyrmling, young, adult, and ancient; Constitution save; printed cone and DC): the target cannot use reactions, its speed is halved, it cannot make more than one attack on its turn, and it can use an Action or a Bonus Action on its turn but not both. Duration is 1 minute. Repeat the Constitution save at the end of each of its turns.
- **2014 Stone Golem Slow** (Wisdom DC 17; creatures the golem can see within 10 feet): the same combat-economy limits as Copper Slowing Breath. Duration is 1 minute. Repeat the Wisdom save at the end of each of its turns. The printed golem action does **not** apply a −2 penalty to AC or Dexterity saving throws.
- **2014 Gold Weakening Breath** (wyrmling, young, adult, and ancient; Strength save; printed cone and DC): Disadvantage on Strength-based attack rolls, Strength checks, and Strength saving throws only. Duration is 1 minute. Repeat the Strength save at the end of each of its turns. No speed, reaction, attack-cap, or Action/Bonus Action limits.
- The 2014 *Slow* spell’s −2 AC and −2 Dexterity saving-throw penalties apply only when a source prints those penalties. Optional `armor_class_bonus` / `saving_throw_flat_bonuses` exist for that case and stay off Copper, Gold, and Stone Golem.

## 15. Concentration

Use selected-edition RAW:

- one concentration effect at a time unless a specific rule overrides;
- starting another concentration effect ends the previous one;
- damage triggers concentration checks using exact edition rules;
- separate damage events create separate checks where RAW requires;
- Incapacitated/death ends concentration;
- dependent effects end immediately;
- audit the damage, DC, roll, modifiers, result, and cleanup.

## 16. Resources, recharge, and resets

During a fight, all usage limits use exact source timing:

- Recharge 5–6 / Recharge 6;
- once per turn/round;
- X/day;
- spell slots;
- class resources;
- charges;
- limited-use monster actions;
- other printed use limits.

Universal Recharge lifecycle:

- A Recharge resource begins the fight available unless its source explicitly says otherwise.
- While the resource is available, no recharge roll is made; it remains available until actually expended.
- Using the associated ability expends the resource according to that ability's normal action/timing rules.
- Once expended, roll the printed recharge die at the start of each later turn of the source while the resource remains unavailable.
- A successful printed threshold restores availability; a failed recharge roll leaves the resource expended.
- Successful recharge only restores the resource. It does not grant an extra Action, repeat the ability automatically, or permit a duplicate use beyond normal action/timing restrictions.
- An ability used on a turn cannot recharge again until a later start-of-turn recharge window.
- Recharge trigger/timing/die/threshold and the action/effect bound to the resource are declarative source data feeding one universal Recharge lifecycle.

AI may use limited/signature resources aggressively because there is no future encounter to conserve for, but it must not knowingly waste them on an illegal/meaningless target.

All resources return to their immutable-card maximum/default after the match.

## 17. Multiattack and repeated attacks

- Resolve each individual attack fully before the next attack.
- Update HP, concentration, conditions, death/life state, target legality, and threat between attacks.
- Retarget between attacks when the printed action permits it.
- Preserve printed number/types/required sequence/options.
- A downed target remains RAW-targetable when applicable.
- A dead/disintegrated/otherwise invalid target is removed from normal target choice.
- Iron Pit natural-1 turn termination cancels all remaining attacks/actions immediately.

## 18. Reactions and interrupts

Reactions use exact trigger windows and costs. Reaction handling must support universal interrupt semantics so rules such as AC changes, attack redirection, movement reactions, Counterspell/Shield-style effects, and future monster reactions can alter the triggering event at the correct point rather than after the fact.

## 19. Boss mechanics

- Legendary Resistance is universal RAW resource/override behavior.
- Legendary Actions are universal RAW timing/cost behavior.
- Mythic/phase transitions should be data-driven universal triggers/actions when possible.

Iron Pit lair-action ownership house rule:

1. identify creatures with lair actions;
2. highest CR owns the lair actions;
3. if highest CR ties, highest initiative owns them;
4. if the owner dies/is permanently removed, lair actions disappear for the rest of that combat;
5. ownership never transfers mid-fight;
6. once selected, the lair action's actual mechanics/timing remain RAW.

## 20. Summons, forms, splitting, and temporary removal

**Summoning is currently disabled in Iron Pit.** A spell, feature, item, or monster ability that summons, conjures, creates, or calls a separate combat creature/entity is arena-unavailable for now and does not block certification when the rest of the source is fully supported.

- Do not create summoned combatants, companion bodies, summoned guardians, or a Summoning Annex.
- A source with a summon option keeps the exact RAW name and audit record, but Arena AI never selects that option.
- When a canonical caster may legally prepare a different non-summoning combat spell instead, prefer that legal replacement for the Iron Pit combat loadout while retaining mandatory always-prepared summon spells in source metadata as arena-unavailable.
- Transformations/Wild Shape/Polymorph are replacement forms, not summons, and remain separately governed by their own support status.
- Split/spawn mechanics printed on an existing creature are not automatically classified as summons; they require their own explicit audit.
- Swallow/engulf/banishment/ethereal/possession and similar mechanics use universal location/control/life-state structures rather than creature-name branches.

### 20.1 2024 Troll Loathsome Limbs arena abstraction

2024 RAW Loathsome Limbs normally creates separate Troll Limb creatures. Iron Pit does not create dynamic limb combatants for this feature. Instead, the source behavior is represented by a source-owned stack on the Troll:

- At the end of **any creature's turn**, if the Troll is Bloodied and took **15 or more Slashing damage during that just-ended turn**, it gains one **Loathsome Limbs** stack, subject to the printed **4/Day** limit and a maximum of four active stacks.
- Each active stack gives the Troll **1 Exhaustion level**, preserving the printed missing-limb penalty.
- Immediately after the Troll's turn, each active stack makes one attached limb attack using the source Troll Limb Rend profile: **+6 to hit, reach 5 ft., 2d4 + 4 Slashing**.
- These attached attacks use the normal universal attack resolver. They do not create separate initiative entries, positions, Hit Point pools, movement, targeting bodies, or spawned combatants.
- The Troll's ordinary Multiattack remains three Rends. The attached attacks are additional post-turn attacks representing the severed limbs.
- Troll **Regeneration remains otherwise source-correct**: 15 HP at the start of its turn; Acid or Fire damage suppresses it on the next turn; the Troll dies at 0 HP only when it starts its turn unable to regenerate.
- When Regeneration actually restores Hit Points, all active Loathsome Limbs stacks and only the Exhaustion levels owned by those stacks are removed. Unrelated Exhaustion is preserved.
- This representation is an explicit Iron Pit arena abstraction of the RAW spawned-creature mechanic; it is not a claim that RAW treats severed limbs as buffs.

## 21. Combat AI: legality first

Separate RAW legality from tactical policy.

- AI never gains hidden metagame knowledge of enemy AC/saves/resistances unless revealed/obvious/known through supported rules.
- During a fight, revealed resistance/immunity/vulnerability may be remembered; that knowledge resets after the match.
- Melee/frontline constraints are enforced before threat heuristics.
- Ranged/spell attackers may target any legal visible/ranged enemy subject to arena effects.
- Prefer strongest useful legal source-defined attacks/signature abilities without a deep hidden-stat expected-value solver.
- Avoid obviously wasteful attacks once an immunity is known when alternatives exist.
- Signature monster abilities should actually be used when legal/useful.
- Bloodied is an AI label at <=50% effective maximum HP, not a fake RAW condition unless a source rule uses Bloodied mechanically.

### Healing policy

- 0 HP healable ally: highest priority.
- 1–25%: strong healing priority.
- 26–50%: heal when worthwhile.
- >50%: normally offense.
- Dead/disintegrated/non-healable targets are excluded.
- If nobody needs legal healing, use offense/another meaningful action.
- Avoid obvious overhealing.

### Threat model

Threat influences target choice only after RAW legality/formation constraints:

- damage dealt: +1× damage threat;
- healing: +0.5× healing threat;
- measurable protection/prevention/redirection: +2× prevented impact;
- taking damage itself adds no threat;
- decisive kills/removal may add a meaningful temporary spike;
- do not add separate generic threat values for every control condition.

End-of-full-round decay tuning:

- non-healers: threat ×0.75;
- healers: threat ×0.50.

Threat ties: current engaged target -> Bloodied -> lowest HP percentage -> d20 reroll if still tied. Threat resets after the match.

## 22. Spellcasting AI

Before initiative, each combatant may receive exactly one proactive defensive/buff activation as an Iron Pit setup action:

- only the action-economy cost is waived;
- spell slot/resource/charge, concentration, duration, target legality/range still apply;
- passive effects do not consume the setup activation;
- avoid redundant nonstacking team buffs;
- each ally still owns its own setup activation.

Normal spell AI:

- use only spells actually known/prepared/provided by the source/build;
- no free matchup-specific spell invention;
- legal upcasting is allowed when the spell is actually known/prepared/provided, the higher-level slot exists, and the source spell defines scaling at higher slot levels;
- an upcast consumes the higher-level slot and must use the source-defined scaling exactly; never invent non-RAW scaling or matchup-only spells;
- when a newly unlocked spell level has no better meaningful combat choice, the AI may prefer a legal upcast of an established damage or healing spell rather than forcing a weaker native-level option;
- among legal damage spells, cast the highest-level damage spell first, then work downward, then cantrips when leveled offense is exhausted;
- most damage still wins when the Action choice is between a spell and another landable option;
- prefer raw damage that is easy to calculate (Magic Missile, Disintegrate, Finger of Death, Hunter's Mark, Ensnaring Strike) over charm and other control;
- damage spells remain legal in the Iron Pit; do not disable them;
- do not pre-cast a spell when a legal melee attack can land this turn after useful legal approach movement;
- one enemy: prefer useful high-damage single-target options before AoE;
- multiple enemies: prefer useful high-damage AoE before single-target options;
- selected-target spell counts and source geometry remain authoritative.

Iron Pit environmental limits, and only these, change RAW fight options: no teleport movement, no plane shift, no summoning/creating a separate combat entity, and no flying vertically. A teleport-class action may still clear teleport-cancelable debuffs in place under section 10.1. A character or monster still fights with every other printed option the engine supports.

### 2014 Turn Undead arena mapping

For the 2014 ruleset, Iron Pit preserves Turn Undead's failed-save removal-from-effective-combat intent without forced flee-path movement inside the arena grid.

- A failed 2014 Turn Undead save applies the source-bound `trembling` effect.
- While Trembling persists, the target cannot take an Action, Bonus Action, or Reaction and cannot move voluntarily.
- The target uses its normal behavior profile once the effect ends; Iron Pit does not force retreat movement for this 2014 arena mapping.
- Trembling ends immediately when the affected creature takes damage.
- At the end of each affected creature's turn, it repeats the Wisdom saving throw against the original Cleric save DC; a success ends Trembling.
- Destroy Undead still resolves before control is applied: an eligible Undead that fails the save is destroyed instead of receiving Trembling.
- This mapping is an explicit Iron Pit arena rule for 2014 Turn Undead and must use the shared timed/source-bound control lifecycle rather than Cleric-specific turn-state code.

## 23. Weapons, loadouts, and masteries

Weapon properties, masteries, fighting styles, feats, and two-weapon rules are universal selected-edition mechanics.

- Loadout/build data chooses weapons/style; the engine reads the shared weapon catalog.
- Never implement `ClassNameMastery()`/`MonsterNameWeaponRule()` when a universal property/mastery can express it.
- Dual wield/off-hand/Nick/Vex/Graze/Cleave/Push/Topple/Sap/Slow and similar properties use exact edition rules when supported.
- Equipment removal/destruction/suppression during combat immediately changes derived stats/access as RAW requires and is visible on the card.
- Temporary equipment state resets after the match.
- Printed monster defenses that apply only to nonmagical attacks, including silvered and adamantine bypasses, stay on the card. Iron Pit does not strip those defenses to make fights easier. They bind to the shared `ConditionalDamageDefense` primitive with `DamageSourceQualifier` values `magical`, `silvered`, and `adamantine`.
- Canonical pregen manufactured weapons use a **fixed level ladder**, never a random hoard d100. The bands match **2014 DMG Treasure Hoard** CR 0–4 / 5–10 / 11–16 / 17+ (p.137–138), which are the same character-level tiers. **Levels 1–4:** PHB silvered weapon (special material cost, not a magic-item table). Qualifier `silvered` only; +0 to hit and damage. Table F can appear on a 0–4 hoard at 86–97, but that is not the scheduled 1–4 loadout. **Levels 5–10:** Magic Item **Table F Weapon +1** (p.146): +1 to attack and damage rolls, `magical`. **Levels 11–16:** **Table G Weapon +2** (p.147): +2 / +2, `magical`. **Levels 17–20:** **Table H Weapon +3** (p.148): +3 / +3, `magical`. A Weapon +N is not silvered and not adamantine. Adamantine Armor appears on Tables F/G/H; core DMG/SRD does not print a separate adamantine weapon +N, so pregens do not invent one. Same pregen level always gets the same gear. Weapon dice stay the mundane catalog dice. Magical Weapon +N attacks bypass printed “from nonmagical attacks” clauses, including silvered and adamantine variants, because those clauses forbid magical sources. Unarmed Strikes are not manufactured magic weapons and keep only class-feature qualifiers such as Ki-Empowered Strikes.

## 24. Canonical pregens

- Maintain one persistent named canonical hero per core class.
- Each class progresses level 1–20 through one legal canonical build; a level derives from the previous certified level plus that level's audited combat delta.
- **Pregen edition sequencing is global, not per-class:** complete and certify all 12 canonical 2014 classes through levels 1–20 before beginning the 2024 pregen migration pass.
- The 2014 target is therefore **240/240 certified level-slots (12 classes × 20 levels)**, followed by a full 2014 pregen and universal-engine re-audit before 2024 pregen expansion resumes.
- After 2014 is complete, derive the 2024 pregens from the certified 2014 mechanic inventory: reuse every mechanically equivalent universal capability and implement only genuine 2024 semantic deltas, ruleset data changes, scaling changes, availability changes, naming changes, or resource differences.
- Do not alternate 2014 and 2024 class construction while the 2014 canonical set is incomplete. Existing 2024 certified work is preserved but is not the active expansion lane until the 2014 240/240 gate is satisfied.
- Only certified levels are publicly runnable.
- Combat-relevant class/subclass/species/feat/equipment/spell/resource mechanics must be implemented or remain explicit blockers.
- Noncombat-only choices do not require engine logic.
- Canonical hero construction details live in `CANONICAL_COMBAT_BUILD_POLICY.md`.

## 25. Monsters

### 25.1 Mandatory 2014-first monster sequencing

Iron Pit completes the **2014 source monster roster first**.

For every 2014 monster mechanic:

1. identify the semantic mechanic;
2. bind or implement it in the universal engine once;
3. certify the 2014 source/card against that primitive;
4. immediately audit matching 2024 source content for reuse;
5. carry the same primitive forward when semantics match;
6. add 2024-specific behavior only for a documented rules difference.

The source/card owns parameters. The engine owns mechanics.

Therefore:
- `Regeneration 10`, `Regeneration 15`, and `Regeneration 20` are the same mechanic with different card data;
- Acid/Fire suppression, required-positive-HP, and zero-HP timing are Regeneration parameters/qualifiers, not separate edition engines;
- the same principle applies to saves, recharge, conditions, damage/healing, resistances, immunities, vulnerabilities, Advantage/Disadvantage, auras, reactions, legendary mechanics, and other reusable combat semantics.

No 2024-specific resolver may be introduced for a mechanic already represented correctly by the 2014-backed universal primitive. If the 2024 wording truly changes the semantics, preserve only that delta through ruleset-scoped data or behavior.

The canonical 2024 SRD catalog contains 330 source monsters.

Monster promotion path:

`SRD source -> source/parser audit -> detected mechanics -> universal capabilities -> runtime -> Python behavior -> browser parity -> generated artifact -> public readiness -> exact-head CI`

- Re-audit all 330 monsters after adding a universal capability.
- A creature becomes runnable only when every outcome-changing printed mechanic is supported or explicitly proven irrelevant under the permanent arena contract.
- Never use a richer/partially parsed stat block to certify a simpler approximation.

## 26. Homebrew target architecture

Future homebrew uses the same rules engine:

- hard edition lock;
- schema-driven supported mechanical blocks;
- free-form flavor/name/description only;
- no arbitrary executable mechanics text;
- supported blocks may be combined if all prerequisites/dependencies are satisfied;
- unsupported mechanics are not silently approximated/certified;
- user owns balance/CR; engine validates technical/mechanical completeness, not power level.

## 27. Victory and safety stop

A team loses when no member remains capable of meaningful combat action or legally returning an ally to active combat.

- Dead/disintegrated entities do not.
- Petrified/banished/etc. are evaluated by their actual rules rather than automatically treated as dead.
- A true stalemate with no meaningful path to progress is a draw.
- The 100-round cap is an **ENGINE SAFETY STOP**, not an ordinary tactical draw. Preserve the complete reproducible record and flag it for investigation.

## 28. Certification contract

A capability/card is not complete because code exists.

Before calling a tranche certified:

1. source-size/architecture guards pass;
2. Python behavior and tests pass;
3. browser behavior and permanent regressions pass;
4. generated-static parity is clean;
5. source/capability audits pass;
6. certification manifests regenerate cleanly from authoritative state;
7. exact intended head is the commit certified by GitHub Actions;
8. production remains browser-only/backend-free;
9. Netlify is used only for deliberate production hosting checkpoints, not routine development.

Machine-readable counts live in `data/hero_certification_manifest.json` and `data/monster_certification_manifest.json`. Never hand-edit counts to match a desired status claim.

### 2024 Restoring Touch and Lay On Hands pool allocation

At Paladin 14, Restoring Touch can remove Blinded, Charmed, Deafened, Frightened, Paralyzed, and Stunned when Lay On Hands is used. Each removed condition costs five healing-pool points, and those points do not restore HP. Ordinary Poisoned removal can share that activation. Arena AI selects the legal removal-only option and declines optional simultaneous HP restoration.

Lay On Hands healing in both editions uses the remaining finite pool, spending only the chosen useful HP allocation up to the target's missing effective HP. Condition removal never makes remaining pool points unusable. Action cost remains Action in 2014 and Bonus Action in 2024. Live battlefield footprint distance governs touch range in both editions. The 2014 feature has no effect on Undead or Constructs; the 2024 feature has no such exclusion. These source restrictions are declarative target parameters for both healing and condition removal.
