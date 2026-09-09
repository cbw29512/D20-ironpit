# Iron Pit Rules Contract

This is the authoritative product/rules contract for Iron Pit. It describes the intended combat model. Repository code, generated certification manifests, and exact-head permanent tests prove implementation status; they do not override this contract by silently changing a rule.

If implementation and this contract disagree, either fix the implementation or make an explicit product decision to revise this file. Historical milestone documents and conversational progress claims are not authority.

## 1. Core architecture

- Iron Pit is a rules-first automated D&D combat simulator.
- Implement combat mechanics as universal capabilities, not hero-, class-, monster-, or stat-block-name special cases.
- Monster and pregen definitions are declarative data wherever practical.
- Unsupported outcome-changing mechanics fail closed. Never approximate, silently ignore, or invent a combat-relevant mechanic merely to make a card runnable.
- Python is the reference/certification oracle. The browser engine is the production fight engine. Supported capabilities require behavioral parity and permanent regression coverage.
- Noncombat-only rules may be omitted from runtime only when they cannot alter an Iron Pit combat outcome.

## 2. Ruleset isolation

The current certified public ruleset is D&D 2024 / SRD 5.2.1.

The target architecture supports hard ruleset profiles:

- 2014 fights use only 2014 monsters, pregens, spells, features, items, and mechanics.
- 2024 fights use only 2024 monsters, pregens, spells, features, items, and mechanics.
- Never cross editions in one fight.
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

## 7. Initiative — Iron Pit house rule

Normal initiative bonuses and ruleset-specific initiative mechanics apply, with these Iron Pit ordering rules:

- A natural 20 initiative roll is in the top-priority bucket.
- A natural 1 initiative roll is in the bottom-priority bucket.
- Natural 20/1 initiative does not grant or remove actions, attacks, or rounds.
- Within the relevant bucket, preserve the normal initiative result ordering unless an exact tie remains.
- Any unresolved initiative tie is broken by pure d20 rerolls among only the tied combatants.
- Repeat tie rerolls until a complete order exists.
- Multiple natural-20 or natural-1 rollers use the same tie-reroll process among themselves.
- Surprise is resolved separately according to the selected ruleset; it does not automatically move a creature to the bottom of initiative.

## 8. Action economy

- Use the selected edition's RAW Action, Bonus Action, Reaction, movement, Extra Attack, Multiattack, and other action-economy rules.
- Extra Attack is multiple attacks inside the Attack action, not an extra Action.
- Multiattack uses exactly the printed number/types/options/sequence.
- Bonus Actions exist only when a rule grants one.
- Reactions refresh according to RAW.
- Conditions suppress actions/reactions according to RAW.
- Once-per-turn, once-per-round, and once-on-each-of-your-turns are distinct limits.
- Dash/Disengage/Hide/Ready/Help/Search are not generic tactical spam; use them only when a supported combat identity or legal fallback requires them.
- Dodge is a fallback when no meaningful legal offensive/healing/signature action exists.

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
- A flavor-only d6 may narrate the critical; it has no additional mechanical effect.
- Saving throw natural 1/20 values have no extra Iron Pit rule unless RAW for the specific rule says otherwise.

## 9. Advantage and Disadvantage

- Track every source independently for audit and expiry.
- Any Advantage source + any Disadvantage source = normal roll, regardless of how many sources exist on either side.
- Only Advantage sources = Advantage.
- Only Disadvantage sources = Disadvantage.
- Removing one source must recompute from the remaining active sources.

## 10. Arena and movement abstraction

The standard Iron Pit is intentionally compact and prevents kiting/fleeing gameplay.

Target physical concept: 15 ft × 10 ft with 5-ft cells. Current implementation may use a simpler fixed-formation abstraction until the square-grid tranche is certified.

Permanent arena rules:

- No voluntary fleeing, long-range kiting loops, or running circles around melee opponents.
- The Pit deity handles ordinary positioning and closing so combatants can engage; printed movement speed does not prevent a creature from reaching the position required to use an otherwise legal attack.
- Printed Walk, Fly, Climb, Swim, Burrow, Hover, and base-speed data remain source-derived and must not be rewritten merely to make a creature usable in the Pit.
- Movement modes must never be roster-eligibility filters. Aquatic, flying, burrowing, climbing, slow, unusual-biology, breathing, and atmosphere requirements are made hospitable by the Pit rather than modeled as survival blockers.
- Ordinary deity/fixed-formation positioning is an arena abstraction, not a hidden speed buff and not voluntary movement by the combatant.
- Default automated placement: melee/frontline forward, ranged/casters behind. Future manual legal placement is authoritative when selected by the user.
- Every card uses one 5-ft footprint for arena occupancy, regardless of normal creature size. Printed size still matters for RAW mechanics such as grapple/target-size restrictions.
- No environmental cover.
- Clear line of sight by default; only combat effects such as Darkness, Fog Cloud, Blindness, Invisibility, or similar supported mechanics alter visibility.
- No default pits, lava, traps, difficult terrain, water, or random arena hazards. A combatant's supported RAW effect may create an area/hazard.
- Flyers cannot use altitude to become permanently unreachable. A melee flyer must enter its legal reach to attack.
- Opportunity Attacks, forced movement, Disengage consequences, speed changes, Grappled/Prone movement effects, and other combat-relevant movement rules remain RAW where applicable. The deity abstraction must never erase a rule that explicitly keys off movement.

