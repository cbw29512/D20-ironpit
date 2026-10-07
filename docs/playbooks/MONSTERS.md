# Monster Implementation Guide

Use this guide for monster traits, actions, reactions, legendary actions, defenses, recharge, conditions, and certification.

Read first: `SOUL.md`, this file, `docs/CURRENT_OPERATING_STATUS.md`, and the exact monster source for the correct edition.

## What a monster is

A monster is immutable source data plus declarative bindings to the universal engine.

### Monster/source owns

- name, source identity and ruleset;
- AC, HP, ability scores, size, creature type and speeds;
- attack bonus and exact attack profile;
- save DC and save ability;
- damage dice, bonus and damage type;
- range, reach, area, target count and geometry;
- duration, recharge threshold and limited uses;
- condition/effect parameters and qualifiers;
- exact printed ability name for cards/logs.

### Universal engine owns

- how attack rolls work;
- how AC is checked;
- how saving throws/checks work;
- how damage/healing resolve;
- what conditions do;
- how resistance/immunity/vulnerability work;
- action economy, timing, movement, recharge and other shared mechanics.

**Blinded is Blinded. Prone is Prone. A saving throw is a saving throw.**  
The monster supplies the numbers; the engine supplies the behavior.

All fight-only mutation lives in temporary combat state and resets after the match.

## Add or fix a monster

1. Read the exact source text and edition.
2. Rewrite each combat ability without its printed name:
   `trigger/timing -> action/resource -> attack/check/save -> damage/healing -> condition/state -> range/area/movement -> duration -> exits/reset`.
3. Search existing **monster and pregen** implementations for every semantic piece.
4. Classify the gap:
   - `ENGINE_EXISTS_BINDING_MISSING`
   - `ENGINE_EXISTS_CERTIFICATION_MISSING`
   - `ARENA_NEUTRAL`
   - `ENGINE_TRULY_MISSING`
5. Reuse or compose existing universal primitives.
6. Bind only the monster's source parameters.
7. Prove one representative monster.
8. Expand the same binding to the mechanically identical family.
9. Run one focused family verification, regenerate owned outputs, then use one final-head CI pass.
10. Update blocker/tracker truth and continue.

## Hard blocker rule

Monster work never invents engine behavior.

If a printed outcome-changing mechanic is not exactly supported, **park that monster/ability and keep moving**. Record the printed name, exact missing semantic, and why it cannot certify.

Never:

- approximate it;
- silently ignore it;
- create a monster-name or ability-name resolver;
- weaken certification;
- strip the printed mechanic;
- guess RAW or Chris's intent.

Return to parked technical debt only after the current pass is exhausted. If RAW meaning, architecture, or equivalence is uncertain, ask Chris one precise question before implementation.

## Arena/environment exceptions

Use only established Iron Pit rules. Do not invent new environmental exceptions.

High-level examples already established:

- the Pit is hospitable to printed creature biology/movement modes;
- hospitality does not create water, rocky terrain, or another missing environment;
- environment-only traits stay inactive when their required context is absent;
- standard-Pit flight is horizontal-only;
- separate summoned/conjured combat entities are currently arena-unavailable.

For any environmental edge case, read `docs/IRON_PIT_RULES_CONTRACT.md` and `docs/IRON_PIT_LOCKED_RULES.md`. Never extrapolate from this summary.

## Edition rule

Finish/bind 2014 first, then inspect 2024 for reuse.

Different AC, DC, dice, range, duration, recharge threshold, damage amount/type, target count, or uses are **source data**, not new mechanics. Keep 2014 and 2024 source data independent even when they bind to the same engine primitive.

## Example: 2014 Brass Dragon Sleep Breath

Behavior:

`Action -> breath Recharge 5-6 -> cone -> CON save -> failed save Unconscious -> ends on damage OR ally Action to wake -> otherwise duration expires`

Reuse:

- save action;
- area targeting;
- recharge;
- timed condition;
- universal `unconscious`;
- damage-triggered expiry;
- generic condition-removal action.

Do not create a Brass Dragon or Sleep Breath resolver. Each dragon card supplies its own DC, cone, duration, recharge and printed name.

## Done means

Exact source behavior; no unsupported outcome-changing mechanic; immutable source; temporary/resetting fight state; universal reuse; Python/browser parity; generated outputs refreshed; blocker/tracker truth current; focused checks and exact-head CI green.
