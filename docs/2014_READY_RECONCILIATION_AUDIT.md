# 2014 READY Reconciliation Audit

Status: active  
Base commit: `e3b2bffb822d8bd5e89794aeb76388f8f6d8761e`

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
Status: PENDING FULL RE-AUDIT
- Level 18 Empty Body uses universal timed self-buff + universal Invisible + source-owned timed resistances.
- Level 19 canonical ASI: +1 Wisdom / +1 Strength.
- Level 20 Perfect Self uses universal initiative resource refill.

### Devotion Paladin 1-11
Status: PENDING FULL RE-AUDIT

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
