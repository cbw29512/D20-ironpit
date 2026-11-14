"""An identical repeated hit refreshes expiry, not modifier payload or stacks."""
import logging

import pytest

from app.combat.modifier_stack import add_modifier
from app.combat.spell_modifiers import build_spell_modifier
from app.combat.state import build_combatant_state
from app.content.audited_fighter import build_karnok_stoneward
from app.content.druid_2024_spells import build_starry_wisp_2024

logger = logging.getLogger(__name__)


def test_2024_starry_wisp_repeat_hit_refreshes_generic_expiry():
    try:
        spell = build_starry_wisp_2024(attack_bonus=5, character_level=4)
        assert spell.on_hit_modifier_effects
        effect = spell.on_hit_modifier_effects[0]
        state = build_combatant_state(build_karnok_stoneward())
        before_card = state.template.model_dump_json()
        first = build_spell_modifier(
            "caster", "target", spell.id, effect, 0, spell.name, round_number=1,
        )
        second = build_spell_modifier(
            "caster", "target", spell.id, effect, 0, spell.name, round_number=2,
        )
        assert first.id == second.id
        assert first.expires_source_turn_end_round == 2
        assert second.expires_source_turn_end_round == 3
        add_modifier(state, first)
        with pytest.raises(ValueError, match="different data"):
            add_modifier(state, second)
        add_modifier(state, second, refresh_expiry=True)
        assert state.active_modifiers == [second]
        add_modifier(state, second, refresh_expiry=True)
        assert state.active_modifiers == [second]
        with pytest.raises(ValueError, match="different data"):
            add_modifier(state, second.model_copy(update={
                "source_name": "Different Effect",
            }), refresh_expiry=True)
        with pytest.raises(ValueError, match="different data"):
            add_modifier(state, first, refresh_expiry=True)
        assert state.template.model_dump_json() == before_card
    except Exception:
        logger.exception("2024 repeat-hit spell modifier expiry test failed")
        raise
