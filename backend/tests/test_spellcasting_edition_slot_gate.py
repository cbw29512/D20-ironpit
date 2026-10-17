"""Edition-isolation regressions for the shared slot-per-turn gate."""
import logging

import pytest

from app.combat.spellcasting import mark_slot_spell_cast, slot_spell_available
from app.combat.state import build_combatant_state
from app.content.audited_cleric import build_seraphine_dawnshield

logger = logging.getLogger(__name__)


@pytest.mark.parametrize("edition,second_cast_legal", [("2014", True), ("2024", False)])
def test_slot_gate_uses_combatant_edition(edition: str, second_cast_legal: bool) -> None:
    try:
        template = build_seraphine_dawnshield().model_copy(update={"ruleset": edition})
        state = build_combatant_state(template)
        key = "1:caster"
        assert slot_spell_available(state, key)
        mark_slot_spell_cast(state, key)
        assert slot_spell_available(state, key) is second_cast_legal
        if second_cast_legal:
            mark_slot_spell_cast(state, key)
        else:
            with pytest.raises(ValueError, match="already been expended"):
                mark_slot_spell_cast(state, key)
        assert slot_spell_available(state, "2:caster")
        assert slot_spell_available(build_combatant_state(template), key)
    except Exception:
        logger.exception("Spellcasting edition gate regression failed for %s", edition)
        raise


def test_missing_turn_key_fails_closed() -> None:
    try:
        state = build_combatant_state(build_seraphine_dawnshield())
        with pytest.raises(ValueError, match="active turn key"):
            slot_spell_available(state, "")
    except Exception:
        logger.exception("Missing-turn-key spellcasting regression failed")
        raise
