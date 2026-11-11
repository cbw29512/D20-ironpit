"""Ghost's printed visual fear reuses the generic save/Frightened lifecycle."""
from __future__ import annotations

import logging

from app.content.monster_basic_candidates_2014 import basic_blockers_2014
from app.content.monster_save_capabilities_2014 import save_capabilities_2014
from app.content.monster_source_2014 import load_monster_source_2014
from app.content.monster_source_visual_save_bindings_2014 import source_proven_visual_saves_2014
from app.content.capability_compiler import _compile_save
from scripts.browser_template_serializer import _save

logger = logging.getLogger(__name__)


def _ghost():
    try:
        monsters = load_monster_source_2014()
        assert len(monsters) == 327
        return next(monster for monster in monsters if monster.id == "ghost")
    except Exception:
        logger.exception("Could not find source Ghost")
        raise


def test_ghost_uses_shared_fear_saves_and_browser_schema():
    try:
        monster = _ghost()
        original = monster.model_dump_json()
        (definition,) = source_proven_visual_saves_2014(monster)
        assert (definition.name, definition.dc, definition.save_ability) == (
            "Horrifying Visage", 13, "wisdom",
        )
        assert definition.area.shape == "emanation"
        assert definition.area.radius_ft == 60
        assert definition.excluded_target_creature_types == ["undead"]
        assert definition.requires_target_to_see_source
        assert definition.source_effect_immunity_on_success
        timed = definition.failed_save_timed_effect
        assert timed.effect_id == "frightened"
        assert timed.duration_rounds == 10
        assert timed.repeat_save_timing == "target_turn_end"
        assert timed.repeat_save_disadvantage_while_source_visible is False
        assert timed.source_effect_immunity_on_end
        runtime = _compile_save(definition)
        browser = _save(runtime)
        assert browser["name"] == "Horrifying Visage"
        assert browser["failedSaveTimedEffect"]["effectId"] == "frightened"
        assert any(action.name == "Horrifying Visage" for action in save_capabilities_2014(monster))
        # Ghost Possession remains unbound and Recharge is unresolved.
        assert "source:extra-action" in basic_blockers_2014(monster)
        assert "mechanic:recharge" in basic_blockers_2014(monster)
        assert monster.model_dump_json() == original
    except Exception:
        logger.exception("Ghost visual fear compilation failed")
        raise


def test_ghost_extra_aging_and_fear_clauses_are_source_exact():
    try:
        monster = _ghost()
        for old, new in (
            ("fails by 5 or more", "fails by 3 or more"),
            ("1d4 × 10 years", "2d4 × 10 years"),
            ("ending the frightened condition on itself", "ending the paralysis on itself"),
            ("within 24 hours of it occurring", "within 12 hours of it occurring"),
            ("immunity to this ghost's Horrifying Visage", "immunity to fear"),
        ):
            assert old in monster.source_actions
            altered = monster.model_copy(update={
                "source_actions": monster.source_actions.replace(old, new),
            })
            assert source_proven_visual_saves_2014(altered) == []
        # Source-defined numeric DC is allowed to vary: all runtime copies
        # must use the new parameter rather than hard-code the Ghost's 13.
        raised_dc = monster.model_copy(update={
            "source_actions": monster.source_actions.replace("DC 13 Wisdom", "DC 18 Wisdom"),
        })
        (scaled,) = source_proven_visual_saves_2014(raised_dc)
        assert scaled.dc == 18
        assert scaled.failed_save_timed_effect.repeat_save_dc == 18
        renamed = monster.model_copy(update={"id": "synthetic-visual-fear", "name": "Other"})
        assert len(source_proven_visual_saves_2014(renamed)) == 1
    except Exception:
        logger.exception("Ghost source mutation proof failed")
        raise
