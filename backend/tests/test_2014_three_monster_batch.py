"""Batch certification: independent 2014 source mechanics admit three monsters."""
from __future__ import annotations

import logging

from app.content.monster_basic_candidates_2014 import basic_blockers_2014
from app.content.monster_roster_2014 import build_basic_2014_monsters
from app.content.monster_source_2014 import load_monster_source_2014

logger = logging.getLogger(__name__)


def test_sea_hag_hydra_and_clay_golem_compile_into_one_roster():
    try:
        source = {card.id: card for card in load_monster_source_2014()}
        expected = {"sea-hag", "hydra", "clay-golem"}
        for monster_id in expected:
            assert basic_blockers_2014(source[monster_id]) == ()
        templates = build_basic_2014_monsters()
        names = {template.id for template in templates}
        assert len(names) == len(templates) == 246
        assert {f"2014-{monster_id}" for monster_id in expected} <= names
        actual = {template.id: template for template in templates}
        hydra = actual["2014-hydra"]
        assert hydra.variable_heads is not None
        assert hydra.variable_heads.initial_heads == 5
        assert hydra.variable_heads.sever_damage_threshold == 25
        assert hydra.variable_heads.regrowth_blocking_damage_types == ["fire"]
        hag = actual["2014-sea-hag"]
        assert hag.visual_disguise_action is not None
        assert hag.visual_disguise_action.inspection_dc == 16
        assert hag.visual_turn_start_rule is not None
        assert hag.visual_turn_start_rule.source_name == "Horrific Appearance"
        clay = actual["2014-clay-golem"]
        assert any(action.id == "haste" for action in clay.timed_self_buff_actions)
        assert any(grant.required_active_effect_id == "haste"
                   for grant in clay.bonus_attack_grants)
        assert all(item.ruleset == "2014" for item in templates)
    except Exception:
        logger.exception("Combined 2014 monster admission regression failed.")
        raise
