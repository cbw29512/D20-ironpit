# 2014 Open Hand Monk Levels 18–20 Capability Audit

Base: `ec6a2b974aa8e61e23cdb0aca4c8fc9a611f27e4` (`main` after certified Monk 17).

## Authoritative RAW source

SRD 5.1 / 2014 Monk progression:

- Level 18: proficiency +6, Martial Arts 1d10, 18 ki, +30 ft. Unarmored Movement, **Empty Body**.
- Level 19: 19 ki, **Ability Score Improvement**.
- Level 20: 20 ki, **Perfect Self**.

Empty Body: action + 4 ki; invisible for 1 minute and resistant to all damage except force for that duration. Its separate 8-ki Astral Projection option is non-arena travel and should not be selected in Iron Pit combat.

Perfect Self: when initiative is rolled and the Monk has 0 ki, regain 4 ki.

Source: D&D Beyond Basic Rules 2014 / SRD 5.1 Monk class (`https://www.dndbeyond.com/sources/dnd/basic-rules-2014/classes`).

## Universal-engine inventory before implementation

### Existing reusable capabilities

1. **Finite resources / spending** — existing `resources` state and resource-cost event/logging paths already represent ki spending. Do not add Monk-specific counters.
2. **Invisible condition** — the condition system already recognizes `invisible`; use the shared timed-condition/effect lifecycle rather than an `empty_body_invisible` flag.
3. **Typed resistance** — `temporary_damage_resistances` plus `damage_defenses.py` already applies resistance. Empty Body should supply all supported damage types except Force as source parameters; damage math remains universal.
4. **Action economy** — Empty Body consumes the normal Action. Use the shared action availability path.
5. **Initiative** — initiative is already a universal lifecycle boundary. Perfect Self belongs in a reusable initiative-triggered resource-floor/refill hook, not in Monk initiative code.
6. **Level-19 ASI** — progression/profile data only. Recompute derived AC, attacks, saves, DCs, and initiative from the chosen canonical ability increase; no new engine primitive.

### Genuine capability gaps / required generalization

**A. Timed composite self-effect**

The engine has timed conditions/effects and temporary typed resistances, but the current resistance examples (notably Rage and defensive spells) own their cleanup in source-specific code. Empty Body requires one 1-minute source effect to own both `invisible` and a temporary resistance set and remove both when the same effect expires. Implement this as a reusable data-driven timed self-effect/buff primitive if no existing generic owner/cleanup API can express it exactly.

Required semantics:

- source effect id and display name are data;
- duration is 10 rounds / 1 minute;
- condition list is data (`invisible`);
- resistance list/exclusions are data (all supported damage types except `force`);
- resource id/cost and action cost are data;
- expiration removes only state owned by this effect, preserving overlapping resistance/condition sources;
- Python/browser parity and event logging are mandatory.

**B. Initiative-triggered resource refill**

No current repository search found a generic initiative hook that conditionally restores a finite resource from zero. Perfect Self therefore needs a reusable rule such as `initiative_resource_refill(resource_id, when_at_or_below, restore_to)` or equivalent data-driven capability. It must execute after initiative is rolled, log the source feature, and never exceed the configured target/cap.

This primitive should also be reusable for mechanically equivalent class/monster features; do not name it for Perfect Self.

## Certification plan

### Level 18

- Extend the 2014 Monk canonical profile/runtime/attack helpers through level 18.
- Add Empty Body feature data.
- Certify 18 ki and +30 ft. movement.
- Python tests: action + 4 ki, 10-round duration, Invisible active, resistance halves every supported non-Force damage type, Force remains unresisted, expiry cleanup, overlapping resistance ownership, insufficient-ki illegality, source-name logging.
- Browser parity tests for the same state transitions and damage results.
- Add capability coverage entry referencing both implementations/tests.
- Regenerate browser/catalog artifacts; READY must be produced only by certification.

### Level 19

- Canonical ASI decision: +1 Wisdom (19→20) and +1 Strength (13→14).
- Test all changed derived values: AC, Strength/Wisdom saves, Monk save DCs, skills, HP, attacks, and Ki.
- No engine work: level 19 is progression data plus derived-stat recompilation.

### Level 20

- Extend ki cap to 20 and add Perfect Self data.
- Implement/use generic initiative resource refill.
- Python/browser tests: 0 ki -> 4 at initiative; 1+ ki -> unchanged; never above cap; correct feature log; 2014-only scope.
- Add permanent capability coverage and certification regression.

## Edition separation

Do not reuse 2024 Monk level-18/20 feature data. 2024 Superior Defense is a different activation/cost/effect package, and 2024 Body and Mind changes Dexterity/Wisdom. Shared internals are permitted only for genuinely equivalent mechanics (typed resistance, resource spending, timed effects, initiative hooks).

## Expected count movement

After certified Monk 18, the 2014 catalog is 89/240. Level 19 raises it to 90/240; level 20 raises it to 91/240. This document does not change READY state or counts.
