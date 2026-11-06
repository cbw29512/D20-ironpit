"""Source-backed 2014 low-level Cleric: reuse ordinary spell engine."""
from __future__ import annotations

import logging

import pytest

from app.content.capability_compiler import compile_combatant
from app.content.monster_basic_candidates_2014 import basic_blockers_2014
from app.content.monster_definition_adapter_2014 import adapt_basic_monster_2014
from app.content.monster_prepared_spells_2014 import supports_prepared_spellcasting_2014
from app.content.monster_source_2014 import load_monster_source_2014
from app.content.monster_source_tier1_cleric_2014 import (
    source_proves_tier1_cleric_spells_2014,
)

logger = logging.getLogger(__name__)


def _card():
    try:
        return next(row for row in load_monster_source_2014() if row.id == "acolyte")
    except Exception:
        logger.exception("Pinned 2014 low-level Cleric source not found.")
        raise


def test_full_roster_and_compiled_spell_combat_uses_shared_builders():
    try:
        roster = load_monster_source_2014()
        assert len(roster) == 327
        assert [row.id for row in roster if source_proves_tier1_cleric_spells_2014(row)] == ["acolyte"]
        card = _card()
        before = card.model_dump_json()
        assert supports_prepared_spellcasting_2014(card)
        assert basic_blockers_2014(card) == ()
        definition = adapt_basic_monster_2014(card)
        template = compile_combatant(definition)
        assert [a.id for a in template.spell_save_actions] == ["sacred-flame"]
        assert {a.id for a in template.defensive_spell_actions} == {"bless", "sanctuary"}
        assert [a.id for a in template.healing_actions] == ["cure-wounds"]
        assert (template.spell_save_actions[0].dc, template.spell_save_actions[0].level) == (12, 0)
        assert next(a for a in template.healing_actions if a.id == "cure-wounds").healing_bonus == 2
        assert next(a for a in template.defensive_spell_actions if a.id == "sanctuary").modifier_effects[0].save_dc == 12
        assert {r.id: r.max_uses for r in template.resources}["spell-slot-1"] == 3
        assert card.model_dump_json() == before
    except Exception:
        logger.exception("Source to shared Cleric spell pipeline failed.")
        raise


@pytest.mark.parametrize("original,changed", [
    ("DC 12", "DC 13"),
    ("+4 to hit with spell attacks", "+5 to hit with spell attacks"),
    ("1st-level spellcaster", "2nd-level spellcaster"),
    ("1st level (3 slots)", "1st level (4 slots)"),
    ("sacred flame, thaumaturgy", "ray of frost, thaumaturgy"),
    ("bless, cure wounds, sanctuary", "bless, cure wounds, fireball"),
])
def test_printed_source_mutations_are_not_silently_admitted(original, changed):
    try:
        card = _card()
        assert original in card.source_traits
        altered = card.model_copy(update={
            "source_traits": card.source_traits.replace(original, changed)
        })
        assert not source_proves_tier1_cleric_spells_2014(altered)
        assert "mechanic:spellcasting" in basic_blockers_2014(altered)
        with pytest.raises(ValueError, match="not a basic"):
            adapt_basic_monster_2014(altered)
    except Exception:
        logger.exception("Low-level Cleric mutated source was not rejected.")
        raise


def test_structured_spell_mutation_and_unheaded_hidden_rider_fail_closed():
    try:
        card = _card()
        altered = card.model_copy(update={
            "spellcasting": {**card.spellcasting, "spells": [
                *card.spellcasting["spells"][:-1],
                {"id": "fireball", "name": "fireball", "level": 3},
            ]},
        })
        assert not source_proves_tier1_cleric_spells_2014(altered)
        assert "mechanic:spellcasting" in basic_blockers_2014(altered)
        hidden = card.model_copy(update={
            "source_traits": card.source_traits + "<p>Its spells deal extra damage.</p>",
        })
        assert not source_proves_tier1_cleric_spells_2014(hidden)
    except Exception:
        logger.exception("Tier-1 Cleric printed/structured mutation guard failed.")
        raise


def test_renamed_source_is_mechanically_equivalent():
    try:
        card = _card()
        renamed = card.model_copy(update={
            "id": "unrelated-cleric",
            "name": "Unrelated Cleric",
            "source_traits": card.source_traits.replace("acolyte", "Unrelated Cleric"),
        })
        assert source_proves_tier1_cleric_spells_2014(renamed)
        assert supports_prepared_spellcasting_2014(renamed)
        assert basic_blockers_2014(renamed) == ()
    except Exception:
        logger.exception("Cleric source binding wrongly depends on monster identity.")
        raise
