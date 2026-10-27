from __future__ import annotations

from app.combat.spell_choice import SpellChoice
from app.combat.spell_save_effect_resolution import compile_spell_save_action
from app.content.monster_innate_source_2014 import innate_spells_2014
from app.content.monster_innate_spells_2014 import innate_spell_save_actions_2014
from app.content.monster_innate_support_2014 import (
    innate_alternate_spell_casts_2014,
    innate_spell_resources_2014,
)
from app.content.monster_source_2014 import load_monster_source_2014
from app.content.shared_control_spells_2014 import blindness_deafness_2014


def _source(monster_id: str):
    return next(card for card in load_monster_source_2014() if card.id == monster_id)


def _blindness(card):
    return next(
        action for action in innate_spell_save_actions_2014(card)
        if action.id == "blindness-deafness"
    )


def test_every_innate_blindness_source_row_binds_exact_parameters() -> None:
    cards = load_monster_source_2014()
    applicable = [
        card for card in cards
        if any(row.get("id") == "blindness-deafness" for row in innate_spells_2014(card))
    ]
    assert [card.id for card in applicable] == ["deep-gnome-svirfneblin"]
    action = _blindness(applicable[0])
    assert action.name == "Blindness/Deafness"
    assert action.level == 2
    assert action.action_cost == "action"
    assert action.range_ft == 30
    assert action.requires_target_sight is True
    assert action.save_ability == "constitution"
    assert action.dc == 11
    assert action.concentration is False
    assert action.duration_minutes == 1
    effect = action.failed_save_timed_effect
    assert effect is not None
    assert effect.effect_id == "blinded"
    assert effect.duration_rounds == 10
    assert effect.expiry_timing == "target_turn_end"
    assert effect.repeat_save_ability == "constitution"
    assert effect.repeat_save_dc == 11
    assert effect.repeat_save_timing == "target_turn_end"
    resource, = [
        item for item in innate_spell_resources_2014(applicable[0])
        if item.id == "blindness-deafness"
    ]
    assert resource.max_uses == 1
    grant, = [
        item for item in innate_alternate_spell_casts_2014(applicable[0])
        if item.spell_id == "blindness-deafness"
    ]
    assert grant.cast_level == 2
    assert grant.resource_id == "blindness-deafness"
    assert grant.resource_cost == 1


def test_innate_blindness_is_source_semantic_and_uses_shared_compiler() -> None:
    source = _source("deep-gnome-svirfneblin")
    renamed = source.model_copy(update={"id": "synthetic-blindness-card", "name": "Synthetic"})
    assert _blindness(renamed) == _blindness(source)
    action = compile_spell_save_action(SpellChoice(_blindness(renamed), 2, ("target",)))
    assert action.failed_save_timed_effect is not None
    assert action.failed_save_timed_effect.effect_id == "blinded"
    assert action.failed_save_timed_effect.repeat_save_timing == "target_turn_end"


def test_shared_blindness_builder_is_dc_parameterized() -> None:
    assert blindness_deafness_2014(11).dc == 11
    assert blindness_deafness_2014(19).failed_save_timed_effect.repeat_save_dc == 19
