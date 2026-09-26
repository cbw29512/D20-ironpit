# 2014 Land Druid Capability Audit

## Scope

Persistent canonical 2014 Thalen Greenbough, Circle of the Land, levels 1–20.

## Classification

| Feature | First level | Classification | Engine plan |
|---|---:|---|---|
| Spellcasting | 1 | ENGINE_EXISTS_BINDING_MISSING | Reuse shared spell save/attack/healing/buff/concentration/resource primitives. |
| Druidic | 1 | ARENA_NEUTRAL | Language feature cannot change an Iron Pit combat outcome. |
| Wild Shape | 2 | ENGINE_TRULY_MISSING | Requires a universal replacement-form lifecycle shared with Polymorph/future transformations. |
| Druid Circle | 2 | ENGINE_EXISTS_BINDING_MISSING | Bind Circle of the Land source data; subclass identity is persistent. |
| Bonus Cantrip | 2 | ENGINE_EXISTS_BINDING_MISSING | Spell-package data only. |
| Natural Recovery | 2 | ARENA_NEUTRAL | Rest-time slot recovery does not alter an in-progress Iron Pit fight; all resources reset between matches. |
| Circle Spells | 3/5/7/9 | ENGINE_EXISTS_BINDING_MISSING or ARENA_NEUTRAL per spell | Reuse existing spell primitives; arena-neutral spells remain source metadata. |
| Land's Stride | 6 | ENGINE_EXISTS_COMPOSITION | Reuse movement/debuff-counter primitives for nonmagical difficult terrain/plants where battlefield semantics apply. |
| Nature's Ward | 10 | ENGINE_EXISTS_COMPOSITION | Reuse condition-immunity and typed-source defense primitives. |
| Nature's Sanctuary | 14 | ENGINE_EXISTS_PARAMETER_DELTA | Reuse universal targeting/save-gate mechanics with source creature-type qualifiers. |
| Timeless Body | 18 | ARENA_NEUTRAL | Aging cannot alter arena combat. |
| Beast Spells | 18 | ENGINE_EXISTS_BINDING_MISSING after Wild Shape | Form-state casting permission; depends on replacement-form support. |
| Archdruid | 20 | ENGINE_EXISTS_BINDING_MISSING after Wild Shape | Unlimited Wild Shape resource plus form-state component handling; depends on replacement-form support. |

## Wild Shape parity map

Wild Shape is not a summon. The same combatant changes form and later reverts.

Required shared state/lifecycle before certification:

- immutable source combatant template remains unchanged;
- mutable combat state records active replacement form and original-form return state;
- form supplies physical statistics and form attacks/movement/size as required by source rules;
- original mental ability scores and eligible retained proficiencies/features remain source-governed;
- form HP is a distinct temporary replacement pool, not Temporary HP;
- reaching 0 form HP reverts and carries excess damage into the original form;
- voluntary reversion follows source action economy;
- concentration and other effects persist or end only when source rules require;
- grid footprint/range/movement consume the active form's size and movement modes;
- fight reset discards all form state;
- Python and browser use the same declarative replacement-form data and lifecycle;
- permanent tests cover transform, damage, zero-HP reversion, excess-damage carryover, voluntary reversion, resource spend, and reset.

Until that universal lifecycle exists, level 2+ Druid certification fails closed rather than ignoring Wild Shape.
