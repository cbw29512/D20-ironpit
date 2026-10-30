from __future__ import annotations

import logging

from app.combat.action_economy import is_available
from app.combat.attack_roll_modifiers import attack_roll_advantage_sources
from app.combat.dice import FixedDiceProvider
from app.combat.hit_modifiers import expire_source_turn_start_modifiers
from app.combat.resources import resource_state
from app.combat.state import begin_turn, build_combatant_state
from app.combat.support_actions import resolve_support_action
from app.content.capability_registry import build_combatant_from_capabilities
from app.content.monster_catalog import load_monster_rows
from app.content.monster_source_audit import audit_monster_source
from app.domain.encounters import EncounterCombatant

logger = logging.getLogger(__name__)


def _row(name: str) -> dict[str, object]:
    try:
        return next(row for row in load_monster_rows() if row["name"] == name)
    except Exception:
        logger.exception("Failed to load monster row for %s.", name)
        raise


def test_frost_giant_war_cry_is_source_backed_recharge_support() -> None:
    try:
        frost = build_combatant_from_capabilities("srd-frost-giant")
        assert len(frost.support_actions) == 1
        action = frost.support_actions[0]
        assert action.name == "War Cry"
        assert action.action_cost == "bonus_action"
        assert (
            action.temporary_hp_dice_count,
            action.temporary_hp_dice_size,
            action.temporary_hp_bonus,
        ) == (2, 10, 5)
        assert action.attack_roll_advantage_until_source_turn_start is True

        issues = audit_monster_source(frost, _row("Frost Giant"))
        assert "uncertified-bonus-action:war-cry" not in issues
        assert not any(
            issue.startswith("uncertified-limited-use:bonusactions-war-cry")
            for issue in issues
        )
        assert "unsupported-action-rider" not in issues
    except Exception:
        logger.exception("Frost Giant War Cry source regression failed.")
        raise


def test_war_cry_spends_bonus_action_and_expires_attack_advantage() -> None:
    try:
        frost = build_combatant_from_capabilities("srd-frost-giant")
        state = build_combatant_state(frost)
        begin_turn(state)
        member = EncounterCombatant(
            combatant_id="frost",
            side="monsters",
            position_ft=0,
            state=state,
        )
        action = frost.support_actions[0]

        event = resolve_support_action(
            1,
            1,
            member,
            member,
            action,
            FixedDiceProvider([5, 6]),
        )

        assert event.temporary_hp_before == 0
        assert event.temporary_hp_after == 16
        assert state.temporary_hp == 16
        assert is_available(state, "bonus_action") is False
        assert resource_state(state, action.resource_id).current_uses == 0
        assert attack_roll_advantage_sources(state) == 1

        removed = expire_source_turn_start_modifiers([state], member.combatant_id)
        assert removed == 1
        assert attack_roll_advantage_sources(state) == 0
    except Exception:
        logger.exception("War Cry runtime lifecycle regression failed.")
        raise
