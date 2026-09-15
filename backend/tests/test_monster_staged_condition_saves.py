from __future__ import annotations

import logging

import pytest

from app.content.monster_source_save_candidates import source_save_candidates

logger = logging.getLogger(__name__)


@pytest.mark.parametrize(
    ("monster", "recharge", "dc"),
    (("Basilisk", 4, 12), ("Medusa", 5, 13)),
)
def test_petrifying_gaze_compiles_as_recharge_bonus_action_staged_save(
    monster: str,
    recharge: int,
    dc: int,
) -> None:
    try:
        row = {
            "name": monster,
            "actions": "",
            "bonusActions": (
                f"Petrifying Gaze (Recharge {recharge}-6). Constitution Saving Throw: DC {dc}, "
                f"each creature in a 30-foot Cone. If the {monster.lower()} sees its reflection in the Cone, "
                f"the {monster.lower()} must make this save. First Failure: The target has the Restrained "
                "condition and repeats the save at the end of its next turn if it is still Restrained, ending "
                "the effect on itself on a success. Second Failure: The target has the Petrified condition "
                "instead of the Restrained condition."
            ),
        }
        actions, resources = source_save_candidates(row)

        assert len(actions) == 1
        assert len(resources) == 1
        action = actions[0]
        resource = resources[0]
        assert action.name == "Petrifying Gaze"
        assert action.action_cost == "bonus_action"
        assert action.save_ability == "constitution"
        assert action.dc == dc
        assert action.range_ft == 0
        assert action.area is not None
        assert action.area.shape == "cone"
        assert action.area.origin == "self"
        assert action.area.length_ft == 30
        assert action.resource_id == resource.id
        assert resource.recharge is not None
        assert resource.recharge.minimum_roll == recharge

        assert len(action.failure_effects) == 1
        effect = action.failure_effects[0]
        assert effect.kind == "condition"
        assert effect.condition == "restrained"
        assert effect.repeat_save_ability == "constitution"
        assert effect.repeat_save_dc == dc
        assert effect.repeat_save_timing == "target_turn_end"
        assert effect.repeat_save_failure_condition == "petrified"
    except Exception:
        logger.exception("Petrifying Gaze source compilation regression failed for %s.", monster)
        raise


def test_underspecified_multistage_save_still_fails_closed() -> None:
    try:
        actions, resources = source_save_candidates({
            "name": "Test Brute",
            "actions": (
                "Petrifying Gaze. Constitution Saving Throw: DC 11, one creature within 30 feet. "
                "First Failure: The target has the Restrained condition. "
                "Second Failure: The target has the Petrified condition."
            ),
            "bonusActions": "",
        })
        assert actions == []
        assert resources == []
    except Exception:
        logger.exception("Incomplete staged save must remain fail-closed.")
        raise
