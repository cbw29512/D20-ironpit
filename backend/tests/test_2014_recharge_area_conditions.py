from __future__ import annotations

import logging

from app.content.monster_basic_candidates_2014 import basic_blockers_2014
from app.content.monster_save_capabilities_2014 import (
    recharge_rules_2014,
    save_capabilities_2014,
    save_resources_2014,
)
from app.content.monster_source_2014 import load_monster_source_2014
from app.content.monster_source_limited_audible_conditions_2014 import (
    source_proven_limited_audible_conditions_2014,
)
from app.content.monster_source_recharge_area_conditions_2014 import (
    source_proven_recharge_area_conditions_2014,
)
from scripts.browser_failed_save_timed_serializer import failed_save_timed_effect_row

logger = logging.getLogger(__name__)


def _monster(name: str):
    try:
        return next(item for item in load_monster_source_2014() if item.name == name)
    except Exception:
        logger.exception("Failed to load 2014 source monster %s.", name)
        raise


def test_dust_mephit_blinding_breath_is_source_bound_recharge_area_control() -> None:
    try:
        monster = _monster("Dust Mephit")
        actions = source_proven_recharge_area_conditions_2014(monster)
        assert len(actions) == 1
        action = actions[0]
        assert action.id == "blinding-breath"
        assert action.resource_id == "blinding-breath"
        assert action.area is not None
        assert (action.area.shape, action.area.length_ft) == ("cone", 15)
        assert action.save_ability == "dexterity"
        assert action.dc == 10
        rider = action.failed_save_timed_effect
        assert rider is not None
        assert rider.effect_id == "blinded"
        assert rider.duration_rounds == 10
        assert rider.repeat_save_timing == "target_turn_end"
        assert "mechanic:recharge" not in basic_blockers_2014(monster)
    except Exception:
        logger.exception("Dust Mephit Recharge area-control regression failed.")
        raise


def test_vrock_spores_compile_periodic_poison_damage_and_recharge() -> None:
    try:
        monster = _monster("Vrock")
        actions = source_proven_recharge_area_conditions_2014(monster)
        assert len(actions) == 1
        spores = actions[0]
        assert spores.id == "spores"
        assert spores.area is not None
        assert (spores.area.shape, spores.area.radius_ft) == ("emanation", 15)
        rider = spores.failed_save_timed_effect
        assert rider is not None
        assert rider.effect_id == "poisoned"
        assert rider.repeat_save_timing == "target_turn_end"
        assert rider.allowed_removal_action_ids == ["holy-water"]
        assert rider.start_of_turn_damage is not None
        assert (
            rider.start_of_turn_damage.dice_count,
            rider.start_of_turn_damage.dice_size,
            str(rider.start_of_turn_damage.damage_type),
        ) == (1, 10, "poison")
        browser = failed_save_timed_effect_row(rider)
        assert browser["startOfTurnDamage"] == {
            "diceCount": 1, "diceSize": 10, "damageType": "poison",
        }
    except Exception:
        logger.exception("Vrock Spores regression failed.")
        raise


def test_vrock_stunning_screech_is_source_bound_one_per_day_area_control() -> None:
    try:
        monster = _monster("Vrock")
        actions = source_proven_limited_audible_conditions_2014(monster)
        assert len(actions) == 1
        screech = actions[0]
        assert screech.id == "stunning-screech"
        assert screech.resource_id == "stunning-screech"
        assert screech.requires_target_hearing is True
        assert screech.excluded_target_creature_types == ["demon"]
        assert screech.area is not None
        assert (screech.area.shape, screech.area.radius_ft) == ("emanation", 20)
        resources = {item.id: item.max_uses for item in save_resources_2014(monster)}
        assert resources["stunning-screech"] == 1
        assert resources["spores"] == 1
        assert [(item.resource_id, item.minimum_roll) for item in recharge_rules_2014(monster)] == [
            ("spores", 6),
        ]
    except Exception:
        logger.exception("Vrock Stunning Screech regression failed.")
        raise


def test_vrock_shared_bindings_clear_recharge_and_extra_action_blockers() -> None:
    try:
        monster = _monster("Vrock")
        actions = {item.id for item in save_capabilities_2014(monster)}
        assert {"spores", "stunning-screech"} <= actions
        blockers = basic_blockers_2014(monster)
        assert "mechanic:recharge" not in blockers
        assert "source:extra-action" not in blockers
    except Exception:
        logger.exception("Vrock blocker regression failed.")
        raise
