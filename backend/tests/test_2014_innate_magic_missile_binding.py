from __future__ import annotations

from app.combat.auto_hit_spell_policy import choose_auto_hit_spell
from app.combat.auto_hit_spell_resolution import resolve_auto_hit_spell
from app.combat.dice import FixedDiceProvider
from app.combat.state import build_combatant_state
from app.content.capability_compiler import compile_combatant
from app.content.monster_definition_adapter_2014 import adapt_monster_mechanics_2014
from app.content.monster_innate_source_2014 import innate_spells_2014
from app.content.monster_innate_spells_2014 import innate_auto_hit_spell_actions_2014
from app.content.monster_innate_support_2014 import (
    innate_alternate_spell_casts_2014,
    innate_spell_resources_2014,
)
from app.content.monster_source_2014 import load_monster_source_2014
from app.content.monsters import build_commoner
from app.content.sorcerer_draconic_2014_spell_support import magic_missile_2014
from app.domain.encounters import EncounterCombatant, EncounterSetup


def _source(monster_id: str):
    return next(card for card in load_monster_source_2014() if card.id == monster_id)


def test_every_innate_magic_missile_row_binds_exact_at_will_parameters() -> None:
    applicable = [
        card for card in load_monster_source_2014()
        if any(row.get("id") == "magic-missile" for row in innate_spells_2014(card))
    ]
    assert [card.id for card in applicable] == ["night-hag"]
    row, = [row for row in innate_spells_2014(applicable[0]) if row.get("id") == "magic-missile"]
    assert row["usage"] == "at_will"
    assert row["uses_per_day"] is None
    action, = innate_auto_hit_spell_actions_2014(applicable[0])
    assert action == magic_missile_2014()
    grant, = [item for item in innate_alternate_spell_casts_2014(applicable[0]) if item.spell_id == action.id]
    assert grant.cast_level == 1
    assert grant.resource_id is None
    assert not any(item.id == action.id for item in innate_spell_resources_2014(applicable[0]))


def test_innate_magic_missile_is_semantic_not_monster_named() -> None:
    source = _source("night-hag")
    renamed = source.model_copy(update={"id": "synthetic-caster", "name": "Synthetic Caster"})
    assert innate_auto_hit_spell_actions_2014(renamed) == innate_auto_hit_spell_actions_2014(source)
    assert innate_alternate_spell_casts_2014(renamed) == innate_alternate_spell_casts_2014(source)


def test_innate_magic_missile_executes_without_slot_or_daily_resource() -> None:
    template = compile_combatant(adapt_monster_mechanics_2014(_source("night-hag")))
    caster = EncounterCombatant(
        combatant_id="night-hag", side="monsters", position_ft=0,
        state=build_combatant_state(template),
    )
    target_template = build_commoner().model_copy(update={"max_hp": 30})
    target = EncounterCombatant(
        combatant_id="target", side="heroes", position_ft=30,
        state=build_combatant_state(target_template),
    )
    setup = EncounterSetup(
        heroes=[target], monsters=[caster], hero_total_levels=1,
        monster_total_cr="5", ruleset="2014",
    )
    assert not [item for item in caster.state.resources if item.id.startswith("spell-slot-")]
    choice = choose_auto_hit_spell(caster, setup, "1:night-hag")
    assert choice is not None
    assert choice.action.id == "magic-missile"
    assert choice.alternate_cast is not None
    assert choice.alternate_cast.resource_id is None
    event = resolve_auto_hit_spell(
        1, 1, caster, target, setup, choice.action, choice.slot_level,
        choice.projectile_count, "1:night-hag", FixedDiceProvider([1, 2, 3]),
        alternate_cast=choice.alternate_cast,
    )
    assert event.damage_roll is not None
    assert event.damage_roll.total == 9
    assert event.resource_remaining is None
    assert target.state.current_hp == 21
    assert caster.state.spell_slot_expended_turn_key is None
    assert caster.state.action_available is False
