"""Cross-caster 2014 Cleric spell reuse without a monster-specific resolver."""
from __future__ import annotations

import logging

import pytest

from app.content.monster_source_2014 import load_monster_source_2014
from app.content.monster_definition_adapter_2014 import adapt_basic_monster_2014
from app.content.monster_prepared_cleric_spells_2014 import (
    prepared_cleric_spell_actions_2014, merge_unique_spell_actions,
)
from app.content.monster_prepared_spells_2014 import supports_prepared_spellcasting_2014
from app.content.capability_compiler import compile_combatant

logger = logging.getLogger(__name__)


def _source(monster_id: str):
    try:
        return next(m for m in load_monster_source_2014() if m.id == monster_id)
    except Exception:
        logger.exception("2014 prepared caster source %s was not found.", monster_id)
        raise


def test_cult_fanatic_reuses_six_cleric_spell_entries_and_hold_person() -> None:
    try:
        card = _source("cult-fanatic")
        original = card.model_dump_json()
        package = prepared_cleric_spell_actions_2014(card)
        assert package.implemented_ids() == {
            "light", "sacred-flame", "thaumaturgy",
            "inflict-wounds", "shield-of-faith", "spiritual-weapon",
        }
        assert len(package.saves) == len(package.attacks) == 1
        assert package.saves[0].dc == 11
        assert package.attacks[0].attack_bonus == 3
        assert package.attacks[0].damage_dice_count == 3
        assert package.attacks[0].damage_dice_size == 10
        assert package.defenses[0].modifier_effects[0].flat_bonus == 2
        assert package.persistent_attacks[0].spatial_mode == "nonspatial"
        assert package.persistent_attacks[0].attack.attack_bonus == 3

        definition = adapt_basic_monster_2014(card)
        template = compile_combatant(definition)
        assert {"sacred-flame", "hold-person"} <= {
            x.id for x in template.spell_save_actions
        }
        assert "inflict-wounds" in {x.id for x in template.spell_attack_actions}
        assert "shield-of-faith" in {x.id for x in template.defensive_spell_actions}
        assert "spiritual-weapon" in {x.id for x in template.persistent_spell_attack_actions}
        assert all(a.id != "command" for a in template.spell_save_actions)
        assert supports_prepared_spellcasting_2014(card) is False
        assert card.model_dump_json() == original
    except Exception:
        logger.exception("2014 Cult Fanatic shared Cleric spell bindings failed.")
        raise


@pytest.mark.parametrize("monster_id", ["acolyte", "priest"])
def test_existing_admitted_clerics_keep_one_spell_action_per_id(monster_id: str) -> None:
    try:
        card = _source(monster_id)
        template = compile_combatant(adapt_basic_monster_2014(card))
        for group in (
            template.spell_save_actions,
            template.spell_attack_actions,
            template.defensive_spell_actions,
            template.persistent_spell_attack_actions,
        ):
            ids = [item.id for item in group]
            assert len(ids) == len(set(ids)), ids
        assert supports_prepared_spellcasting_2014(card)
    except Exception:
        logger.exception("Existing Cleric source regression: %s.", monster_id)
        raise


def test_malformed_source_prepared_cleric_spell_does_not_silently_bind() -> None:
    try:
        card = _source("cult-fanatic").model_copy(deep=True)
        for entry in card.spellcasting["spells"]:
            if entry.get("id") == "inflict-wounds":
                entry["level"] = 9
        with pytest.raises(ValueError, match="Source prepared spell"):
            prepared_cleric_spell_actions_2014(card)

        card = _source("cult-fanatic").model_copy(deep=True)
        card.spellcasting["source_complete"] = False
        assert prepared_cleric_spell_actions_2014(card).implemented_ids() == set()

        # Generic duplicate handling fails closed on conflicting outcomes.
        from app.content.cleric_2014_level1_spells import sacred_flame_2014
        first, changed = sacred_flame_2014(11, 4), sacred_flame_2014(12, 4)
        with pytest.raises(ValueError, match="Conflicting prepared spell"):
            merge_unique_spell_actions([first], [changed])
    except Exception:
        logger.exception("Malformed 2014 source spell did not fail closed.")
        raise
