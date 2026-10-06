from __future__ import annotations

import logging

from app.content.capability_compiler import compile_combatant
from app.content.monster_basic_candidates_2014 import basic_blockers_2014
from app.content.monster_definition_adapter_2014 import adapt_basic_monster_2014
from app.content.monster_source_2014 import load_monster_source_2014

logger = logging.getLogger(__name__)


def _scout():
    try:
        return next(item for item in load_monster_source_2014() if item.id == "scout")
    except Exception:
        logger.exception("Failed to load the pinned 2014 Scout source row.")
        raise


def test_scout_range_correction_preserves_source_and_reuses_flexible_multiattack() -> None:
    try:
        source = _scout()
        before = source.model_dump()
        longbow = next(item for item in source.attacks if item.id == "longbow")
        assert longbow.kind == "ranged"
        assert longbow.name == "Longbow"

        assert basic_blockers_2014(source) == ()
        runtime = compile_combatant(adapt_basic_monster_2014(source))

        attacks = [runtime.weapon_attack, *runtime.alternate_weapon_attacks]
        ranged = next(item for item in attacks if item.id == "2014-scout-longbow")
        melee = next(item for item in attacks if item.id == "2014-scout-shortsword")
        assert ranged.weapon.normal_range_ft == 150
        assert ranged.weapon.long_range_ft == 600
        assert runtime.attack_action is not None
        assert len(runtime.attack_action.slots) == 2
        assert all(set(slot.attack_ids) == {ranged.id, melee.id}
                   for slot in runtime.attack_action.slots)
        assert runtime.attack_action.is_attack_action is False
        assert source.model_dump() == before
    except Exception:
        logger.exception("2014 Scout source-range correction certification failed.")
        raise
