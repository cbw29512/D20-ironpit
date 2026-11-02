"""Source-verified binding of 2014 Duergar Resilience to shared save-Advantage grants."""
from __future__ import annotations

import logging
import pytest

from app.content.monster_source_2014 import load_monster_source_2014
from app.content.monster_passive_grants_2014 import saving_throw_advantage_grants_2014

logger = logging.getLogger(__name__)


def test_duergar_resilience_binds_shared_grants():
    try:
        monster = next(m for m in load_monster_source_2014() if m.id == "duergar")
        grants = saving_throw_advantage_grants_2014(monster)
        sources = {g.source_name for g in grants}
        assert "Duergar Resilience" in sources
        tags = set()
        for g in grants:
            if g.source_name == "Duergar Resilience" and g.required_effect_tags:
                tags.update(g.required_effect_tags)
        assert {"poison", "charm", "paralyzed"} <= tags
        magical = [g for g in grants if g.source_id == "duergar-resilience-magical"]
        assert len(magical) == 1
        assert magical[0].requires_magical_effect
    except Exception:
        logger.exception("Duergar Resilience binding failed")
        raise


def test_duergar_resilience_fails_closed_on_mutation():
    try:
        monster = next(m for m in load_monster_source_2014() if m.id == "duergar")
        original = monster.source_traits
        monster.source_traits = (original or "").replace("advantage", "disadvantage")
        with pytest.raises(ValueError, match="mutated"):
            saving_throw_advantage_grants_2014(monster)
        monster.source_traits = original
    except Exception:
        logger.exception("Fail-closed mutation test failed")
        raise
