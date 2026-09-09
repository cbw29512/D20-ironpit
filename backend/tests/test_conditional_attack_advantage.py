from __future__ import annotations

import logging

from app.combat.attacks import resolve_attack
from app.combat.conditional_attack_advantage import conditional_attack_advantage_sources
from app.combat.dice import FixedDiceProvider
from app.combat.state import build_combatant_state
from app.content.demo import build_demo_fighter, build_goblin_warrior
from app.domain.models import ConditionalAttackAdvantage, RollMode

logger = logging.getLogger(__name__)


def _attack():
    try:
        return build_goblin_warrior().weapon_attack.model_copy(update={
            "conditional_damage": [],
            "conditional_attack_advantage": [ConditionalAttackAdvantage(trigger="target_not_full_hp")],
        })
    except Exception:
        logger.exception("Failed to build conditional-Advantage regression attack.")
        raise


def test_target_not_full_hp_advantage_uses_effective_max_hp() -> None:
    try:
        target = build_combatant_state(build_demo_fighter())
        attack = _attack()
        assert conditional_attack_advantage_sources(attack, target) == 0
        target.max_hp_bonus = 5
        target.current_hp += 5
        assert conditional_attack_advantage_sources(attack, target) == 0
        target.current_hp -= 1
        assert conditional_attack_advantage_sources(attack, target) == 1
    except Exception:
        logger.exception("Target-not-full-HP state regression failed.")
        raise


def test_target_not_full_hp_advantage_enters_canonical_attack_roll_mode() -> None:
    try:
        attacker = build_combatant_state(build_goblin_warrior())
        defender = build_combatant_state(build_demo_fighter())
        attack = _attack()
        defender.current_hp -= 1
        event = resolve_attack(1, 1, attacker, defender, attack, 5, FixedDiceProvider([3, 17, 2]))
        assert event.attack_roll.mode is RollMode.ADVANTAGE
        assert event.attack_roll.selected_roll == 17
    except Exception:
        logger.exception("Canonical attack-roll conditional Advantage regression failed.")
        raise
