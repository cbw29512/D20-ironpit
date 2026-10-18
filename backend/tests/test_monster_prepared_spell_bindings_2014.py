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
