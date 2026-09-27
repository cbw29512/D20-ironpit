# 2014 Fiend Warlock Capability Audit

## Scope

Active canonical hero: **Varek Ashenmark**, 2014 Warlock, Fiend Patron, `blaster` combat build.

This audit starts the 2014 lane from current `main` after the Draconic Sorcerer 1–20 merge. It does **not** reuse the repository's existing Warlock progression/subclass tables as 2014 rules data because those tables are sourced to the 2024 Warlock and encode 2024-only progression facts such as patron-at-3, Magical Cunning, prepared-spell counts, and Epic Boon.

Source authority for this lane: **D&D Beyond Basic Rules 2014 — Warlock / The Fiend**, cross-checked against the repository's edition-isolation and canonical-build contracts.

## Level 1 RAW state

2014 Warlock level 1 supplies:

- d8 Hit Die;
- light armor and simple-weapon proficiency;
- Wisdom and Charisma saving throw proficiency;
- two Warlock cantrips known;
- two 1st-level Warlock spells known;
- one Pact Magic slot, slot level 1;
- Pact Magic slot recovery on a short or long rest;
- Otherworldly Patron at level 1;
- Fiend Patron at level 1;
- Fiend Expanded Spell List adds legal spell choices rather than auto-preparing them;
- Dark One's Blessing at level 1.

The 2014 Fiend progression continues patron features at levels 6, 10, and 14. Do not copy the 2024 patron-at-3 progression.

## Canonical build

Repository policy already defines the Fiend Warlock canonical role as the **blaster / eldritch-blaster** lane.

Level-1 spell choices must therefore be deterministic, legal 2014 choices that favor executable combat mechanics. Spell/loadout selection is data; it must not create new engine mechanics.

## Level 1 semantic decomposition

### Pact Magic

**Classification:** existing resource/casting mechanics plus 2014 progression data.

Required parameters:

- source name: `Pact Magic`;
- resource: Pact Magic spell slot;
- level 1 maximum: 1;
- level 1 slot level: 1;
- reset: short rest or long rest;
- all Pact Magic slots share the current Warlock slot level.

Do not model 2014 Pact Magic with the 2024 prepared-spell progression table.

### Eldritch Blast and other attack/save spells

**Classification:** existing universal spell primitives.

Use the normal spell-attack / save-damage / concentration / damage pipelines according to each selected spell's actual RAW behavior. No Warlock-named spell resolver is permitted.

### Dark One's Blessing

2014 behavior: when the Warlock reduces a hostile creature to 0 HP, the Warlock gains Temporary HP equal to Charisma modifier + Warlock level, minimum 1.

Semantic pieces:

- **trigger:** source combatant reduces a hostile target from above 0 HP to 0 HP;
- **action cost:** none;
- **recipient:** source combatant;
- **effect:** Temporary HP;
- **amount:** source Charisma modifier + source Warlock level;
- **minimum:** 1;
- **duration:** normal Temporary HP lifecycle;
- **resource cost / recharge:** none;
- **source-facing log name:** `Dark One's Blessing`.

### Reuse decision

The **Temporary HP primitive already exists** and remains authoritative. Dark One's Blessing must feed that primitive.

The missing piece is a generic source-owned **hostile-zeroing/defeat trigger**. Repository search found no existing universal trigger that means “this source caused a hostile creature to transition from HP > 0 to HP = 0.”

This is therefore **not a new Temporary HP mechanic**. It is a reusable trigger/configuration gap around the existing Temporary HP primitive.

## Required generic trigger contract before implementation

Proposed declarative shape:

- trigger id: `source-reduces-hostile-to-zero-hp`;
- require source attribution on the damage event;
- require target hostility relative to the source;
- require target HP transition from `> 0` to `0`;
- do not retrigger from additional damage while the target is already at 0 HP;
- if a target later returns above 0 HP and is reduced to 0 again, the transition is eligible again;
- apply the declared universal effect only after the normal damage-defense and zero-HP lifecycle has resolved;
- preserve the exact source ability name in the event/log;
- support all damage families that can truthfully attribute the zeroing to a source, not only weapon attacks.

The trigger must not branch on `warlock`, Varek, `fiend-patron`, or `dark-ones-blessing`.

## State contract

Source/card state stays immutable.

Combat state owns:

- current HP;
- Temporary HP;
- action/resources;
- source-owned effect state if the generic trigger needs ephemeral bookkeeping.

No permanent kill counter is required for Dark One's Blessing. The transition is event-driven.

## Certification requirements

Level 1 cannot be READY until permanent Python and browser tests prove:

1. the 2014 Warlock progression values are edition-correct;
2. Pact Magic uses the correct 2014 slot count/slot level and reset semantics;
3. the canonical spell package is legal 2014 Warlock content;
4. Eldritch Blast and selected spells use existing universal spell mechanics;
5. Dark One's Blessing grants the correct Temporary HP after a hostile 0-HP transition;
6. it does not trigger for an ally, self, or a target already at 0 HP;
7. it can trigger again after a target is restored above 0 and later reduced to 0 again;
8. Temporary HP uses the repository's edition-specific non-stacking replacement/retention rule;
9. Python/browser behavior matches;
10. 2024 Warlock data remains unchanged.

## Next implementation step

Implement the generic hostile-zeroing trigger in the smallest shared event/resolution layer that can observe source attribution and the HP transition across every supported damage family. Then bind Dark One's Blessing declaratively and certify Varek level 1 before progressing to level 2.
