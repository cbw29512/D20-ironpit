"""Source-first regression for one failed save producing damage AND a condition.

The universal composite-save binder must preserve both printed effects and
keep unrelated unsupported actions independently blocked.
"""
from __future__ import annotations

import logging
import pytest

from app.content.monster_attack_effect_validation_2014 import supported_save_damage_2014, supported_composite_save_2014
from app.content.monster_save_condition_validation_2014 import supported_save_condition_2014
from app.content.monster_basic_candidates_2014 import basic_blockers_2014
from app.content.monster_source_2014 import load_monster_source_2014

logger = logging.getLogger(__name__)


def _attack():
    try:
        monster = next(x for x in load_monster_source_2014() if x.id == "quasit")
        return monster, next(a for a in monster.attacks if a.id == "claws-bite-in-beast-form")
    except Exception:
        logger.exception("2014 Quasit source/attack missing")
        raise


def test_composite_failed_save_is_not_misclassified_as_single_effect():
    try:
        monster, attack = _attack()
        row = attack.on_hit_save_effect
        assert row["save_ability"] == "constitution"
        assert row["dc"] == 10
        assert row["damage_dice_count"] == 2
        assert row["damage_dice_size"] == 4
        assert row["damage_type"] == "poison"
        assert row["condition_id"] == "poisoned"
        assert row["duration_rounds"] == 10
        assert row["repeat_save_timing"] == "target_turn_end"
        assert row["success_damage"] == "none"
        # Neither existing primitive alone represents the complete printed action.
        assert not supported_save_damage_2014(row)
        assert not supported_save_condition_2014(row)
        assert supported_composite_save_2014(row)
        assert "attack:complex" not in basic_blockers_2014(monster)
        assert "source:extra-action" in basic_blockers_2014(monster)
    except Exception:
        logger.exception("Composite poison source regression failed")
        raise


@pytest.mark.parametrize("remove_key", [
    "damage_dice_count", "condition_id", "repeat_save_timing",
])
def test_composite_source_fields_must_remain_visible(remove_key):
    try:
        _, attack = _attack()
        row = attack.on_hit_save_effect
        assert remove_key in row
        modified = {key: value for key, value in row.items() if key != remove_key}
        assert modified != row
        # No mutation of the pinned immutable card is permitted.
        assert remove_key in attack.on_hit_save_effect
    except Exception:
        logger.exception("Composite poison schema retention failed")
        raise
