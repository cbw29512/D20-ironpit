# Universal Engine Implementation Guide

Use this guide when a monster/pregen exposes a shared combat-mechanic gap or an existing primitive must be corrected.

Read first: `SOUL.md`, this file, the exact source behavior exposing the gap, and current code/tests for the nearest existing primitive.

## Engine ownership

**The engine owns behavior. Source content owns exact numbers.**

The engine does not decide a monster's AC, DC, attack bonus, damage dice, range, duration or recharge number. It defines how those values are used.

Examples:

- source says AC 17; engine defines attack roll vs AC;
- source says DC 15 DEX save; engine defines saving-throw resolution;
- source says 2d6+4 fire; engine defines rolling/applying typed damage;
- source says Prone; engine defines every Prone consequence;
- source says Recharge 5-6; engine defines recharge timing/roll behavior.

Never hardcode source identity or source-specific numbers into a universal resolver.

## Required implementation map

Every universal primitive must map through:

`immutable source parameters -> domain/capability schema -> temporary combat state -> Python rules resolver -> browser resolver -> serializer/generated data -> audit/event evidence -> permanent tests`

Primary locations:

- schema/capabilities: `backend/app/domain/`
- Python rules reference: `backend/app/combat/`
- browser runtime: `frontend/browser-*.js`
- serialization/generation: `scripts/`
- permanent Python tests: `backend/tests/`
- permanent browser tests: `frontend/*.test.cjs`

If the current primitive lives elsewhere, follow current repository code rather than forcing this map mechanically.

## Universal mechanic catalog

This is the search checklist before new engine code.

| Mechanic | Engine responsibility | Typical source parameters / anchors |
|---|---|---|
| Attack roll | d20 mode, hit/miss, critical, AC comparison | attack bonus, weapon/spell profile; `combat/attacks.py`, browser attack modules |
| Saving throw | d20 save, modifiers, success/failure | ability, DC, success/failure effects; `combat/saving_throws.py`, `browser-saving-throws.js` |
| Ability check | d20 check and modifiers | ability/skill, DC/contest | search current `backend/app/combat/` check resolvers and browser equivalents |
| Advantage/Disadvantage | combine universal sources into roll mode | qualifying trigger/source | attack/save modifier modules; never ability-name dispatch |
| Damage | roll/apply typed damage in order | dice, bonus, type, qualifiers | damage pipeline, `damage_defense_evaluation.py`, browser damage modules |
| Resistance/Immunity/Vulnerability | modify typed damage | defense type/qualifier | domain capabilities + shared damage-defense pipeline |
| Healing | restore HP within legal limits | dice/amount/resource/target | `combat/healing.py`, `healing_resolution_support.py`, browser healing |
| Temporary HP | apply/replace temporary HP | amount/source | combat state + browser state/healing paths |
| Conditions | one canonical semantic state per condition | condition id, duration, exits | `domain/action_types.py`, `combat/condition_rules.py`, browser condition rules |
| Timed effects | apply, expire and remove temporary effects | duration/timing/exit flags | timed-effect schema + Python/browser timed-condition modules |
| Condition removal | remove allowed conditions through generic actions | action cost, target, removable ids | `combat/condition_removal*.py`, browser condition removal |
| Action economy | legal/spent Action, Bonus Action, Reaction | cost/timing | `combat/action_economy.py`, `browser-action-economy.js` |
| Resources | spend/restore limited or unlimited uses | resource id/count/cost | template resources + temporary runtime state |
| Recharge | restore expended capability from recharge rule | threshold/timing | `domain/recharge.py`, `browser-recharge.js` |
| Targeting/areas | legal target geometry | range, cone/line/radius/target count | `domain/targeting.py`, `combat/area_targeting.py`, browser area targeting |
| Movement | legal grid movement and speed consumption | speeds, reach, forced distance | grid/movement/reaction modules; battlefield contract |
| Failed-save forced movement | on a failed save, send declared distance through shared forced-movement/grid legality | source `failure_push_ft` -> `SaveCapabilityDefinition.failed_save_push_ft` -> `SavingThrowAction.failed_save_push_ft` | `combat/saving_throws.py`, shared forced-movement module, `browser-saves.js` |
| Reactions/OA | trigger legality and reaction spend | trigger, reach/range, qualifiers | shared reaction/movement modules |
| Concentration | start, maintain, save, end | effect id, duration, DC rules | `combat/concentration*.py`, `browser-concentration*.js` |
| Zero HP/death | unconscious/death/stabilization lifecycle | source-specific riders/qualifiers | `combat/zero_hp*.py`, death/instant-death modules, browser zero-HP |
| Buff/Debuff | semantic modifier + timing + qualifiers | modifier, duration, scope | typed modifier/timed-effect systems |
| Multiattack/sequence | execute complete legal printed sequence | slots/variants/counts | attack-action definitions + shared sequence selection |
| Replacement form | temporary combat form/state | form template, HP mode, exits | replacement-form schema/runtime |
| Audit/log | record evidence only | printed source name + generic mechanic ids | audit/event schema; never changes outcomes |

