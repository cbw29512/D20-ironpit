"""Source-pinned 2014 finisher and named-action Invisible expiry."""
from __future__ import annotations

import logging

import pytest

from app.content.monster_basic_candidates_2014 import basic_blockers_2014
from app.content.monster_source_2014 import load_monster_source_2014
from app.content.monster_source_invisibility_2014 import source_invisibility_action_2014
from app.content.monster_source_zero_hp_finisher_2014 import source_proven_zero_hp_finisher_2014

logger = logging.getLogger(__name__)


def _wisp():
    try:
        return next(m for m in load_monster_source_2014() if m.id == "will-o-wisp")
    except Exception:
        logger.exception("2014 Will-o'-Wisp pinned source was not found.")
        raise


def test_source_proven_families_and_admission():
    try:
        roster = load_monster_source_2014()
        matching = [
            source.id for source in roster
            if source_proven_zero_hp_finisher_2014(source)
        ]
        assert len(roster) == 327
        assert matching == ["will-o-wisp"]
        card = _wisp()
        original = card.model_dump_json()
        action, = source_proven_zero_hp_finisher_2014(card)
        assert action.id == "consume-life" and action.name == "Consume Life"
        assert action.action_cost == "bonus_action"
        assert action.requires_target_zero_hp_alive
        assert action.instant_death_on_failed_save
        assert action.target_scope == "all-other-creatures"
        assert action.magical_effect and action.requires_target_sight
        assert (action.dc, action.range_ft, action.heal_source_on_kill_dice_count,
                action.heal_source_on_kill_dice_size) == (10, 5, 3, 6)
        invisibility, = source_invisibility_action_2014(card)
        assert invisibility.id == "invisibility"
        assert invisibility.condition_ids == ["invisible"]
        assert invisibility.concentration and invisibility.magical_effect
        assert invisibility.ends_on_owner_attack
        assert invisibility.ends_on_owner_action_ids == ["consume-life"]
        assert not invisibility.ends_on_owner_spell_cast
        assert basic_blockers_2014(card) == ()
        assert card.model_dump_json() == original
        renamed = card.model_copy(update={"id": "synthetic-druid", "name": "Other Source"})
        assert source_proven_zero_hp_finisher_2014(renamed) == [action]
        assert source_invisibility_action_2014(renamed) == [invisibility]
    except Exception:
        logger.exception("2014 finisher/Invisible source proof failed.")
        raise


@pytest.mark.parametrize("old,new", [
    ("As a bonus action", "As an action"),
    ("within 5 feet", "within 20 feet"),
    ("has 0 hit points and is still alive", "has 1 hit point"),
    ("DC 10 Constitution", "DC 20 Wisdom"),
    ("or die.", "or become frightened."),
    ("regains 10 (3d6)", "regains 20 (4d8)"),
    ("hit points. </p>", "hit points. The target takes 1d6 force damage.</p>"),
])
def test_altered_printed_finisher_does_not_bind(old: str, new: str):
    try:
        card = _wisp()
        assert old in card.source_traits
        altered = card.model_copy(update={
            "source_traits": card.source_traits.replace(old, new),
        })
        assert not source_proven_zero_hp_finisher_2014(altered)
        assert "source:trait" in basic_blockers_2014(altered)
    except Exception:
        logger.exception("2014 finisher source mutation was not rejected.")
        raise


def test_invisibility_source_change_cannot_suppress_named_exit():
    try:
        card = _wisp()
        altered = card.model_copy(update={
            "source_actions": card.source_actions.replace(
                "or uses its Consume Life", "or casts a spell",
            ),
        })
        assert not source_invisibility_action_2014(altered)
        assert "source:extra-action" in basic_blockers_2014(altered)
    except Exception:
        logger.exception("2014 Invisible named-exit source drift not blocked.")
        raise
