"""2014 Fog Cloud: source-complete typed zone, no spell-name combat dispatch."""
from __future__ import annotations

import logging

import pytest

from app.content.capability_compiler import compile_combatant
from app.content.monster_basic_candidates_2014 import basic_blockers_2014
from app.content.monster_definition_adapter_2014 import adapt_monster_mechanics_2014
from app.content.monster_innate_fog_cloud_2014 import source_proven_innate_fog_cloud_2014
from app.content.monster_innate_support_2014 import (
    innate_spell_resources_2014, supports_innate_spellcasting_2014,
)
from app.content.monster_source_2014 import load_monster_source_2014
from scripts.browser_template_serializer import _suppression_zone

logger = logging.getLogger(__name__)


@pytest.mark.parametrize("monster_id,uses", [("ice-mephit", 1), ("cloud-giant", None)])
def test_fog_cloud_compiles_without_monster_specific_combat_mechanics(monster_id, uses):
    try:
        monster = next(item for item in load_monster_source_2014() if item.id == monster_id)
        before = monster.model_dump_json()
        (action,) = source_proven_innate_fog_cloud_2014(monster)
        assert (action.id, action.name, action.level) == ("fog-cloud", "Fog Cloud", 1)
        assert (action.cast_range_ft, action.radius_ft, action.duration_rounds) == (120, 20, 600)
        assert action.obscuration_kind == "heavy-physical" and action.concentration
        assert not (action.deafens or action.blocks_verbal_spells
                    or action.thunder_immunity or action.expends_spell_slot)
        assert action.resource_id == ("fog-cloud" if uses else None)
        resources = {r.id: r.max_uses for r in innate_spell_resources_2014(monster)}
        assert resources.get("fog-cloud") == uses
        template = compile_combatant(adapt_monster_mechanics_2014(monster))
        assert _suppression_zone(template.suppression_zone_actions[0])["obscurationKind"] == "heavy-physical"
        assert monster.model_dump_json() == before
        renamed = monster.model_copy(update={"id": "neutral-source", "name": "Neutral"})
        assert source_proven_innate_fog_cloud_2014(renamed) == [action]
        if monster_id == "ice-mephit":
            assert supports_innate_spellcasting_2014(monster)
            assert basic_blockers_2014(monster) == ()
        else:
            # Cloud Giant has additional unbound innate spells: do not certify it.
            assert not supports_innate_spellcasting_2014(monster)
    except Exception:
        logger.exception("Fog Cloud immutable source check failed: %s", monster_id)
        raise


@pytest.mark.parametrize("monster_id", ["ice-mephit", "cloud-giant"])
def test_fog_cloud_missing_or_changed_source_fails_closed(monster_id):
    try:
        monster = next(item for item in load_monster_source_2014() if item.id == monster_id)
        assert source_proven_innate_fog_cloud_2014(monster)
        assert "fog cloud" in monster.source_traits.casefold()
        altered = monster.model_copy(update={
            "source_traits": monster.source_traits.replace("fog cloud", "fireball"),
        })
        assert source_proven_innate_fog_cloud_2014(altered) == []
        changed = monster.model_copy(deep=True)
        changed.innate_spellcasting["spells"][0]["uses_per_day"] = 19
        assert source_proven_innate_fog_cloud_2014(changed) == []
        missing = monster.model_copy(update={"source_traits": None})
        assert source_proven_innate_fog_cloud_2014(missing) == []
    except Exception:
        logger.exception("Fog Cloud mutation guard failed: %s", monster_id)
        raise
