"""Quasit 2014 Scare uses source-driven shared Frightened control."""
from __future__ import annotations
import logging
import pytest
from app.content.monster_source_scare_2014 import source_scare_2014
from app.content.monster_source_2014 import load_monster_source_2014
from app.content.monster_basic_candidates_2014 import basic_blockers_2014
logger = logging.getLogger(__name__)

def _quasit():
    try:
        return next(row for row in load_monster_source_2014() if row.id == "quasit")
    except Exception:
        logger.exception("Pinned Quasit card missing")
        raise

def test_scare_uses_generic_save_and_repeat_disadvantage():
    try:
        source = _quasit()
        action, = source_scare_2014(source)
        assert action.name == "Scare" and action.dc == 10 and action.range_ft == 20
        assert action.resource_id == "scare"
        effect = action.failed_save_timed_effect
        assert effect.effect_id == "frightened" and effect.duration_rounds == 10
        assert effect.repeat_save_ability == "wisdom" and effect.repeat_save_dc == 10
        assert effect.repeat_save_timing == "target_turn_end"
        assert effect.repeat_save_disadvantage_while_source_visible
    except Exception:
        logger.exception("Quasit Scare generic binding failed")
        raise

@pytest.mark.parametrize("old,new", [
    ("DC 10 Wisdom", "DC 11 Wisdom"),
    ("within 20 feet", "within 30 feet"),
    ("with disadvantage if the quasit is within line of sight", "with advantage if the quasit is within line of sight"),
])
def test_modified_printed_scare_fails_closed(old, new):
    try:
        source = _quasit()
        assert old in source.source_actions
        altered = source.model_copy(update={"source_actions": source.source_actions.replace(old, new)})
        if "DC 10" in old or "within 20" in old:
            # Numeric card parameters are source-derived and therefore legal.
            action, = source_scare_2014(altered)
            assert action.dc != 10 or action.range_ft != 20
        else:
            assert not source_scare_2014(altered)
    except Exception:
        logger.exception("Quasit Scare source mutation verification failed")
        raise
