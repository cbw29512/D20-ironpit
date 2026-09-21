# 2014 Thief Rogue levels 11-20 engine audit

## Scope and authority

This audit is intentionally implementation-first and fail-closed. It inventories the combat-relevant RAW gained by the canonical 2014 Thief Rogue after the currently certified level-10 boundary before any runtime or registry widening occurs.

Rules authority: D&D Basic Rules 2014 / SRD 5.1 Rogue and Thief. The existing Iron Pit rules contract remains authoritative for certification policy and edition isolation.

Current certification boundary on this branch: **level 20 candidate-complete**. Exact-head certification gates remain authoritative before merge.

## Existing universal capability baseline

The current Mara runtime already reuses universal weapon attacks, proficiency/ability math, Sneak Attack progression, Cunning Action, Uncanny Dodge, and Evasion. Levels 11-20 must continue to reuse universal capabilities where semantics match rather than introduce Rogue-specific branches.

## RAW feature inventory and engine disposition

| Level | RAW addition | Combat relevance in Iron Pit | Existing equivalent / required primitive | Disposition before certification |
| ---: | --- | --- | --- | --- |
| 11 | Reliable Talent; Sneak Attack 6d6 | Ability checks can affect Hide/arena decisions; damage progression is direct | Sneak Attack die scaling already exists. No verified generic proficient-check d20 floor was found in the current engine search. | **BLOCKED** on reusable proficient ability-check minimum-roll primitive if an arena path invokes a qualifying check. Do not fake by adding a flat bonus. |
| 12 | Ability Score Improvement | Changes derived combat statistics depending on canonical choice | Existing build-audit/ability-score machinery | **APPROVED**: +2 Constitution (14→16) for survivability and improved Constitution checks/saves. |
| 13 | Use Magic Device; Sneak Attack 7d6 | Magic-item permission is only relevant if canonical arena loadout contains such an item | Existing loadout has no qualifying magic item; Sneak Attack scaling already exists | Treat Use Magic Device as audited but arena-inert for the current mundane loadout; no engine primitive is justified solely for this snapshot. |
| 14 | Blindsense | Provides location awareness for hidden/invisible creatures within 10 ft. while Mara can hear; it does **not** grant sight | The certified arena has no Hide/location-guess loop and no certified opponent path that creates unresolved creature-location state | **AUDITED / ARENA-INERT** for the current certified matrix. Do not use it to bypass invisible-attacker visibility rules or Uncanny Dodge's "can see" requirement. |
| 15 | Slippery Mind; Sneak Attack 8d6 | Adds Wisdom saving-throw proficiency | Existing saving-throw bonus compiler can represent proficiency if supplied the RAW proficiency set | Reuse saving-throw machinery; add Wisdom at level 15. No Rogue-specific engine branch needed. |
| 16 | Ability Score Improvement | Changes derived combat statistics depending on canonical choice | Existing build-audit/ability-score machinery | **APPROVED**: +2 Constitution (16→18). |
| 17 | Thief's Reflexes; Sneak Attack 9d6 | A second turn in round 1 at initiative -10 materially changes combat | Shared declarative first-round extra-turn scheduler with backend/browser parity | **IMPLEMENTED / CERTIFICATION CANDIDATE**: offset is data-driven at -10; no Rogue-specific turn-loop branch. |
| 18 | Elusive | Suppresses attack-roll Advantage against Mara while she is not incapacitated | Shared defender attack-Advantage suppression primitive with backend/browser parity | **IMPLEMENTED / CERTIFICATION CANDIDATE**: suppresses Advantage sources only while not incapacitated and preserves Disadvantage. |
| 19 | Ability Score Improvement; Sneak Attack 10d6 | Changes derived combat statistics depending on canonical choice | Existing build-audit/ability-score machinery | **IMPLEMENTED / CERTIFICATION CANDIDATE**: approved +2 Constitution (18→20), CON 20, and Sneak Attack 10d6. |
| 20 | Stroke of Luck | Once per short/long rest, a missed in-range attack can become a hit; failed ability check can become d20=20 | Shared declarative miss-to-hit override resource with backend/browser parity | **IMPLEMENTED / CERTIFICATION CANDIDATE**: first missed in-range arena attack spends the resource automatically; if the miss is a natural 1, Stroke of Luck overrides it before Iron Pit turn termination, producing a normal hit rather than a critical. Ability-check branch remains arena-inert while no qualifying check path exists. |

## Required implementation order

1. Preserve the approved canonical Constitution progression: +2 CON at levels 12, 16, and 19.
2. Extend the private candidate/profile progression without registering it, preserving 2014-only data.
3. Reuse current saving-throw machinery for Slippery Mind and current Sneak Attack scaling for 11/13/15/17/19.
4. Inventory engine code again at implementation time for semantic equivalents to Reliable Talent, Blindsense, Thief's Reflexes, Elusive, and Stroke of Luck. Add a primitive only when no equivalent exists.
5. Any new primitive requires Python tests, browser parity tests, logging, serialization/certification coverage, and permanent CI coverage before Mara's certification boundary moves.
6. Generate canonical artifacts from certification; never hand-edit READY counts.

## Certification blockers

Deferred general engine gaps: Reliable Talent check-floor semantics if a future certified path invokes a qualifying proficient ability check, Blindsense location-awareness semantics if a future arena path introduces unresolved creature location, and Stroke of Luck's failed-ability-check branch while no qualifying arena check path exists. No active 2014 Rogue combat blocker remains through level 20.

Content blockers: **none for the level-12/16/19 ASIs**. The approved canonical progression is +2 Constitution at each of those levels.

Levels 12-20 are safe in the current certification candidate matrix: level 12 applies CON 16; level 13 Use Magic Device is arena-inert with the mundane loadout; level 14 Blindsense is location-awareness only and the arena has no unresolved-location loop; level 15 reuses the shared saving-throw compiler for Wisdom proficiency and Sneak Attack 8d6; level 16 applies CON 18. Levels 17-20 now use reusable engine primitives or existing build math. Stroke of Luck uses a one-use fresh-fight resource and the shared miss-to-hit interrupt; Chris explicitly approved overriding a natural 1 immediately when the resource is available.