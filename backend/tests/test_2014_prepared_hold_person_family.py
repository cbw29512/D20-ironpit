"""2014 prepared Hold Person reuses the single, source-parameterized spell.

The parser's complete prepared-spell list remains authoritative for this
capability. Other unsupported spells continue to block full monster admission.
"""
from __future__ import annotations

import logging

from app.content.monster_source_2014 import load_monster_source_2014
from app.content.monster_prepared_spells_2014 import prepared_spell_save_actions_2014

logger = logging.getLogger(__name__)

_EXPECTED = {
    "cult-fanatic": 11,
    "guardian-naga": 16,
    "mummy-lord": 17,
    "spirit-naga": 14,
}


def test_2014_hold_person_all_printed_prepared_casters_share_one_spell() -> None:
    try:
        cards = load_monster_source_2014()
        assert len(cards) == 327
        matching = [
            card for card in cards
            if isinstance(card.spellcasting, dict)
            and any(
                isinstance(spell, dict) and spell.get("id") == "hold-person"
                for spell in card.spellcasting.get("spells", [])
            )
        ]
        assert {card.id for card in matching} == set(_EXPECTED)
        for card in matching:
            initial = card.model_dump_json()
            actions = [
                action for action in prepared_spell_save_actions_2014(card)
                if action.id == "hold-person"
            ]
            assert len(actions) == 1
            action = actions[0]
            assert (action.level, action.action_cost, action.dc, action.save_ability) == (
                2, "action", _EXPECTED[card.id], "wisdom",
            )
            assert action.range_ft == 60
            assert action.required_target_creature_types == ["humanoid"]
            assert action.concentration and action.duration_minutes == 1
            assert action.failed_save_timed_effect is not None
            assert action.failed_save_timed_effect.effect_id == "paralyzed"
            assert action.failed_save_timed_effect.repeat_save_timing == "target_turn_end"
            assert action.failed_save_timed_effect.repeat_save_dc == _EXPECTED[card.id]
            assert card.model_dump_json() == initial

            # Source IDs/names do not select a Hold Person combat resolver.
            renamed = card.model_copy(update={"id": "renamed-source", "name": "Renamed Source"})
            renamed_actions = [
                spell for spell in prepared_spell_save_actions_2014(renamed)
                if spell.id == "hold-person"
            ]
            assert renamed_actions == actions

            # An incomplete parsed source cannot invent a castable spell.
            truncated = card.model_copy(deep=True)
            truncated.spellcasting["source_complete"] = False
            assert not [
                spell for spell in prepared_spell_save_actions_2014(truncated)
                if spell.id == "hold-person"
            ]
    except Exception:
        logger.exception("2014 prepared Hold Person family regression failed.")
        raise
