"""Light is printed reference metadata, not a standard Iron Pit combat Action.

The weapon Light property and genuine Darkness/Fog Cloud mechanics are distinct.
"""
from __future__ import annotations

import logging

import pytest

from app.content.canonical_cleric_spells import CLERIC_CANTRIPS
from app.content.capability_compiler import compile_combatant
from app.content.cleric_2014_spell_package import _CANTRIPS as CLERIC_2014_CANTRIPS
from app.content.monster_definition_adapter_2014 import adapt_monster_mechanics_2014
from app.content.monster_source_2014 import load_monster_source_2014
from app.content.wizard_2024_spell_package import _cantrips as wizard_2024_cantrips

logger = logging.getLogger(__name__)


@pytest.mark.parametrize("monster_id", ["acolyte", "cloud-giant", "storm-giant"])
def test_printed_2014_light_is_not_an_executable_combat_spell(monster_id):
    try:
        # Keep source cards immutable and distinguish a printed choice from
        # a compiled combat Action. Even blocked monsters can be inspected.
        source = next(m for m in load_monster_source_2014() if m.id == monster_id)
        before = source.model_dump_json()
        spells = (
            source.spellcasting.get("spells", []) if isinstance(source.spellcasting, dict)
            else source.innate_spellcasting.get("spells", [])
        )
        assert any(row.get("id") == "light" for row in spells)
        template = compile_combatant(adapt_monster_mechanics_2014(source))

        # Every chosen combat spell belongs to one existing universal Action
        # family. Light must never consume a slot or create an active effect.
        action_groups = (
            template.spell_save_actions,
            template.spell_attack_actions,
            template.auto_hit_spell_actions,
            template.defensive_spell_actions,
            template.timed_self_buff_actions,
            template.suppression_zone_actions,
            template.persistent_save_zone_actions,
        )
        assert "light" not in {action.id for group in action_groups for action in group}
        assert "light" not in {resource.id for resource in template.resources}
        assert source.model_dump_json() == before
    except Exception:
        logger.exception("Light arena-neutral source/card regression: %s", monster_id)
        raise


def test_2014_and_2024_character_light_remains_outside_arena():
    try:
        # This checks separately authored pregen spell choices and guards
        # against making Light an executable precombat buff in another edition.
        groups = (CLERIC_CANTRIPS, CLERIC_2014_CANTRIPS, wizard_2024_cantrips(4))
        for group in groups:
            found = [choice for choice in group if choice.id == "light"]
            assert len(found) == 1
            assert found[0].required_capabilities == ["arena-out-of-scope"]
    except Exception:
        logger.exception("Light pregen edition policy check failed.")
        raise


def test_light_exclusion_does_not_erase_real_obscuration_spells():
    try:
        sources = {item.id: item for item in load_monster_source_2014()}
        for monster_id, spell_id in (("drow", "darkness"), ("cloud-giant", "fog-cloud")):
            template = compile_combatant(adapt_monster_mechanics_2014(sources[monster_id]))
            assert any(action.id == spell_id for action in template.suppression_zone_actions)
    except Exception:
        logger.exception("Light policy accidentally altered active obscuration.")
        raise
