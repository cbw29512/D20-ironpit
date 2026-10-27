from __future__ import annotations

import logging

from app.content.monster_innate_spells_2014 import innate_spell_save_actions_2014
from app.content.monster_innate_support_2014 import supports_innate_spellcasting_2014
from app.content.monster_source_2014 import load_monster_source_2014

logger = logging.getLogger(__name__)


def _pit_fiend():
    try:
        return next(card for card in load_monster_source_2014() if card.id == "pit-fiend")
    except Exception:
        logger.exception("Pinned 2014 Pit Fiend source is missing.")
        raise


def test_innate_fireball_reuses_shared_source_parameterized_spell() -> None:
    try:
        monster = _pit_fiend()
        fireball = next(
            action for action in innate_spell_save_actions_2014(monster)
            if action.id == "fireball"
        )

        assert fireball.name == "Fireball"
        assert fireball.level == 3
        assert fireball.range_ft == 150
        assert fireball.dc == 21
        assert fireball.save_ability == "dexterity"
        assert fireball.damage_dice_count == 8
        assert fireball.damage_dice_size == 6
        assert fireball.damage_type == "fire"
        assert fireball.success_damage == "half"
        assert fireball.area is not None
        assert fireball.area.shape == "radius"
        assert fireball.area.radius_ft == 20
        assert supports_innate_spellcasting_2014(monster) is True

    except Exception:
        logger.exception("2014 innate Fireball integration regression failed.")
        raise


def test_innate_fireball_binding_uses_spell_data_not_monster_identity() -> None:
    try:
        renamed = _pit_fiend().model_copy(update={
            "id": "renamed-fiend",
            "name": "Renamed Fiend",
        })
        fireball = next(
            action for action in innate_spell_save_actions_2014(renamed)
            if action.id == "fireball"
        )
        assert fireball.id == "fireball"
        assert fireball.dc == 21
        assert supports_innate_spellcasting_2014(renamed) is True
    except Exception:
        logger.exception("Renamed innate Fireball binding regression failed.")
        raise