### Canonical condition IDs

Current shared condition vocabulary is defined in `backend/app/domain/action_types.py`:

`blinded, charmed, deafened, exhaustion, frightened, grappled, incapacitated, invisible, paralyzed, petrified, poisoned, prone, restrained, stunned, unconscious`.

A source that applies one of these binds to that condition. It does not create a source-specific version.

Likewise, source-declared forced movement is data, not a named ability subsystem. For example, a breath weapon that says a failed save pushes a target supplies the save/DC/area/push distance; the generic save and forced-movement engines own resolution.

## Before adding a primitive

1. Describe the exact behavior without the printed ability name.
2. Split it into existing mechanics from the catalog.
3. Search both Python and browser engines plus monster and pregen bindings.
4. If composition is exact, reuse it.
5. If an existing primitive is missing one generic parameter, widen that primitive rather than creating a sibling implementation.
6. Only if exact composition is impossible may the issue be classified `ENGINE_TRULY_MISSING`.

**Do not implement the new primitive immediately from content work.** Park the content, record the gap, finish the current pass, then return to engine technical debt deliberately.

If RAW meaning, lifecycle, timing, ownership, or equivalence is uncertain, ask Chris before coding.

## Adding a genuine new primitive

When technical-debt work returns to a confirmed `ENGINE_TRULY_MISSING` gap:

1. Define schema and immutable parameters first.
2. Define mutable combat state, lifecycle, expiry and reset behavior.
3. Identify where it enters the canonical resolution sequence.
4. Implement Python reference behavior with explicit errors/logging.
5. Implement equivalent browser behavior with explicit failure handling.
6. Serialize only declarative data needed by the browser.
7. Emit audit evidence without letting audit code affect results.
8. Add focused Python/browser parity regressions.
9. Re-audit both pregens and monsters for every source that can now reuse it.
10. Remove obsolete duplicate/special-case paths.

Never weaken tests or certification to admit unsupported content.

## Example: Sleep/Wake metadata

Suppose source data already describes:

- failed save -> `unconscious`;
- duration;
- ends on damage;
- an ally can spend an Action to wake the sleeper.

If the timed-effect pipeline carries condition/duration but drops the allowed-removal metadata, do **not** create a Sleep subsystem.

Widen the generic timed-effect schema/serializer/runtime to carry the removal permission, then use the existing `unconscious` and condition-removal primitives.

## Done means

The primitive is source-neutral; source numbers remain content data; schema/state/lifecycle are explicit; Python/browser behavior matches; reset is correct; serialization is declarative; permanent tests exist; affected monster/pregen content is re-audited.

For deep lifecycle/ordering changes read `docs/UNIVERSAL_COMBATANT_ARCHITECTURE.md` and `docs/COMBAT_RESOLUTION_PIPELINE.md`. For battlefield geometry read `docs/VTT_CARD_BATTLEFIELD_CONTRACT.md`.
