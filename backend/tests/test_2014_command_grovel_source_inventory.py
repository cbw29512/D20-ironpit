"""2014 Command source inventory for the locked automated Grovel choice.

This audit does NOT admit a monster or implement language/turn-timing rules.
A new prepared Command caster must be reviewed before source admission.
"""
from __future__ import annotations

import logging

from app.content.monster_source_2014 import load_monster_source_2014

logger = logging.getLogger(__name__)

# Source-specific data is only for certification; runtime must never branch on IDs.
_EXPECTED_DC = {
    "androsphinx": 18,
    "cult-fanatic": 11,
    "guardian-naga": 16,
    "mummy-lord": 17,
}


def test_2014_command_spell_source_inventory_is_complete_and_immutable() -> None:
    try:
        cards = load_monster_source_2014()
        assert len(cards) == 327
        originals = {card.id: card.model_dump_json() for card in cards}
        prepared = [
            card for card in cards
            if isinstance(card.spellcasting, dict)
            and any(
                isinstance(spell, dict) and spell.get("id") == "command"
                for spell in (card.spellcasting.get("spells") or [])
            )
        ]
        innate = [
            card.id for card in cards
            if isinstance(card.innate_spellcasting, dict)
            and any(
                isinstance(spell, dict) and spell.get("id") == "command"
                for spell in (card.innate_spellcasting.get("spells") or [])
            )
        ]
        assert not innate, "New innate Command needs its own source and use audit."
        assert {card.id for card in prepared} == set(_EXPECTED_DC)

        for card in prepared:
            source = card.spellcasting
            assert source["source_complete"] is True
            assert source["unsupported_text"] is None
            assert source["ability"] == "wisdom"
            assert source["save_dc"] == _EXPECTED_DC[card.id]
            assert "command" in (card.source_traits or "").casefold()
            entries = [spell for spell in source["spells"] if spell["id"] == "command"]
            assert entries == [{"id": "command", "name": "command", "level": 1}]

        # The audit must not change any source card; new fight state is separate.
        assert {card.id: card.model_dump_json() for card in cards} == originals
    except Exception:
        logger.exception("2014 Command source inventory or immutability failed.")
        raise
