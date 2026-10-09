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


## Iron Pit 2014 Land Druid combat plan — caster-first

**October 9, 2026 user decision:** Land and other caster-oriented Druids
primarily remain spellcasters. Do **not** automatically Wild Shape after
casting a Concentration spell. Reserve Wild Shape as an emergency defensive
buffer once the Druid is pressed hard on HP, evaluated against healing and
other legal spell choices. The current conservative executable AI gate permits
an emergency candidate at **one-third or less of its original HP**, while
never changing printed source ability or preventing manual lawful use.
This is an Iron Pit AI heuristic, **not a RAW threshold**.

1. Pre-combat legal buffs are handled by the existing generic source policy.
2. Maintain the best legal Concentration spell, then prefer damage/control
   spells, recovery or protection. **Do not immediately transform at high HP.**
3. If original HP falls to one-third or less and an available Wild Shape form
   offers useful extra survivability, spend the printed **Action** and one
   Wild Shape use to enter the already-certified canonical level form.
   Prefer a life-saving immediate spell when shape-changing would be inferior.
   The current runtime implements the HP availability gate; the broader
   spell-vs-form **opportunity-value comparison remains a separate task**.
4. **2014 Wild Shape does not heal original HP.** It gives the fresh beast's
   separate HP pool; on reversion the Druid returns to exactly the earlier
   normal HP minus any overflow injury. At zero form HP, existing universal
   reversion rules apply.
5. Do not automatically cycle in and out in caster mode simply to replenish
   form HP. A new printed Wild Shape use is not free; preserve the limits.
   Normal form's Concentration may continue while transformed, including
   canonical Concentration saves after damage.

## Moon Druid distinction — not part of this Land Druid pregen

2014 Circle of the Moon is intended to play as a Wild Shape frontline build.
Starting at **Druid level 2** it uses **Bonus Action** to enter Wild Shape,
instead of the normal Action; source-legal Beast CR starts at 1 and increases
per Circle Forms, while movement gates remain source-correct. Unlike Land, its
AI may transform tactically at healthy HP. A Moon Druid can spend a **Bonus
Action and a spell slot while transformed** to recover **1d8 Beast-form HP per
spell-slot level**. Reverting (Bonus Action on its turn) and later reentering
with a new printed Wild Shape use gives a **fresh Beast-form HP pool**, not
healing to the Druid's original HP. The printed Bonus Action/resource economy
prevents instant free form cycling.

For 2024, all Druids get **Bonus Action Wild Shape**, retain normal HP and
gain level-based **Temporary HP**. The 2024 Circle of the Moon instead gains
**three times Druid level** Temporary HP and source-defined form AC; it
can cast its **Circle of the Moon Spells**, including Cure Wounds, in Beast
form, but it does **not** inherit 2014 Combat Wild Shape's spell-slot-for-1d8
form-HP healing. Temporary HP do not stack, and reversion does not heal
normal HP. Honor source-known forms and legal CR/movement restrictions.

This AI-role distinction is implemented as a declarative per-source
`ai_use_policy` value: `emergency_only` for existing caster Druids;
`tactical` for future fully certified Moon or other frontline transformations.
This **does not** itself add a Moon Druid build. Existing one-form-per-level
Land certification and the separate 2024 form roster remain unchanged.

2014 source: https://www.dndbeyond.com/sources/dnd/basic-rules-2014/classes
2014 Moon class feature: https://dnd5e.wikidot.com/druid:moon
2024 source: https://www.dndbeyond.com/sources/dnd/br-2024/character-classes
2024 Moon source: https://www.dndbeyond.com/posts/1755-the-2024-circle-of-the-moon-druid-and-changes-to
