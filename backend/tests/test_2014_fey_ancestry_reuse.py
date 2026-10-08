"""2014 Drow/Drider Fey Ancestry reuses universal tagged save Advantage."""
from __future__ import annotations

import logging

from app.content.monster_passive_grants_2014 import (
    bound_passive_trait_names_2014,
    saving_throw_advantage_grants_2014,
)
from app.content.monster_source_2014 import load_monster_source_2014

logger = logging.getLogger(__name__)


def test_fey_ancestry_is_source_tagged_charm_save_advantage() -> None:
    try:
        sources = {item.id: item for item in load_monster_source_2014()}
        for monster_id in ("drow", "drider"):
            monster = sources[monster_id]
            assert "Fey Ancestry" in monster.trait_names
            assert "Fey Ancestry" in bound_passive_trait_names_2014(monster)
            grants = [
                grant for grant in saving_throw_advantage_grants_2014(monster)
                if grant.source_name == "Fey Ancestry"
            ]
            assert len(grants) == 1
            assert grants[0].required_effect_tags == ["charm"]
            assert set(grants[0].abilities) == {
                "strength", "dexterity", "constitution",
                "intelligence", "wisdom", "charisma",
            }
            assert grants[0].requires_magical_effect is False
    except Exception:
        logger.exception("2014 Fey Ancestry source binding certification failed")
        raise
