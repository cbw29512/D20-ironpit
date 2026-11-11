"""2014 destructible wall source audit; no combat admission claimed."""
from __future__ import annotations

import logging

from app.content.monster_source_2014 import load_monster_source_2014
from app.content.monster_source_barrier_2014 import source_barrier_parameters_2014
from app.content.monster_basic_candidates_2014 import monster_blockers_2014

logger = logging.getLogger(__name__)


def test_printed_barrier_is_exact_unique_and_mutation_safe() -> None:
    try:
        cards = {card.id: card for card in load_monster_source_2014()}
        assert len(cards) == 327
        matched = {
            card.id: source_barrier_parameters_2014(card)
            for card in cards.values()
            if source_barrier_parameters_2014(card) is not None
        }
        assert set(matched) == {"ice-devil"}
        source = cards["ice-devil"]
        immutable = source.model_dump_json()
        parameters = matched["ice-devil"]
        assert parameters.action_id == "wall-of-ice"
        assert parameters.recharge_minimum == 6
        assert (parameters.section_ac, parameters.section_hp) == (5, 30)
        assert parameters.damage_immunities == (
            "acid", "cold", "necrotic", "poison", "psychic",
        )
        assert (parameters.creation_save_dc, parameters.creation_damage_dice) == (17, "10d6")
        assert (
            parameters.cross_destroyed_section_dc,
            parameters.cross_destroyed_section_damage_dice,
        ) == (17, "5d6")
        assert source.model_dump_json() == immutable
        renamed = source.model_copy(update={"id": "renamed-wall-owner", "name": "Renamed Owner"})
        assert source_barrier_parameters_2014(renamed) == parameters
        for before, after in (
            ("30 hit points", "40 hit points"),
            ("17 Constitution", "16 Constitution"),
            ("the rest of the wall vanishes", "the next round begins"),
        ):
            altered = source.model_copy(update={
                "source_actions": source.source_actions.replace(before, after),
            })
            assert altered.source_actions != source.source_actions
            assert source_barrier_parameters_2014(altered) is None
        assert any(
            blocker in monster_blockers_2014(source)
            for blocker in ("mechanic:recharge", "source:extra-action")
        )
    except Exception:
        logger.exception("2014 source barrier proof failed.")
        raise
