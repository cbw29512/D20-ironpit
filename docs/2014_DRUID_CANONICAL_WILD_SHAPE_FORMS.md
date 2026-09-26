# 2014 Druid Canonical Wild Shape Forms

## Circle of the Land — Thalen Greenbough

Iron Pit uses one deterministic canonical Wild Shape form at each 2014 Land Druid breakpoint. This avoids creature-selection AI drift and keeps replacement-form certification finite.

| Druid level | Max CR | Movement gate | Canonical form | Purpose |
|---|---:|---|---|---|
| 2–3 | 1/4 | No swim or fly | Wolf | Baseline replacement form; Bite + Prone exercises shared attack/control semantics. |
| 4–7 | 1/2 | Swim allowed, no fly | Crocodile | Adds grapple/restrain semantics using existing shared control primitives. |
| 8–20 | 1 | Swim/fly allowed | Brown Bear | Durable melee benchmark with Multiattack and straightforward damage. |

Rules:

- The canonical form changes only when the Druid reaches the next legal Wild Shape breakpoint.
- A higher-level Druid does not dynamically choose among all legal beasts; Iron Pit uses the table above.
- Wild Shape is a replacement form, not a summon.
- Form data must come from the certified 2014 monster/beast source pipeline where available.
- No beast-specific combat resolver is permitted. Form attacks, movement, size, AC, HP, saves, and traits must flow through shared combatant primitives.
- Mental ability retention, form HP/reversion, excess-damage carryover, concentration persistence, and resource use remain governed by the universal replacement-form lifecycle.

## Future Circle of the Moon benchmark

Circle of the Moon is not part of Thalen's current 2014 Land Druid progression. For future Moon-Druid engine expansion, reserve:

- CR 2 benchmark beast: **Polar Bear**
- Elemental Wild Shape benchmark: one of the printed Air/Earth/Fire/Water Elemental forms, using the subclass feature's two-use Wild Shape cost.

These are future capability targets only and do not alter Land Druid certification.


## Iron Pit Druid combat sequence

The deterministic Land Druid combat plan is:

1. **Opening free buff before initiative** — use one legal available combat buff under the global Iron Pit opening-buff rule. Prefer a non-concentration buff when available so the concentration slot remains free.
2. **Establish concentration** — on the first normal turn, cast the highest-priority legal concentration spell for the current build when that improves the fight.
3. **Wild Shape** — on the next legal Action, enter the canonical form for the current level.
4. **Maintain concentration while shaped** — replacement form does not end concentration by itself. Incoming damage in beast form still triggers normal concentration checks.
5. **Fight in form** — use the canonical beast's shared attacks/control/movement until reversion or until a higher-priority legal action is required.

If the chosen concentration spell itself is used as the single free opening buff, the Druid may Wild Shape with the first normal-turn Action.

Circle of the Land uses the printed Action cost for Wild Shape. Future Circle of the Moon support may use its subclass-specific bonus-action transformation rule, but that must not leak into Land Druid behavior.