### AoE/targeting arena simplification

- Offensive team AoE is ally-safe in the standard Iron Pit: affect valid opposing-team targets only.
- This does **not** convert every AoE into “all enemies.” Preserve printed radius/shape/range/target counts over occupied squares.
- Selected-target buffs/heals preserve their printed target counts.
- Large areas may hit the whole opposing team only when their actual geometry covers it.

## 11. Damage pipeline

Resolve each damage component separately and preserve source qualifiers.

Universal dimensions include:

- damage type;
- magical/nonmagical or other source qualifiers when relevant;
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

No resurrection is available during an Iron Pit fight. Dead/disintegrated combatants remain out for the match; the Pit deity restores them only after combat.

### Disintegration

A source that says reaching 0 causes disintegration must intercept generic PC death saves first:

- set the combatant to DISINTEGRATED;
- no Death Saving Throws;
- ordinary healing cannot target/restore the combatant;
- remove it from normal active target pools;
- preserve the exact lethal source in the log.

### Petrification

Staged petrification effects use a universal progression/state machine with the exact source saves, stages, timing, immunities, and termination rules. Petrified is not treated as dead unless a rule explicitly makes that consequence apply.

## 14. Conditions and effect lifecycle

Combat-relevant conditions are universal rules, not source-specific implementations. Sources apply/remove/configure them.

Support all selected-edition combat-relevant conditions as needed, including Blinded, Charmed, Deafened, Frightened, Grappled, Incapacitated, Invisible, Paralyzed, Petrified, Poisoned, Prone, Restrained, Stunned, Unconscious, and edition-appropriate additional conditions.

- Track multiple sources where source duration/removal matters.
- Do not multiply the mechanical severity of the same condition merely because multiple sources apply it unless RAW says so.
- Use exact source duration and repeat-save timing.
- Do not invent a default DC or default recovery save.
- Buffs/debuffs/conditions remain visibly attached to cards while active.

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

Do not ban or mechanically compress summons merely to fit the UI.

- Each summoned creature remains an independent mechanical entity with its own HP, actions, saves, conditions, and death.
- Identical summons may be visually stacked (`Wolves ×8`) but are not one creature under the hood.
- If legal summoned occupancy exceeds the standard arena, create the minimum temporary magical Summoning Annex necessary. It cannot be exploited for fleeing/kiting/unreachable flight.
- AoE can affect only the subset whose actual occupied positions are in the area; resolve saves/damage per entity.
- Summon initiative/control/command cost/source-death behavior follows the source RAW.
- Transformations/Wild Shape/Polymorph are replacement forms, not extra bodies.
- Split/spawn mechanics create independent entities when RAW requires.
- Swallow/engulf/banishment/ethereal/possession and similar mechanics use universal location/control/life-state structures rather than creature-name branches.

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
- no upcasting for now; lower-level spells use their printed/native slot level only;
- prioritize highest available native spell level, then work downward, then cantrips when leveled offense is exhausted/not meaningful;
- one enemy: prefer useful high-damage single-target options before AoE;
- multiple enemies: prefer useful high-damage AoE before single-target options;
- damage-first unless control/utility is a defining source identity or is otherwise clearly the meaningful legal action;
- selected-target spell counts and source geometry remain authoritative.

## 23. Weapons, loadouts, and masteries

Weapon properties, masteries, fighting styles, feats, and two-weapon rules are universal selected-edition mechanics.

- Loadout/build data chooses weapons/style; the engine reads the shared weapon catalog.
- Never implement `ClassNameMastery()`/`MonsterNameWeaponRule()` when a universal property/mastery can express it.
- Dual wield/off-hand/Nick/Vex/Graze/Cleave/Push/Topple/Sap/Slow and similar properties use exact edition rules when supported.
- Equipment removal/destruction/suppression during combat immediately changes derived stats/access as RAW requires and is visible on the card.
- Temporary equipment state resets after the match.

## 24. Canonical pregens

- Maintain one persistent named canonical hero per core class.
- Each class progresses level 1–20 through one legal canonical build; a level derives from the previous certified level plus that level's audited combat delta.
- Only certified levels are publicly runnable.
- Combat-relevant class/subclass/species/feat/equipment/spell/resource mechanics must be implemented or remain explicit blockers.
- Noncombat-only choices do not require engine logic.
- Canonical hero construction details live in `CANONICAL_COMBAT_BUILD_POLICY.md`.

## 25. Monsters

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

- Valid summons can keep a team active.
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
