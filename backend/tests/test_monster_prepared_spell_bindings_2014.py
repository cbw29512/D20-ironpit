"""2014 prepared-spell source and browser-card parity regressions."""
from __future__ import annotations
import logging
import pytest
from app.content.monster_source_2014 import load_monster_source_2014
from app.content.monster_prepared_spell_bindings_2014 import bind_prepared_spells_2014
from app.content.monster_spell_slot_resources_2014 import monster_spell_slot_resources_2014
from app.content.monster_capabilities_2014 import load_2014_mvp_definitions
from app.content.capability_compiler import compile_combatant
from app.domain.capabilities import CombatantDefinition
from scripts.browser_template_serializer import template_row

logger = logging.getLogger(__name__)

def mage_subset(*ids):
    mage = next(m for m in load_monster_source_2014() if m.name == "Mage")
    source = mage.spellcasting
    assert source is not None
    spells = [s for s in source["spells"] if s["id"] in ids]
    assert {s["id"] for s in spells} == set(ids)
    return mage.model_copy(update={"spellcasting": {**source, "spells": spells}})

def test_prepared_spell_binding_and_browser_card():
    try:
        mage = mage_subset("fire-bolt", "magic-missile")
        before = mage.model_dump(mode="json")
        bound = bind_prepared_spells_2014(mage)
        assert [s.id for s in bound.attacks] == ["fire-bolt"]
        assert [s.id for s in bound.auto_hits] == ["magic-missile"]
        assert bound.attacks[0].attack_bonus == mage.spellcasting["attack_bonus"]
        assert mage.model_dump(mode="json") == before
        base = load_2014_mvp_definitions()["2014-goblin"]
        definition = CombatantDefinition.model_validate({
            **base.model_dump(mode="json"),
            "spell_attack_actions": [s.model_dump(mode="json") for s in bound.attacks],
            "auto_hit_spell_actions": [s.model_dump(mode="json") for s in bound.auto_hits],
            "resources": [r.model_dump(mode="json") for r in monster_spell_slot_resources_2014(mage)],
        })
        browser = template_row(compile_combatant(definition))
        assert browser["spell_attack_actions"][0]["attackBonus"] == mage.spellcasting["attack_bonus"]
        assert browser["auto_hit_spell_actions"][0]["projectileCount"] == 3
    except Exception:
        logger.exception("Prepared spell binding/browser export failed")
        raise

def test_prepared_spell_binding_fails_closed_on_unbound_spell():
    try:
        mage = mage_subset("magic-missile")
        specimen = mage.model_copy(update={"spellcasting": {
            **mage.spellcasting, "spells": [{"id": "light", "level": 0}],
        }})
        with pytest.raises(ValueError, match="unbound"):
            bind_prepared_spells_2014(specimen)
    except Exception:
        logger.exception("Prepared spell fail-closed test failed")
        raise


def test_prepared_spell_shared_attack_and_defense_bindings_serialize():
    """A synthetic 2014 source uses exactly the same primitives as pregens."""
    try:
        mage = mage_subset("magic-missile")
        prepared = [
            {"id": "shocking-grasp", "level": 0},
            {"id": "inflict-wounds", "level": 1},
            {"id": "bless", "level": 1},
            {"id": "shield-of-faith", "level": 1},
            {"id": "sanctuary", "level": 1},
            {"id": "false-life", "level": 1},
            {"id": "aid", "level": 2},
            {"id": "beacon-of-hope", "level": 3},
            {"id": "death-ward", "level": 4},
        ]
        specimen = mage.model_copy(update={"spellcasting": {
            **mage.spellcasting, "spells": prepared,
        }})
        immutable_before = specimen.model_dump(mode="json")
        bound = bind_prepared_spells_2014(specimen)
        assert {action.id for action in bound.attacks} == {"shocking-grasp", "inflict-wounds"}
        assert {action.id for action in bound.defenses} == {row["id"] for row in prepared[2:]}
        assert next(action for action in bound.defenses if action.id == "sanctuary").modifier_effects[0].save_dc == mage.spellcasting["save_dc"]
        assert specimen.model_dump(mode="json") == immutable_before
        base = load_2014_mvp_definitions()["2014-goblin"]
        definition = CombatantDefinition.model_validate({
            **base.model_dump(mode="json"),
            "spell_attack_actions": [action.model_dump(mode="json") for action in bound.attacks],
            "defensive_spell_actions": [action.model_dump(mode="json") for action in bound.defenses],
            "resources": [row.model_dump(mode="json") for row in monster_spell_slot_resources_2014(specimen)],
        })
        browser = template_row(compile_combatant(definition))
        assert {action["id"] for action in browser["spell_attack_actions"]} == {"shocking-grasp", "inflict-wounds"}
        assert {action["id"] for action in browser["defensive_spell_actions"]} == {row["id"] for row in prepared[2:]}
        assert next(action for action in browser["defensive_spell_actions"] if action["id"] == "shield-of-faith")["actionCost"] == "bonus_action"
    except Exception:
        logger.exception("Shared prepared spell attack/defense browser parity failed")
        raise


def test_prepared_defensive_spell_wrong_source_level_fails_closed():
    try:
        mage = mage_subset("magic-missile")
        specimen = mage.model_copy(update={"spellcasting": {
            **mage.spellcasting, "spells": [{"id": "bless", "level": 2}],
        }})
        with pytest.raises(ValueError, match="mismatches source"):
            bind_prepared_spells_2014(specimen)
    except Exception:
        logger.exception("Prepared defensive spell source-level validation failed")
        raise
