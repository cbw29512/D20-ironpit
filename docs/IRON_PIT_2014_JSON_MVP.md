# Iron Pit 2014 JSON MVP

## Purpose

Build the 2014 monster version of Iron Pit around one canonical JSON monster catalog and one universal combat engine.

This document is the scope lock for the 2014 workstream. If a task does not directly advance this MVP, defer it.

## Core Architecture

```text
2014 SRD monster source
        ↓
canonical monster JSON
        ↓
thin loader / validator
        ↓
universal combat engine
        ↓
temporary fight state
```

The monster catalog owns monster facts. The engine owns combat rules.

### Monster data belongs in JSON

Examples:
- name / slug
- AC
- HP and hit dice
- STR / DEX / CON / INT / WIS / CHA
- saves and skills
- movement modes
- senses
- CR
- resistances
- immunities
- vulnerabilities
- attacks
- attack bonus
- reach / range
- damage dice and damage type
- actions / reactions / traits
- recharge values
- save DCs
- targeting / area data
- conditions and durations once normalized

### Engine logic stays universal

Examples:
- attack roll resolution
- AC checks
- damage rolls
- resistance / immunity / vulnerability
- saving throws
- melee vs ranged range checks
- movement to enable the desired action
- multiattack
- recharge
- conditions
- grapples / restraint
- AoE targeting
- recurring / timed effects

Never add monster-name-specific resolver branches when a reusable mechanic can represent the behavior.

## MVP Goal

Prove that monsters can be added by data instead of custom code.

A monster should be usable by:

```text
add / convert JSON record
→ validate record
→ load record
→ fight
```

No per-monster Python or JavaScript combat implementation should be required unless the monster introduces a genuinely unsupported universal mechanic.

## MVP Scope

### Phase 1 — Catalog boots

- Add the supplied 2014 monster JSON as the initial source catalog.
- Load all available monster records without hand-registering monsters.
- Preserve source values for basic monster facts.
- Validate required fields and report malformed records clearly.
- Support lookup by stable id / slug.

### Phase 2 — Basic combat from JSON

Prove at least one simple melee monster and one ranged-capable monster can fight using only catalog data.

Required universal mechanics:
- initiative
- AC
- HP
- melee attack rolls
- ranged attack rolls
- attack bonus
- reach / normal range / long range where available
- damage dice + modifier
- damage type
- death / 0 HP
- basic movement to enter legal range

### Phase 3 — Core defensive attributes

Add direct JSON-driven handling for:
- damage resistance
- damage immunity
- damage vulnerability

Prove these with representative monsters; do not create monster-specific branches.

### Phase 4 — First special-mechanic slice

Add only enough structured special-action support to prove the architecture extends cleanly.

Target reusable mechanics:
- saving throw action
- condition application
- recharge
- multiattack

Do not attempt every unusual 2014 ability before the MVP is demonstrated.

## MVP Definition of Done

The MVP is complete only when all of the following are true:

- [ ] The 2014 monster catalog is committed to the 2014 branch.
- [ ] Basic monster facts come directly from the catalog, not duplicated registries.
- [ ] Monsters can be looked up by id / slug.
- [ ] At least one simple melee monster completes a fight from JSON data only.
- [ ] At least one ranged-capable monster completes a fight from JSON data only.
- [ ] AC, HP, attack bonus, range, damage and damage type are read directly from JSON-derived data.
- [ ] Resistance, immunity and vulnerability are engine mechanics driven by monster data.
- [ ] Runtime combat state resets between fights.
- [ ] Adding a basic compatible monster requires data only, not a new resolver branch.
- [ ] A small automated test proves a newly added JSON monster can be loaded and fought without editing the engine.

## Explicit Non-Goals Until MVP Is Done

Do not spend time on these before the MVP checklist above is complete:

- 2024 monster conversion or certification
- full 327-monster special-ability coverage
- pregens
- UI redesign / polish
- character art / silhouettes
- deployment polish
- exhaustive certification manifests
- duplicate compiler/enrichment pipelines
- hand-written per-monster modules
- performance optimization unless the MVP is actually too slow to run
- every legendary action / lair action / niche trait

## Rules Learned From the 2024 Work

Keep the useful lessons:

1. One universal engine.
2. Monster differences are data.
3. Runtime state is temporary.
4. Damage types, saves, conditions and resources must be explicit structured concepts.
5. Python and browser implementations should consume the same normalized monster definitions.
6. Unsupported mechanics should be reported clearly rather than silently ignored.
7. Movement should be action-driven: choose desired legal action, use it if already in range, otherwise move only enough to enable or improve it.
8. AoE targeting should maximize useful enemy targets when that mechanic is added.
9. Do not let one unusual monster block progress on compatible monsters.

Do not keep the expensive lessons:

- no parser → candidate → enrichment → compiler → generated registry → reconciliation chain for ordinary monster facts
- no repeated rebuilding of AC, HP, damage, range or resistance data that already exists in the source catalog
- no full-roster certification cycle for every small development change

## Development Order

Work in this order unless this document is intentionally changed:

1. Catalog file + loader
2. Schema / validation
3. Basic melee fight
4. Basic ranged fight
5. Resist / immune / vulnerable
6. Multiattack
7. Saving throw actions
8. Conditions
9. Recharge
10. Inventory unsupported mechanics across the whole catalog
11. Group unsupported abilities into reusable mechanic families
12. Expand engine by highest-yield mechanic family

## Progress Rule

Track progress by **universal mechanic coverage**, not by creating custom fixes for individual monsters.

If a monster is blocked by a missing reusable mechanic:
- record the mechanic
- record all monsters that need it
- continue with monsters already supported
- implement the mechanic when it is the highest-value next family

## 2014 / 2024 Separation

The 2014 JSON work lives on `feat/2014-json-engine`.

The 2024 Recharge/certification work remains preserved separately and is not the source branch for this MVP.

Long-term target:

```text
2014 catalog ─┐
              ├── universal Iron Pit engine
2024 catalog ─┘
```

The ruleset should select data, not select a separate combat engine.

## Scope Change Rule

Before adding a major feature not listed in the MVP, update this document first and explain why it is required for the MVP.

When in doubt: finish the smallest working JSON-driven fight first.
