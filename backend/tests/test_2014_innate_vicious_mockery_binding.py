from __future__ import annotations

from app.content.bard_2014_vicious_mockery import vicious_mockery_action_2014
from app.content.monster_innate_source_2014 import innate_spells_2014
from app.content.monster_innate_spells_2014 import innate_spell_save_actions_2014
from app.content.monster_innate_support_2014 import innate_spell_resources_2014
from app.content.monster_source_2014 import load_monster_source_2014


def _source(monster_id: str):
    return next(card for card in load_monster_source_2014() if card.id == monster_id)


def _mockery(card):
    return next(action for action in innate_spell_save_actions_2014(card) if action.id == "vicious-mockery")


def test_every_innate_vicious_mockery_row_binds_exact_parameters() -> None:
    applicable = [
        card for card in load_monster_source_2014()
        if any(row.get("id") == "vicious-mockery" for row in innate_spells_2014(card))
    ]
    assert [card.id for card in applicable] == ["green-hag"]
    row, = [row for row in innate_spells_2014(applicable[0]) if row.get("id") == "vicious-mockery"]
    assert row["usage"] == "at_will"
    assert row["uses_per_day"] is None
    action = _mockery(applicable[0])
    assert action == vicious_mockery_action_2014(12)
    assert action.range_ft == 60
    assert action.save_ability == "wisdom"
    assert action.damage_dice_count == 1
    assert action.damage_dice_size == 4
    assert action.damage_type == "psychic"
    assert action.success_damage == "none"
    assert action.requires_target_hearing is True
    assert action.requires_target_sight is True
    assert action.failed_save_timed_effect is not None
    assert action.failed_save_timed_effect.next_attack_disadvantage is True
    assert not any(resource.id == "vicious-mockery" for resource in innate_spell_resources_2014(applicable[0]))


def test_innate_vicious_mockery_is_semantic_not_monster_named() -> None:
    source = _source("green-hag")
    renamed = source.model_copy(update={"name": "Synthetic Mockery Caster"})
    assert _mockery(renamed) == _mockery(source)


def test_shared_vicious_mockery_builder_accepts_source_dc() -> None:
    assert vicious_mockery_action_2014(12).dc == 12
    assert vicious_mockery_action_2014(19, 4).damage_dice_count == 4
