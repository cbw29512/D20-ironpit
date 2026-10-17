"""Fail-closed spell-slot lookup for cantrips in both editions."""
import logging

import pytest

from app.combat.spellcasting import legal_slot_levels, mark_slot_spell_cast
from app.combat.state import build_combatant_state
from app.content.audited_cleric import build_seraphine_dawnshield

logger = logging.getLogger(__name__)


@pytest.mark.parametrize("ruleset", ["2014", "2024"])
def test_cantrip_slot_query_validates_turn_and_ruleset(ruleset: str) -> None:
    try:
        template = build_seraphine_dawnshield().model_copy(update={"ruleset": ruleset})
        state = build_combatant_state(template)
        assert legal_slot_levels(state, "1:caster", 0) == (0,)
        mark_slot_spell_cast(state, "1:caster")
        assert legal_slot_levels(state, "1:caster", 0) == (0,)
        with pytest.raises(ValueError, match="active turn key"):
            legal_slot_levels(state, "", 0)
        with pytest.raises(ValueError, match="integer"):
            legal_slot_levels(state, "1:caster", True)
        with pytest.raises(ValueError, match="integer"):
            legal_slot_levels(state, "1:caster", -1)
        invalid = build_combatant_state(template.model_copy(update={"ruleset": "unknown"}))
        with pytest.raises(ValueError, match="Unsupported"):
            legal_slot_levels(invalid, "1:caster", 0)
    except Exception:
        logger.exception("Cantrip slot-query validation failed for %s", ruleset)
        raise
