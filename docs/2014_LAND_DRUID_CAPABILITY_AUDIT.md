# 2014 Land Druid Capability Audit

## Scope

Persistent canonical 2014 Thalen Greenbough, Circle of the Land, levels 1–20.

## Classification

| Feature | First level | Classification | Engine plan / current status |
|---|---:|---|---|
| Spellcasting | 1 | ENGINE_EXISTS_COMPOSITION | Shared spell save/attack/healing/buff/concentration/resource primitives are bound through the certified progression. |
| Druidic | 1 | ARENA_NEUTRAL | Language feature cannot change an Iron Pit combat outcome. |
| Wild Shape | 2 | ENGINE_EXISTS_COMPOSITION | Universal replacement-form lifecycle is implemented in Python/browser and bound to certified 2014 beast templates. |
| Druid Circle | 2 | ENGINE_EXISTS_BINDING_MISSING | Circle of the Land identity is bound; later subclass features remain level-gated. |
| Bonus Cantrip | 2 | ENGINE_EXISTS_BINDING_MISSING | Mending is the deterministic arena-neutral bonus cantrip choice. |
| Natural Recovery | 2 | ARENA_NEUTRAL | Rest-time slot recovery does not alter an in-progress Iron Pit fight; all resources reset between matches. |
| Forest Circle Spells — 2nd | 3 | ENGINE_EXISTS_COMPOSITION | Barkskin uses the universal minimum-AC modifier; Spider Climb is arena-neutral on the standard flat Pit. |
| Forest Circle Spells — 3rd | 5 | ARENA_NEUTRAL | The source spells remain recorded. Call Lightning requires vertical storm-cloud placement that is unavailable on the standard authoritative x/y battlefield with horizontal-only flight; Plant Growth has no default normal plants to affect. Neither is selected by Arena AI. |
| Forest Circle Spells — 4th | 7 | ENGINE_EXISTS_COMPOSITION + ARENA_NEUTRAL | Freedom of Movement reuses shared movement/debuff-counter primitives; Divination is arena-neutral. |
| Forest Circle Spells — 5th | 9 | ENGINE_EXISTS_BINDING_MISSING or ARENA_NEUTRAL | Re-audit Commune with Nature and Tree Stride against the standard Pit before binding. |
| Land's Stride | 6 | ENGINE_EXISTS_COMPOSITION | Bound to the universal nonmagical Difficult Terrain counter plus contextual saving-throw Advantage against magical plant impediments. Exact source identity remains Land's Stride. |
| Nature's Ward | 10 | ENGINE_EXISTS_COMPOSITION | Reuse condition-immunity and typed-source defense primitives. |
| Nature's Sanctuary | 14 | ENGINE_EXISTS_PARAMETER_DELTA | Reuse universal targeting/save-gate mechanics with source creature-type qualifiers. |
| Timeless Body | 18 | ARENA_NEUTRAL | Aging cannot alter arena combat. |
| Beast Spells | 18 | ENGINE_EXISTS_BINDING_MISSING | Replacement-form lifecycle exists; add form-state spellcasting permission according to RAW component restrictions. |
| Archdruid | 20 | ENGINE_EXISTS_BINDING_MISSING | Reuse unlimited-resource handling plus Wild Shape/form-state component rules; no Druid-named resolver. |

## Wild Shape parity map

Wild Shape is not a summon. The same combatant changes form and later reverts.

Implemented shared state/lifecycle:

- immutable source combatant template remains unchanged;
- mutable combat state records active replacement form and original-form return state;
- form supplies physical statistics and form attacks/movement/size from certified beast data;
- original mental ability scores are retained through the universal replacement-form compiler;
- form HP is a distinct replacement pool, not Temporary HP;
- reaching 0 form HP reverts and carries excess damage into the original form;
- voluntary reversion follows the source action economy;
- concentration persists through transformation and still uses normal concentration checks;
- active form size/movement/attacks flow through shared combatant primitives;
- fight reset discards all replacement-form state;
- Python and browser use the same declarative replacement-form semantics;
- permanent regressions cover transform, damage routing, zero-HP reversion, excess damage, voluntary reversion, resource spend, concentration persistence, and browser roster resolution.

## Current certification boundary

Levels 1–8 are the current registered 2014 Land Druid certification boundary on this branch.

Level 5 is certified without inventing Call Lightning geometry. The permanent Pit contract defines one authoritative x/y grid and restricts flight to horizontal movement, so the spell's required vertical storm-cloud placement is not a legal standard-Pit action. Its generic concentration repeat-save capability remains available for future content whose geometry is legal.

Plant Growth is likewise arena-neutral on the default battlefield because the Pit supplies no normal plants by default. Both source spells stay in the Forest Circle metadata and must be re-audited if a future arena mode adds qualifying vertical space or normal plants.
