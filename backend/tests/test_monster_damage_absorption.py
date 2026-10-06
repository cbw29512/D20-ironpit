import logging
from pathlib import Path
import sys

import pytest

# CI runs from backend/; serializers are repository-level build tools.
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.combat.damage_defenses import resolve_damage_amount
from app.combat.state import build_combatant_state
from app.content.demo import build_demo_fighter
from app.content.capability_compiler import compile_combatant
from app.content.capability_from_template import definition_from_template
from app.content.monster_catalog import load_monster_rows
from app.content.monster_conditional_damage_defenses_2014 import template_defense_fields_2014
from app.content.monster_damage_absorption import damage_absorptions_2024, damage_absorptions_from_source
from app.content.monster_source_2014 import load_monster_source_2014
from app.content.monster_trait_bindings_2014 import bound_trait_names_2014
from app.content.monster_trait_bindings_2024 import bind_monster_source_traits_2024
from app.content.monster_trait_source_audit import trait_issues
from scripts.browser_template_serializer import template_row

logger = logging.getLogger(__name__)
EXPECTED = {
    "Clay Golem": ("Acid Absorption", "acid"),
    "Flesh Golem": ("Lightning Absorption", "lightning"),
    "Iron Golem": ("Fire Absorption", "fire"),
    "Shambling Mound": ("Lightning Absorption", "lightning"),
}


@pytest.mark.parametrize("edition", ["2014", "2024"])
@pytest.mark.parametrize("name", EXPECTED)
def test_paired_source_bindings_heal_through_shared_engine(edition, name):
    try:
        source_name, damage_type = EXPECTED[name]
        # This harness exercises a single trait; it never certifies a partial monster.
        template = build_demo_fighter().model_copy(update={"name": name, "kind": "monster", "ruleset": edition})
        if edition == "2014":
            source = next(item for item in load_monster_source_2014() if item.name == name)
            fields = template_defense_fields_2014(source)
            assert source_name in bound_trait_names_2014(source)
            # Source fields are constructor input: validate strings into typed enums.
            template = type(template).model_validate({**template.model_dump(), **fields})
        else:
            row = next(item for item in load_monster_rows() if item["name"] == name)
            template = bind_monster_source_traits_2024(template)
            assert not any("absorption" in issue for issue in trait_issues(template, row))
            missing = template.model_copy(update={"damage_absorptions": []})
            assert "trait-runtime-mismatch:damage-absorption" in trait_issues(missing, row)
        assert len(template.damage_absorptions) == 1
        rule = template.damage_absorptions[0]
        assert (rule.source_name, rule.damage_type.value) == (source_name, damage_type)
        assert compile_combatant(definition_from_template(template)).damage_absorptions == [rule]
        # Serialization proves the browser receives this edition's own source data.
        serialized = template_row(template)["damage_absorptions"][0]
        assert serialized == {"sourceId": rule.source_id, "sourceName": source_name, "damageType": damage_type}
        state = build_combatant_state(template)
        state.current_hp = template.max_hp - 7
        assert resolve_damage_amount(5, rule.damage_type, state) == (0, 5, source_name)
        assert state.current_hp == template.max_hp - 2
        assert build_combatant_state(template).current_hp == template.max_hp
    except Exception:
        logger.exception("Paired absorption binding failed for %s %s.", edition, name)
        raise


def test_all_657_source_entries_are_scanned_without_creature_name_dispatch():
    try:
        old = {m.name for m in load_monster_source_2014() if template_defense_fields_2014(m)["damage_absorptions"]}
        new = {row["name"] for row in load_monster_rows() if damage_absorptions_2024(row)}
        assert old == new == set(EXPECTED)
        renamed = "Thermal Gift. Whenever the construct is subjected to fire damage, it takes no damage and instead regains a number of hit points equal to the fire damage dealt."
        rule = damage_absorptions_from_source(renamed, set())[0]
        assert (rule.source_name, rule.damage_type.value) == ("Thermal Gift", "fire")
    except Exception:
        logger.exception("Full paired absorption source scan failed.")
        raise


def test_healing_only_payload_needs_printed_immunity_and_malformed_traits_fail_closed():
    try:
        text = "Fire Absorption. Whenever the construct is subjected to fire damage, it regains a number of hit points equal to the fire damage dealt."
        with pytest.raises(ValueError, match="printed damage prevention or Immunity"):
            damage_absorptions_from_source(text, set())
        assert damage_absorptions_from_source(text, {"fire"})[0].damage_type.value == "fire"
        with pytest.raises(ValueError, match="unsupported source payload"):
            damage_absorptions_from_source("Fire Absorption. Reduces Fire damage by 5.", {"fire"})
    except Exception:
        logger.exception("Absorption fail-closed source checks failed.")
        raise
