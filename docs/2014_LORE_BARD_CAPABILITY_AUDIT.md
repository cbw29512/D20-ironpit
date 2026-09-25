# 2014 Lore Bard Capability Audit

This audit covers the canonical 2014 Lore Bard lane before runtime certification. Source ability names remain presentation/audit metadata; runtime bindings must use universal mechanics.

## Class features

| Feature | Level | Classification | Iron Pit binding |
|---|---:|---|---|
| Bardic Inspiration | 1 | ENGINE_TRULY_MISSING | Reuse universal d20 bonus-die roll math, add one shared consumable grant/lifecycle usable by attack rolls, saving throws, and supported ability checks. |
| Spellcasting | 1 | ENGINE_EXISTS_BINDING_MISSING | Bind legal 2014 Bard spell packages to existing spell attack/save/healing/buff/control primitives. |
| Jack of All Trades | 2 | ENGINE_EXISTS_PARAMETER_DELTA | Initiative is a Dexterity ability check; bind half proficiency to otherwise-unproficient supported ability checks. Do not create Bard-specific roll resolution. |
| Song of Rest | 2 | ARENA_NEUTRAL | Iron Pit has no in-fight short-rest healing; combatants reset between matches. |
| Expertise | 3/10 | ENGINE_EXISTS_PARAMETER_DELTA | Compile selected proficient skill bonuses; no new resolver. |
| Font of Inspiration | 5 | ENGINE_EXISTS_PARAMETER_DELTA | Same Bardic Inspiration resource; recovery timing changes to short/long rest. Inter-fight reset remains full by arena contract. |
| Countercharm | 6 | ENGINE_TRULY_MISSING | Reuse contextual save-Advantage semantics/tags; add universal timed friendly-group buff action with range/duration/action cost. |
| Magical Secrets | 10/14/18 | ENGINE_EXISTS_BINDING_MISSING | Deterministically select legal combat spells and reuse their existing primitives. |
| Superior Inspiration | 20 | ENGINE_EXISTS_BINDING_MISSING | Exact match for universal initiative resource refill with zero threshold and restore amount 1. |

## College of Lore

| Feature | Level | Classification | Iron Pit binding |
|---|---:|---|---|
| Bonus Proficiencies | 3 | ARENA_NEUTRAL | Canonical combat build already records relevant skill choices; no new combat resolver. |
| Cutting Words | 3 | ENGINE_TRULY_MISSING | Add universal reaction roll-penalty-die hook; source parameters select eligible enemy attack/check/damage rolls and hearing/charm-immunity qualifiers. |
| Additional Magical Secrets | 6 | ENGINE_EXISTS_BINDING_MISSING | Deterministic legal combat spell selection using existing spell primitives. |
| Peerless Skill | 14 | ENGINE_EXISTS_COMPOSITION | Reuse the same consumable Bardic Inspiration d20 bonus-die grant for the Bard's own supported ability check. |

## Engine work budget for this lane

The intended new universal engine surface is limited to:

1. consumable d20 bonus-die grant/lifecycle;
2. timed friendly-group contextual saving-throw buff action;
3. reaction roll-penalty-die hook.

Everything else is content binding, parameterization, composition, or arena-neutral. If implementation requires more than these three new universal surfaces, re-audit before expanding the engine.
