from __future__ import annotations

import logging

from app.combat.conditions import is_incapacitated, resolve_condition_attack_sources
from app.combat.cover import resolve_attack_cover_bonus
from app.combat.masteries import resolve_attack_roll_effect_sources
from app.combat.range import resolve_attack_roll_mode
from app.combat.sight import can_see_combatant, resolve_visibility_attack_sources
from app.domain.models import (
    BattlefieldState,
    CombatantState,
    RollMode,
    Weapon,
)

logger = logging.getLogger(__name__)


def resolve_attack_mode_and_cover(
    attacker: CombatantState,
    defender: CombatantState,
    weapon: Weapon,
    distance_ft: int,
    battlefield: BattlefieldState | None,
) -> tuple[RollMode, int]:
    try:
        cover_bonus = resolve_attack_cover_bonus(defender, battlefield)
        advantage_sources, disadvantage_sources = resolve_attack_roll_effect_sources(
            attacker, defender.template.id
        )
        sight_advantage, sight_disadvantage = resolve_visibility_attack_sources(
            attacker, defender, battlefield
        )
        condition_advantage, condition_disadvantage = resolve_condition_attack_sources(defender)
        close_enemy_active = (
            can_see_combatant(defender, attacker, battlefield)
            and not is_incapacitated(defender)
        )
        mode = resolve_attack_roll_mode(
            weapon,
            distance_ft,
            advantage_sources=advantage_sources + sight_advantage + condition_advantage,
            other_disadvantage_sources=(
                disadvantage_sources + sight_disadvantage + condition_disadvantage
            ),
            close_enemy_active=close_enemy_active,
        )
        return mode, cover_bonus
    except Exception as exc:
        logger.exception(
            "Failed to resolve attack-roll context: %s -> %s.",
            attacker.template.name,
            defender.template.name,
        )
        raise RuntimeError("Attack-roll context could not be resolved.") from exc
