# 2014 READY Reconciliation Audit

Status: active  
PR branch base commit: `e3b2bffb822d8bd5e89794aeb76388f8f6d8761e`  
Latest audit validation anchor: `7c87cfbaef3349f2eaad86728e09f4ab71935720` (`main`, after PR #344)

The PR branch is intentionally still based on the earlier audit anchor while the audit is active. PR #344 added Paladin audit documentation only; no runtime behavior changed between these anchors. Re-anchor to current `main` before any reconciliation repair is merged.

## Objective

Re-audit every currently certified 2014 pregen level, every currently certified 2014 monster, and the universal combat engine before advancing a new 2014 pregen progression tranche.

This audit exists to catch stale "arena-neutral" assumptions, incomplete feature composition, source/runtime drift, browser/Python parity gaps, and READY entries whose printed combat mechanics are not actually exercised through the universal engine.

## Locked baseline

Current certified 2014 hero progression:
- Fighter 1-20
- Berserker Barbarian 1-20
- Thief Rogue 1-20
- Open Hand Monk 1-20
- Devotion Paladin 1-11
- Total certified hero levels: **91**

Current certified 2014 monsters:
- **128 / 327**

Current paired-edition report:
- 2014 ready: 128 / 327
- 2024 ready: 140 / 330
- shared identities: 288
- both ready: 103
- 2014 catch-up candidates with ready 2024 counterpart: 17
- 2014 ahead: 13
- both blocked: 155

## Audit order

1. Already-certified 2014 heroes.
2. Already-certified 2014 monsters.
3. Universal engine capability and lifecycle coverage against findings from 1-2.
4. Repair only proven gaps.
5. Regenerate artifacts and rerun full certification.
6. Only then resume unfinished 2014 pregen progression work.

## Required classification for every finding

Use exactly one classification before changing runtime code:

- `ENGINE_EXISTS_BINDING_MISSING`
- `ENGINE_EXISTS_CERTIFICATION_MISSING`
- `ENGINE_EXISTS_COMPOSITION`
- `ARENA_NEUTRAL`
- `ENGINE_TRULY_MISSING`

A different printed ability name is never evidence that a new primitive is needed.

## Per-entry acceptance checklist

For each certified hero level or monster:

1. Re-read authoritative edition-specific source facts.
2. Enumerate every combat-relevant printed feature/action/reaction/resource.
3. Decompose each into universal semantics:
   - trigger/timing
   - action/bonus/reaction/free cost
   - resource/recharge/use limit
   - attack/check/save
   - damage/healing
   - condition/state change
   - range/area/geometry
   - duration/expiry
   - interruption/override behavior
4. Search existing hero and monster primitives for semantic equivalence.
5. Verify immutable source data carries the exact parameters and source-facing name.
6. Verify Python reference behavior.
7. Verify browser production parity.
8. Verify permanent regression evidence reaches the live encounter path.
9. Verify generated artifacts are current.
10. Keep READY only if every outcome-changing printed mechanic is supported or explicitly arena-neutral under the current rules contract.

## Known audit finding already repaired

### 2014 Thief Rogue 20 — Stroke of Luck

Prior certification treated the failed-ability-check branch as arena-neutral. That became stale once grapple escape became a live ability-check path.

Repair merged in PR #343:
- attack-miss branch continues to use the universal miss-to-hit override;
- failed ability checks compose the existing universal failed-D20 replacement primitive;
- both consume the same one-use Stroke of Luck resource;
- no Rogue-specific resolver was added.

Classification: `ENGINE_EXISTS_COMPOSITION`.

This is the model for the rest of the audit: re-evaluate old assumptions against the *current* engine, not the engine state that existed when the content was first certified.

## Certified hero audit queue

### Fighter 1-20
Status: AUDITED — ONE REPAIR REQUIRED

Verified represented behavior:
- legal 2014 Human/Champion progression and ASIs;
- Defense Fighting Style and level-10 Archery style;
- Action Surge resource scaling;
- Improved/Superior Critical thresholds;
- Extra Attack progression through four attacks;
- Remarkable Athlete on currently live initiative/Acrobatics paths;
- Indomitable uses/reset count and 2014 no-level-bonus reroll behavior;
- Survivor start-turn healing threshold and amount;
- no 2024 Weapon Mastery or other 2024-only Fighter features.

Finding FTR-2014-001:
- Classification: `ENGINE_EXISTS_BINDING_MISSING`.
- Second Wind is still reached through legacy identity-driven orchestration (`should_use_second_wind`, `use_second_wind`, and browser ability hook id `second-wind`).
- The existing universal `HealingAction` schema already exactly represents the 2014 behavior: self, Bonus Action, 1d10 + Fighter level, one source resource use, Bloodied policy.
- Required repair: bind 2014 Second Wind declaratively to the universal healing path and prove Python/browser live-turn parity without double activation. Do not create a new mechanic.


### Berserker Barbarian 1-20
Status: AUDITED — CERTIFICATION REPAIR REQUIRED

Verified represented behavior:
- Rage damage/resistance/resource lifecycle;
- 2014 Frenzy + exhaustion;
- Reckless Attack and Danger Sense;
- Extra Attack and Fast Movement;
- Mindless Rage immunity to Charmed/Frightened while raging;
- Feral Instinct initiative Advantage;
- Brutal Critical scaling;
- Intimidating Presence save/condition lifecycle;
- Relentless Rage via universal effect-bound survival save;
- Retaliation via universal damage-reaction attack schema;
- Persistent Rage lifecycle;
- Indomitable Might via universal ability-check minimum;
- Primal Champion ability caps and unlimited Rage representation.

Arena-neutral clarification:
- Feral Instinct's surprised-first-turn clause has no live trigger in the standard certified arena because there is currently no surprise-producing path. Initiative Advantage remains live and implemented.

Finding BARB-2014-001:
- Classification: `ENGINE_EXISTS_CERTIFICATION_MISSING`.
- High-level Python/browser regressions for Persistent Rage, Indomitable Might, and unlimited Rage still clone/mutate a certified level-13 card into synthetic level-15/18/20 fixtures.
- Generic primitives are tested, and the actual runtime now exports levels 14-20, but the permanent evidence does not consistently exercise the real certified high-level templates.
- Required repair: replace staged-era mutated fixtures with actual level-14 through level-20 runtime/browser cards and add live encounter-path regressions for Retaliation, Persistent Rage, Indomitable Might, and unlimited Rage. No new engine primitive is indicated.


### Thief Rogue 1-20
Status: AUDITED — ONE ENGINE GAP REQUIRED

Verified represented behavior:
- Sneak Attack scaling and eligible weapons;
- Expertise-derived skill bonuses;
- Cunning Action Dash on the live offensive-movement path;
- Uncanny Dodge and Evasion;
- Slippery Mind save proficiency;
- Thief's Reflexes universal first-round extra-turn scheduling;
- Elusive attack-Advantage suppression;
- Stroke of Luck attack-miss + failed-ability-check composition after PR #343;
- legal ASI progression and 2014/2024 isolation.

Arena-neutral features remain explicitly scoped:
- Fast Hands: no trap/lock/object-use combat loop in the standard arena;
- Second-Story Work: no climbing/running-jump requirement in the standard arena;
- Supreme Sneak: no legal Hide-position loop in the standard open arena;
- Use Magic Device: canonical loadout is mundane;
- Blindsense: no unresolved hidden-creature location loop; authoritative positions are already known;
- Thief's Reflexes surprised exception: no surprise-producing path.

Finding ROG-2014-001:
- Classification: `ENGINE_TRULY_MISSING`.
- Reliable Talent was certified as arena-inert, but that assumption is stale: grapple escape now invokes Mara's proficient/expert Acrobatics ability check.
- RAW semantic requirement: on an ability check that includes Mara's proficiency bonus, a d20 roll of 9 or lower is treated as 10 before the final total is evaluated.
- Existing `AbilityCheckMinimum` / Indomitable Might replaces the final check total with an ability-score floor and is not mechanically equivalent.
- Required repair: add the smallest reusable proficient-ability-check d20-floor primitive in Python/browser, bind Reliable Talent declaratively from level 11, and prove live grapple-escape behavior plus non-proficient checks remaining unaffected. Re-audit heroes/monsters for other consumers after the primitive lands.

Previously repaired finding:
- Stroke of Luck stale failed-ability-check assumption was repaired in PR #343 by composing the existing failed-D20 replacement primitive with the existing attack-miss override and shared one-use resource.


### Open Hand Monk 1-20
Status: AUDITED — THREE COMBAT GAPS REQUIRED

Verified represented behavior:
- Martial Arts die scaling and Bonus Action attack;
- Flurry of Blows resource/action economy;
- Stunning Strike via shared save + timed Stunned condition;
- Wholeness of Body via universal healing;
- Stillness of Mind via universal condition removal;
- Evasion via shared defense primitive;
- Purity of Body poison immunity;
- Tranquility via universal opening targeting ward;
- Diamond Soul save proficiencies + failed-save reroll;
- Quivering Palm via universal deferred save effect;
- Empty Body via universal timed self-buff, universal Invisible, and source-owned timed resistances;
- level-19 canonical ASI (+1 Wisdom / +1 Strength);
- Perfect Self via universal initiative resource refill.

Arena-neutral features:
- Slow Fall: standard certified arena has no falling hazard;
- Tongue of the Sun and Moon: communication does not alter automated arena combat;
- Timeless Body: aging/food/water do not alter arena combat.

Finding MONK-2014-001 — Deflect Missiles follow-up attack:
- Classification: `ENGINE_TRULY_MISSING`.
- Current Python/browser Deflect Missiles only reduces ranged-weapon damage and spends the Reaction.
- 2014 Deflect Missiles also permits spending 1 Ki, when reduction reaches 0, to make the caught missile ranged attack as part of the same Reaction.
- No current caught-projectile / conditional post-deflection attack primitive was found.
- Required repair: add the smallest reusable reaction follow-up attack capability keyed by semantic trigger (eligible projectile damage reduced to 0), resource cost, range, and attack/damage parameters; then bind Deflect Missiles without Monk-name dispatch.

Finding MONK-2014-002 — Open Hand Technique incomplete options:
- Classification: `ENGINE_EXISTS_COMPOSITION` plus one missing primitive.
- Current Python/browser implementation hardcodes only the Dexterity-save Prone option.
- Existing universal forced movement already supports the Strength-save push option's 15-foot movement semantics.
- No generic timed "cannot take reactions" suppression effect was found for the third option.
- Required repair: represent Open Hand Technique as declarative on-hit choices/composition; reuse universal Prone and forced movement; add only the smallest generic timed reaction-suppression primitive for the unmatched effect. Arena AI may deterministically choose among legal supported options, but a target that is already/immune to Prone must not erase other legal Open Hand outcomes.

Finding MONK-2014-003 — Ki-Empowered Strikes source qualifier:
- Classification: `ENGINE_TRULY_MISSING`.
- Level-6 Ki-Empowered Strikes makes unarmed strikes count as magical for overcoming resistance and immunity to nonmagical attacks/damage.
- The current damage-defense model carries damage type but no certified magical/nonmagical source qualifier.
- Required repair: add one universal attack/damage-source qualifier consumed by conditional defenses; bind level-6+ Monk unarmed strikes as magical for this purpose; then re-audit the full 2014 monster roster because any nonmagical B/P/S resistance or immunity may change certification behavior.

Existing endgame bindings remain valid:
- Level 18 Empty Body uses universal timed self-buff + universal Invisible + source-owned timed resistances.
- Level 20 Perfect Self uses universal initiative resource refill.


### Devotion Paladin 1-11
Status: AUDITED — THREE REPAIRS REQUIRED

Verified represented behavior:
- legal 2014 Human/Paladin progression through level 11;
- sword/shield + Defense style AC;
- spell slots and prepared/oath-spell package;
- Divine Smite slot scaling, Fiend/Undead rider, critical doubling, and melee-only trigger;
- Extra Attack;
- Aura of Protection strongest-bonus stacking and live range;
- Aura of Devotion and Aura of Courage live range/immunity;
- Improved Divine Smite declarative radiant rider;
- condition removal, defensive spells, concentration, and Dispel Magic entrypoints.

Arena-neutral features:
- Divine Sense: creature identity is already authoritative to the engine;
- Divine Health disease immunity: the standard arena currently has no disease-effect producer.

Finding PAL-2014-001 — Turn the Unholy lifecycle/turn behavior:
- Classification: `ENGINE_TRULY_MISSING` plus correction of an invalid composition.
- Current shared turning code applies literal `frightened` + `incapacitated`, ends if the source becomes incapacitated/dead, and the current forced-retreat turn logs fleeing without actually moving the creature.
- 2014 turning is not the Incapacitated condition. It restricts the turned creature's turn/reactions and compels movement away; it ends on damage or duration, not merely because the source later becomes incapacitated/dead.
- Required repair: model a universal Turned/forced-retreat behavior with real authoritative-grid movement, reaction suppression, allowed-action restriction, source-distance constraint, and correct end conditions. Reuse universal forced movement/pathing where semantically applicable; do not encode Paladin identity into the resolver.

Finding PAL-2014-002 — Lay on Hands healing pool:
- Classification: `ENGINE_TRULY_MISSING`.
- Current declarative healing action heals `5 * level` and spends `5 * level` pool points every use.
- 2014 Lay on Hands is a point pool: the Paladin chooses how many remaining points to spend, healing the same amount; spending exactly 5 points may instead cure one disease or neutralize one poison.
- Poison removal is already represented at a 5-point cost; disease is arena-neutral today.
- Required repair: add a reusable variable resource-pool healing amount semantic so Arena AI spends only the useful legal amount instead of draining the whole pool on every heal.

Finding PAL-2014-003 — Sacred Weapon magical source qualifier:
- Classification: `ENGINE_EXISTS_COMPOSITION` once MONK-2014-003's universal magical/nonmagical source qualifier lands.
- Sacred Weapon's attack-roll bonus is implemented, but the weapon also becomes magical for the duration if it was not already magical.
- Bind that source-owned timed qualifier to the same universal damage-defense qualifier required by Ki-Empowered Strikes; no Paladin-specific damage-defense code.


## Certified monster audit queue

All **128 currently READY 2014 monsters** must be rechecked against:
- source actions and Multiattack structure;
- attack range/reach;
- saving-throw actions and riders;
- damage defenses;
- conditions and repeat-save lifecycle;
- recharge and limited-use resources;
- reactions;
- bonus/extra actions;
- zero-HP mechanics;
- spellcasting;
- movement-dependent mechanics;
- source traits that can change combat outcomes;
- Python/browser parity and live-path tests.

READY status must fail closed if any printed outcome-changing mechanic is discovered without support.

## Certified monster audit findings

### MON-2014-001 — Flyby falsely classified arena-neutral
- Classification: `ENGINE_TRULY_MISSING`.
- The current 2014 classifier admits Flyby as arena-neutral.
- Full generated-READY-roster sweep confirms **four** affected cards: **Flying Snake, Giant Owl, Owl, Pteranodon**. The earlier three-card list missed Flying Snake.
- Flyby changes Opportunity Attack legality when the creature flies out of an enemy's reach and is therefore outcome-changing under the authoritative grid/OA contract.
- Current universal OA legality checks reactor state, sight, reaction availability, movement source, and Disengage, but carries no immutable mover-side OA exemption.
- Required repair: remove Flyby from the neutral allowlist and add one universal mover-side Opportunity Attack exemption semantic, parameterized so Flyby applies only to qualifying flight movement. Until then, affected cards must fail closed rather than remain READY.

### MON-2014-002 — Echolocation/special senses missing from 2014 source/runtime schema
- Classification: `ENGINE_TRULY_MISSING`.
- Confirmed READY cards currently admitted with Echolocation: **Bat, Giant Bat, Killer Whale, Swarm of Bats**.
- The 2014 source model has no certified senses/blindsight field, and the universal Invisible attack modifier currently has no special-sense override.
- This became directly outcome-changing once Invisible was certified for 2014 Monk Empty Body.
- Required repair: carry authoritative senses/ranges into immutable source data, add universal perception-of-target semantics for effects such as blindsight, and make Invisible/unseen attack modifiers consume that semantic. Until then, Echolocation cards cannot be treated as fully READY against all certified opponents.

### MON-2014-003 — Sunlight Sensitivity depends on an undefined arena environment fact
- Classification: `ARENA_NEUTRAL` only if the rules contract explicitly fixes the standard arena as having no direct sunlight; otherwise `ENGINE_TRULY_MISSING`.
- Confirmed READY card admitted on the current neutral assumption: **Kobold**.
- The standard-arena contract already fixes clear line of sight, no environmental cover, and no default pits/lava/traps/difficult terrain/water/random hazards, so terrain-dependent neutral traits can be evaluated deterministically.
- The contract still does **not** define direct sunlight/lighting state.
- Required repair: either lock the standard arena lighting environment explicitly (making Sunlight Sensitivity deterministically active or inactive as specified) or model environmental sunlight and its attack/Perception disadvantage. Do not silently assume a lighting state.

## Cross-edition findings exposed by the 2014 reconciliation

These findings are recorded now because the same universal mechanic/certification policy is shared across editions. They do **not** authorize skipping the 2014-first repair order.

### XED-MON-001 — 2024 Flyby and Agile are also falsely arena-neutral
- Classification: `ENGINE_TRULY_MISSING`.
- The 2024 trait source audit currently lists both `Flyby` and `Agile` as arena-neutral.
- Current 2024 READY Flyby cards: **Hippogriff, Owl, Pteranodon, Giant Owl, Giant Wasp, Flying Snake, Gargoyle**.
- Current 2024 READY Agile cards: **Deer, Rat**.
- Both mechanics change Opportunity Attack legality. Flyby is movement-mode-qualified; Agile is not.
- The same universal mover-side OA-exemption primitive required by MON-2014-001 must support these source-specific parameters rather than adding Flyby- or Agile-named resolvers.
- Re-audit both editions after that primitive lands and fail closed any affected READY card until its binding/parity evidence is present.

### XED-MON-002 — 2024 Sunlight Sensitivity shares the same undefined environment dependency
- Classification: `ARENA_NEUTRAL` only after an explicit no-direct-sunlight arena contract; otherwise `ENGINE_TRULY_MISSING`.
- Current 2024 READY affected card: **Kobold Warrior**.
- The source trait changes attack rolls/ability checks while in sunlight, so the same environment decision as MON-2014-003 must be edition-neutral.

### XED-ARCH-001 — 2024 READY monster authoring remains overwhelmingly legacy-derived
- Classification: `ENGINE_EXISTS_BINDING_MISSING` as architecture/content migration debt; this fact alone is **not** a RAW-readiness blocker when source audits and runtime behavior are complete.
- Current 2024 READY runtime count: **140**.
- `combatant_capabilities_v1.json` contains **138** monster definitions generated from `build_legacy_monster_templates(include_capability_migrated=False)`.
- `combatant_capabilities_native_v1.json` contains only **2** native monster definitions: Swarm of Insects and Swarm of Venomous Snakes.
- Required follow-up after the READY correctness gate: migrate repeated families from imperative legacy builders into authoritative declarative capability data one semantic family at a time, preserving source-audit parity and exact behavior. Do not bulk-rewrite working mechanics.

## Monster defense gate verification

- The 2014 basic-candidate gate already fails closed on `unsupported_defense_text`.
- The 128 generated READY 2014 monsters currently expose only unconditional typed resistances/immunities/vulnerabilities supported by the existing damage-type path; conditional nonmagical-attack defense text is not silently admitted through this basic roster.
- This means MONK-2014-003 remains a real universal capability gap, but it has **not** already corrupted the current 128-monster READY set through a known conditional-defense admission.
- The blocked/catch-up monsters that use conditional magical/nonmagical defenses must be re-evaluated when the universal source qualifier lands.

## Paired-edition catch-up queue after READY reconciliation

Do not process these until the currently READY 2014 roster is revalidated.

Current 17 reported 2014 catch-up entries:
1. Gargoyle
2. Bandit Captain
3. Violet Fungus
4. Animated Armor
5. Cultist
6. Grimlock
7. Lemure
8. Frog
9. Scout
10. Earth Elemental
11. Xorn
12. Druid
13. Boar
14. Giant Boar
15. Knight
16. Grick
17. Manticore

The paired report is a queue, not proof of readiness.

## Universal engine audit areas

The engine audit must reconcile all currently used capability families, including:
- attack resolution and hit outcomes;
- saving throws and ability checks;
- advantage/disadvantage;
- damage typing and defenses;
- conditions and timed/source-owned effects;
- action economy;
- resource spending/reset;
- movement/grid/reach/range/area geometry;
- reactions and post-damage triggers;
- healing/temporary HP/max HP changes;
- concentration;
- recharge and limited-use lifecycle;
- initiative hooks;
- zero-HP/death/survival replacement;
- support-action selection;
- Main Action selection;
- ability-hook sequencing;
- generated serializer parity;
- Step/Watch/Replay/Turbo canonical-event-stream invariance.

## Definition of Done

This reconciliation is complete only when:

- all 91 currently certified 2014 hero levels have been re-audited;
- all 128 currently certified 2014 monsters have been re-audited;
- every discovered gap is repaired or the affected entry is blocked;
- no READY entry depends on stale arena-neutral assumptions;
- no source ability is implemented by hero/class/monster name when a universal primitive can represent it;
- Python and browser parity are proven for every retained READY capability;
- generated artifacts are regenerated from authoritative source/runtime code;
- 2014 Hero Certification is green;
- Paired Edition Monster Report is green;
- full exact-head CI is green;
- only after this gate may the next unfinished 2014 pregen progression tranche advance.
