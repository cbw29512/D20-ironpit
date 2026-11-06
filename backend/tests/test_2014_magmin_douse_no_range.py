"""Source-prove Magmin Touch douse has no printed range; universal action ends burning."""
from __future__ import annotations

import logging

from app.content.monster_source_2014 import load_monster_source_2014
from app.combat.douse_burning import douse_burning
from app.domain.timed_effects import TimedEffect

logger = logging.getLogger(__name__)


def test_magmin_touch_source_has_no_douse_range():
    try:
        magmin = next(c for c in load_monster_source_2014() if c.id == "magmin")
        section = magmin.source_actions
        assert "until a creature takes an action to douse the fire" in section.lower()
        assert "adjacent" not in section.lower() and "reach" not in section.lower().split("douse")[-1]
        assert "flammable object" in section
    except Exception:
        logger.exception("Magmin douse source proof failed")
        raise


def test_douse_removes_burning_effect():
    try:
        class Fake:
            timed_effects = []
            active_effect_ids = []
            id = "t"
        target = Fake()
        target.timed_effects.append(TimedEffect(
            effect_id="burning", source_id="m", source_effect_id="touch",
            source_name="Touch",
        ))
        target.active_effect_ids.append("burning")
        events = douse_burning(target, "actor", 1)
        assert not target.timed_effects
        assert "burning" not in target.active_effect_ids
        assert len(events) == 1
    except Exception:
        logger.exception("Douse primitive failed")
        raise
