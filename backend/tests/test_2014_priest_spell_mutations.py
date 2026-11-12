"""2014 Priest source changes must never inherit fabricated spell actions."""
from __future__ import annotations

import logging

import pytest

from app.content.monster_basic_candidates_2014 import basic_blockers_2014
from app.content.monster_priest_spells_2014 import priest_spell_actions_2014
from app.content.monster_source_2014 import load_monster_source_2014
from app.content.monster_source_priest_spellcasting_2014 import (
    source_proves_priest_spellcasting_2014,
)

logger = logging.getLogger(__name__)


def _source():
    try:
        return next(row for row in load_monster_source_2014()
                    if row.id == "priest")
    except Exception:
        logger.exception("Priest mutation source fixture was not found.")
        raise


@pytest.mark.parametrize("old,new", [
    ("5th-level spellcaster", "6th-level spellcaster"),
    ("DC 13", "DC 14"),
    ("+5 to hit with spell attacks", "+6 to hit with spell attacks"),
    ("1st level (4 slots)", "1st level (3 slots)"),
    ("2nd level (3 slots)", "2nd level (4 slots)"),
    ("3rd level (2 slots)", "3rd level (1 slot)"),
    ("guiding bolt, sanctuary", "fireball, sanctuary"),
    ("lesser restoration, spiritual weapon", "lesser restoration, hold person"),
    ("dispel magic,", "shield,"),
    ("spirit guardians", "fireball"),
])
def test_printed_spell_changes_fail_closed(old, new):
    try:
        card = _source()
        assert old in card.source_traits
        altered = card.model_copy(update={
            "source_traits": card.source_traits.replace(old, new),
        })
        assert not source_proves_priest_spellcasting_2014(altered)
        assert "mechanic:spellcasting" in basic_blockers_2014(altered)
        assert not priest_spell_actions_2014(altered).saves
    except Exception:
        logger.exception("Mutated Priest spell list was silently admitted.")
        raise


def test_new_unheaded_rider_or_structured_slot_change_fails_closed():
    try:
        card = _source()
        extra = card.model_copy(update={
            "source_traits": card.source_traits + "<p>All spells also deal 5 fire damage.</p>",
        })
        # Appended text after source sections is still visible to the
        # complete Spellcasting proof: it cannot be hidden in a continuation.
        assert not source_proves_priest_spellcasting_2014(extra)
        changed = card.model_copy(update={
            "spellcasting": {**card.spellcasting, "slots": {"1": 4, "2": 3, "3": 3}},
        })
        assert not source_proves_priest_spellcasting_2014(changed)
        spells = [dict(row) for row in card.spellcasting["spells"]]
        spells[4]["id"] = "magic-missile"
        changed_spell = card.model_copy(update={
            "spellcasting": {**card.spellcasting, "spells": spells},
        })
        assert not source_proves_priest_spellcasting_2014(changed_spell)
    except Exception:
        logger.exception("Priest source mutation guard failed.")
        raise


def test_source_name_is_only_display_not_dispatch():
    try:
        card = _source()
        renamed = card.model_copy(update={
            "id": "renamed-caster", "name": "Other Character",
        })
        assert source_proves_priest_spellcasting_2014(renamed)
        assert priest_spell_actions_2014(renamed).attacks[0].id == "guiding-bolt"
    except Exception:
        logger.exception("2014 Priest source proof depended on card identity.")
        raise
