"""Full-HP self-buff expiry follows source-owned generic timed-effect removal."""
from __future__ import annotations

import logging

from app.combat.state import build_combatant_state
from app.combat.timed_conditions import apply_timed_condition
from app.combat.timed_self_buffs import resolve_timed_self_buff
from app.combat.zero_hp import restore_hit_points
from app.content.audited_fighter import build_karnok_stoneward
from app.domain.encounters import EncounterCombatant
from app.domain.size import CreatureSize
from app.domain.timed_self_buffs import TimedSelfBuffAction

logger = logging.getLogger(__name__)


def test_renamed_full_hp_buff_restores_size_without_deleting_unrelated_effect():
    """Source-name-independent healing cleanup must undo owned size at full HP."""
    try:
        card = build_karnok_stoneward()
        original_size = card.size
        action = TimedSelfBuffAction(
            id="unrelated-growth", name="Unrelated Growth",
            ends_at_full_hp=True, duration_rounds=10,
            size_override=CreatureSize.LARGE,
            ability_check_advantage_abilities=["strength"],
        )
        template = card.model_copy(update={"timed_self_buff_actions": [action]})
        state = build_combatant_state(template)
        state.current_hp = state.template.max_hp - 1
        actor = EncounterCombatant(
            combatant_id="renamed-caster", side="heroes", position_ft=0,
            state=state,
        )
        applied = apply_timed_condition(
            state, "invisible", "other-source",
            source_effect_id="unrelated-invisibility",
            expires_at_start_of_source_turn=False,
        )
        assert applied == "invisible"
        result = resolve_timed_self_buff(
            1, 1, actor, action, spend_action_cost=False,
        )
        assert result.feature_id == action.id
        assert state.template.size == CreatureSize.LARGE
        assert state.active_effect_ids.count(action.id) == 1
        assert restore_hit_points(state, 1) == 1
        assert state.template.size == original_size
        assert card.size == original_size
        assert action.id not in state.active_effect_ids
        assert "invisible" in state.active_effect_ids
        assert len(state.timed_effects) == 1
        assert state.timed_effects[0].source_effect_id == "unrelated-invisibility"
    except Exception:
        logger.exception("Source-neutral full-HP self-buff lifecycle regression failed")
        raise
