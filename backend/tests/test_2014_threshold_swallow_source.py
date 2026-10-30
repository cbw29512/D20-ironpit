from __future__ import annotations

import logging

import pytest

from app.content.demo import build_demo_fighter
from app.content.monster_basic_candidates_2014 import basic_blockers_2014
from app.content.monster_grapple_swallow_source_2014 import source_grapple_swallow_2014
from app.content.monster_source_2014 import load_monster_source_2014
from app.domain.swallow_actions import swallow_action_from_source
from scripts.browser_template_serializer import template_row

logger = logging.getLogger(__name__)
CORPUS = {monster.id: monster for monster in load_monster_source_2014()}


@pytest.mark.parametrize(
    "monster_id,threshold,dc,range_ft,all_swallowed,delivery_mode,max_swallowed",
    [
        ("behir", 30, 14, 10, False, "action_attack", 1),
        ("remorhaz", 30, 15, 10, True, "action_attack", None),
        ("kraken", 50, 25, 10, True, "attack_hit", None),
        ("tarrasque", 60, 20, 10, True, "action_attack", None),
    ],
)
def test_threshold_regurgitation_profiles_are_source_proven(
    monster_id, threshold, dc, range_ft, all_swallowed, delivery_mode, max_swallowed,
) -> None:
    try:
        monster = CORPUS[monster_id]
        original = monster.model_dump_json()
        profile = source_grapple_swallow_2014(monster)

        assert profile is not None
        assert profile.source_name == "Swallow"
        assert profile.attack_id == "bite"
        assert profile.delivery_mode == delivery_mode
        assert profile.max_swallowed == max_swallowed
        assert profile.regurgitation_damage_threshold == threshold
        assert profile.regurgitation_save_ability == "constitution"
        assert profile.regurgitation_save_dc == dc
        assert profile.regurgitation_range_ft == range_ft
        assert profile.regurgitation_all_swallowed is all_swallowed
        assert monster.model_dump_json() == original
    except Exception:
        logger.exception("Threshold Swallow source proof failed for %s.", monster_id)
        raise


def test_kraken_browser_card_uses_attack_hit_delivery() -> None:
    try:
        profile = source_grapple_swallow_2014(CORPUS["kraken"])
        action = swallow_action_from_source(profile)
        assert action is not None
        assert action.delivery_mode == "attack_hit"

        row = template_row(
            build_demo_fighter().model_copy(update={"swallow_actions": [action]})
        )
        serialized = row["swallowActions"][0]
        assert serialized["deliveryMode"] == "attack_hit"
        assert serialized["maxSwallowed"] is None
    except Exception:
        logger.exception("Kraken attack-hit Swallow serialization regression failed.")
        raise


def test_complete_327_card_scan_proves_only_supported_swallow_grammars() -> None:
    try:
        assert len(CORPUS) == 327
        proven = {
            monster.id for monster in CORPUS.values()
            if source_grapple_swallow_2014(monster) is not None
        }
        assert proven == {
            "behir", "giant-frog", "giant-toad",
            "kraken", "remorhaz", "tarrasque",
        }
        for monster_id in proven:
            blockers = basic_blockers_2014(CORPUS[monster_id])
            assert "mechanic:swallow" not in blockers
        for monster_id in ("behir", "giant-frog", "giant-toad", "remorhaz"):
            assert basic_blockers_2014(CORPUS[monster_id]) == ()
        for monster_id in ("kraken", "tarrasque"):
            blockers = basic_blockers_2014(CORPUS[monster_id])
            assert "mechanic:swallow" not in blockers
            assert blockers  # Unrelated printed mechanics still fail closed.
    except Exception:
        logger.exception("Full 2014 Swallow source scan regression failed.")
        raise
