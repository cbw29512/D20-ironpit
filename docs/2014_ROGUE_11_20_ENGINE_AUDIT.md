# 2014 Thief Rogue levels 11-20 engine audit

## Scope and authority

This audit is intentionally implementation-first and fail-closed. It inventories the combat-relevant RAW gained by the canonical 2014 Thief Rogue after the currently certified level-10 boundary before any runtime or registry widening occurs.

Rules authority: D&D Basic Rules 2014 / SRD 5.1 Rogue and Thief. The existing Iron Pit rules contract remains authoritative for certification policy and edition isolation.

No READY flags, registry entries, generated browser heroes, or manifest counts are changed by this audit.

## Existing universal capability baseline

The current Mara runtime already reuses universal weapon attacks, proficiency/ability math, Sneak Attack progression, Cunning Action, Uncanny Dodge, and Evasion. Levels 11-20 must continue to reuse universal capabilities where semantics match rather than introduce Rogue-specific branches.

## RAW feature inventory and engine disposition

| Level | RAW addition | Combat relevance in Iron Pit | Existing equivalent / required primitive | Disposition before certification |
| ---: | --- | --- | --- | --- |
| 11 | Reliable Talent; Sneak Attack 6d6 | Ability checks can affect Hide/arena decisions; damage progression is direct | Sneak Attack die scaling already exists. No verified generic proficient-check d20 floor was found in the current engine search. | **BLOCKED** on reusable proficient ability-check minimum-roll primitive if an arena path invokes a qualifying check. Do not fake by adding a flat bonus. |
| 12 | Ability Score Improvement | Changes derived combat statistics depending on canonical choice | Existing build-audit/ability-score machinery | **APPROVED**: +2 Constitution (14→16) for survivability and improved Constitution checks/saves. |
| 13 | Use Magic Device; Sneak Attack 7d6 | Magic-item permission is only relevant if canonical arena loadout contains such an item | Existing loadout has no qualifying magic item; Sneak Attack scaling already exists | Treat Use Magic Device as audited but arena-inert for the current mundane loadout; no engine primitive is justified solely for this snapshot. |
| 14 | Blindsense | Hidden/invisible opponents within 10 ft. are combat-relevant | No verified generic short-range hidden/invisible location-awareness capability found in the current engine search | **BLOCKED** on reusable awareness/sense primitive; must use authoritative distance and hearing state. |
| 15 | Slippery Mind; Sneak Attack 8d6 | Adds Wisdom saving-throw proficiency | Existing saving-throw bonus compiler can represent proficiency if supplied the RAW proficiency set | Reuse saving-throw machinery; add Wisdom at level 15. No Rogue-specific engine branch needed. |
| 16 | Ability Score Improvement | Changes derived combat statistics depending on canonical choice | Existing build-audit/ability-score machinery | **APPROVED**: +2 Constitution (16→18). |
| 17 | Thief's Reflexes; Sneak Attack 9d6 | A second turn in round 1 at initiative -10 materially changes combat | No verified generic extra-first-round-turn scheduler capability found in the current engine search | **BLOCKED** on reusable extra-turn scheduling primitive. Must preserve action/bonus/reaction accounting and browser parity. |
| 18 | Elusive | Suppresses attack-roll Advantage against Mara while she is not incapacitated | No verified generic defender advantage-suppression primitive found in the current engine search | **BLOCKED** on reusable conditional attack-advantage suppression primitive. It must not suppress Disadvantage or operate while incapacitated. |
| 19 | Ability Score Improvement; Sneak Attack 10d6 | Changes derived combat statistics depending on canonical choice | Existing build-audit/ability-score machinery | **APPROVED**: +2 Constitution (18→20). |
| 20 | Stroke of Luck | Once per short/long rest, a missed in-range attack can become a hit; failed ability check can become d20=20 | No verified generic post-roll miss-to-hit / failed-check override resource primitive found in the current engine search | **BLOCKED** on reusable post-roll outcome override plus rest-recharging resource. Attack path is arena-relevant even if ability checks are not. |

## Required implementation order

1. Preserve the approved canonical Constitution progression: +2 CON at levels 12, 16, and 19.
2. Extend the private candidate/profile progression without registering it, preserving 2014-only data.
3. Reuse current saving-throw machinery for Slippery Mind and current Sneak Attack scaling for 11/13/15/17/19.
4. Inventory engine code again at implementation time for semantic equivalents to Reliable Talent, Blindsense, Thief's Reflexes, Elusive, and Stroke of Luck. Add a primitive only when no equivalent exists.
5. Any new primitive requires Python tests, browser parity tests, logging, serialization/certification coverage, and permanent CI coverage before Mara's certification boundary moves.
6. Generate canonical artifacts from certification; never hand-edit READY counts.

## Certification blockers

Technical blockers currently identified by this audit: Reliable Talent check-floor semantics (when exercised), Blindsense awareness, Thief's Reflexes first-round extra turn, Elusive advantage suppression, and Stroke of Luck post-roll override/resource semantics.

Content blockers: **none for the level-12/16/19 ASIs**. The approved canonical progression is +2 Constitution at each of those levels.

Levels 12-13 are safe after the approved Constitution ASI: level 12 changes derived HP/CON modifiers, and level 13 Use Magic Device is arena-inert with the canonical mundane loadout. Level 14 remains blocked on reusable Blindsense/awareness semantics.