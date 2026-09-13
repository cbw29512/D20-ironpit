# 2014 Iron Pit monster certification scope

This directory contains the pinned 2014/SRD 5.1 monster source artifacts used by the 2014 Iron Pit certification branch.

## Combat-only spell scope

Iron Pit implements only spells that can materially change an arena combat outcome. Exploration, social, travel, divination, crafting, and other noncombat utility spells are intentionally out of runtime scope.

Regular and innate spellcasting use the same universal combat spell resolver. The source distinction is retained only for usage data such as spell slots, at-will casting, and uses per day.

A combatant may apply one appropriate combat buff immediately before initiative as free pre-combat setup. Dispel Magic is an in-combat action and may remove an opposing pre-combat magical buff, including on the caster's first turn. Antimagic effects suppress magical effects in their printed area while active; they do not require a separate monster-specific subsystem.

Named attacks such as Bite, Claw, Tail, Sting, and weapon names are source data, not separate engine mechanics. The universal attack resolver consumes each attack's hit bonus, damage, damage type, and reusable riders.

Generated browser monster artifacts preserve source-audit fingerprints (traits, reactions, bonus actions, limited-use actions, legendary actions, and spellcasting metadata) so browser certification verifies the same canonical monster data used by the Python engine.

Unsupported outcome-changing mechanics remain fail-closed until represented by a reusable engine capability and proven in both Python and browser runtimes.
