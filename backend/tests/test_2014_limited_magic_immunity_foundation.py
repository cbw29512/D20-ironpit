"""Foundation tests for 2014 Rakshasa Limited Magic Immunity advantage binding."""
from __future__ import annotations

import logging

from app.content.monster_source_2014 import load_monster_source_2014
from app.content.monster_passive_grants_2014 import saving_throw_advantage_grants_2014

logger = logging.getLogger(__name__)


def test_rakshasa_limited_magic_immunity_binds_save_advantage() -> None:
    """Source-verified advantage on saves vs other spells/magical effects reuses existing grant."""
    try:
        monster = load_monster_source_2014("rakshasa")
        assert "Limited Magic Immunity" in monster.trait_names
        grants = saving_throw_advantage_grants_2014(monster)
        matching = [g for g in grants if g.source_id == "limited-magic-immunity"]
        assert len(matching) == 1
        grant = matching[0]
        assert grant.source_name == "Limited Magic Immunity"
        assert grant.requires_magical_effect
        assert set(grant.abilities) == {"strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"}
    except Exception:
        logger.exception("Limited Magic Immunity foundation test failed.")
        raise
