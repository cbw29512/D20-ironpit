"""Command is a printed spell binding, not a new creature-specific mechanic."""
from __future__ import annotations

import logging
import re

import pytest

from app.combat.spell_policy import spell_at_slot
from app.combat.spell_target_counts import spell_save_target_count
from app.content.monster_command_spell_2014 import (
    command_grovel_2014, prepared_command_spell_actions_2014,
)
from app.content.monster_definition_adapter_2014 import adapt_monster_mechanics_2014
from app.content.monster_source_2014 import load_monster_source_2014
from scripts.browser_template_serializer import _spell

logger = logging.getLogger(__name__)
_EXPECTED = {
    "androsphinx": 18, "cult-fanatic": 11,
    "guardian-naga": 16, "mummy-lord": 17,
}


def test_source_complete_command_casters_use_the_same_shared_spell() -> None:
    try:
        cards = load_monster_source_2014()
        assert len(cards) == 327
        sources = {card.id: card for card in cards}
        actual = {
            card.id for card in cards
            if isinstance(card.spellcasting, dict)
            and any(isinstance(spell, dict) and spell.get("id") == "command"
                    for spell in card.spellcasting.get("spells", []))
        }
        assert actual == set(_EXPECTED)
        for name, dc in _EXPECTED.items():
            card = sources[name]
            original = card.model_dump_json()
            actions = prepared_command_spell_actions_2014(card)
            assert actions == (command_grovel_2014(dc),)
            spell = actions[0]
            assert spell.name == "Command" and spell.level == 1
            assert spell.action_cost == "action" and spell.range_ft == 60
            assert spell.save_ability == "wisdom" and spell.dc == dc
            assert spell.requires_target_sight
            assert spell.requires_shared_spoken_language
            assert not spell.requires_target_hearing
            assert spell.excluded_target_creature_types == ["undead"]
            assert not spell.concentration
            assert spell.allows_higher_slots
            assert spell.max_target_pair_distance_ft == 30
            assert spell_save_target_count(spell, 1) == 1
            assert spell_save_target_count(spell_at_slot(spell, 3), 3) == 3
            rider = spell.failed_save_timed_effect
            assert rider is not None
            assert (rider.effect_id, rider.duration_target_turns,
                    rider.expiry_timing, rider.turn_behavior) == (
                "commanded", 1, "target_turn_end", "fall_prone_end_turn",
            )
            # The canonical definition gets the same reusable spell, even if
            # unrelated spells keep this creature blocked from certification.
            definition = adapt_monster_mechanics_2014(card)
            assert [s for s in definition.spell_save_actions if s.id == "command"] == [spell]
            assert card.model_dump_json() == original
            renamed = card.model_copy(update={"id": "renamed-source", "name": "Renamed Source"})
            assert prepared_command_spell_actions_2014(renamed) == actions
    except Exception:
        logger.exception("2014 Command prepared-source binding regression failed.")
        raise


def test_command_source_mutations_fail_closed_without_admitting_incomplete_cards() -> None:
    try:
        sources = {row.id: row for row in load_monster_source_2014()}
        card = sources["cult-fanatic"]
        incomplete = card.model_copy(deep=True)
        incomplete.spellcasting["source_complete"] = False
        assert prepared_command_spell_actions_2014(incomplete) == ()

        for changed in (
            {"id": "command", "name": "changed", "level": 1},
            {"id": "command", "name": "command", "level": 2},
        ):
            altered = card.model_copy(deep=True)
            altered.spellcasting["spells"] = [
                changed if item.get("id") == "command" else item
                for item in altered.spellcasting["spells"]
            ]
            with pytest.raises(ValueError, match="source entry"):
                prepared_command_spell_actions_2014(altered)

        missing_printed = card.model_copy(deep=True)
        missing_printed.source_traits = re.sub(
            r"\bcommand\b", "changed", missing_printed.source_traits,
            flags=re.IGNORECASE,
        )
        with pytest.raises(ValueError, match="printed Spellcasting"):
            prepared_command_spell_actions_2014(missing_printed)

        missing_dc = card.model_copy(deep=True)
        missing_dc.spellcasting["save_dc"] = None
        with pytest.raises(ValueError, match="spell save DC"):
            prepared_command_spell_actions_2014(missing_dc)
        assert sources["cult-fanatic"].model_dump_json() == card.model_dump_json()
    except Exception:
        logger.exception("Command source-mutation fail-closed checks failed.")
        raise


def test_command_browser_serialization_uses_existing_generic_effect_fields() -> None:
    try:
        spell = command_grovel_2014(13)
        browser = _spell(spell)
        assert browser["id"] == "command" and browser["name"] == "Command"
        assert browser["requiresSharedSpokenLanguage"] is True
        assert browser["requiresTargetSight"] is True
        assert browser["excludedTargetCreatureTypes"] == ["undead"]
        assert browser["allowsHigherSlots"] is True
        assert browser["targetCountPerSlotAbove"] == 1
        assert browser["maxTargetPairDistanceFt"] == 30
        rider = browser["failedSaveTimedEffect"]
        assert rider["effectId"] == "commanded"
        assert rider["durationTargetTurns"] == 1
        assert rider["turnBehavior"] == "fall_prone_end_turn"
        assert rider["expiryTiming"] == "target_turn_end"
    except Exception:
        logger.exception("2014 Command browser parity fields are incomplete.")
        raise
