from __future__ import annotations

import logging

from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import WeaponAttackKind

logger = logging.getLogger(__name__)


def _nearest_enemy_distance(target: EncounterCombatant, setup: EncounterSetup) -> int:
    enemies = setup.monsters if target.side == "heroes" else setup.heroes
    living = [enemy for enemy in enemies if enemy.state.is_alive and not enemy.state.is_dead]
    return min((abs(target.position_ft - enemy.position_ft) for enemy in living), default=10**9)


def _priority(
    caster: EncounterCombatant,
    target: EncounterCombatant,
    setup: EncounterSetup,
) -> tuple[int, int, int, str]:
    is_melee = target.state.template.weapon_attack.weapon.attack_kind is WeaponAttackKind.MELEE
    group = 0 if is_melee else 1 if target is caster else 2
    return (
        group,
        _nearest_enemy_distance(target, setup),
        abs(caster.position_ft - target.position_ft),
        target.combatant_id,
    )


def select_friendly_buff_targets(
    caster: EncounterCombatant,
    setup: EncounterSetup,
    range_ft: int,
    target_count: int,
) -> list[EncounterCombatant]:
    """Select legal friendly targets: all melee first, then caster, then remaining back line."""
    try:
        side = setup.heroes if caster.side == "heroes" else setup.monsters
        legal = [
            target for target in side
            if target.state.is_alive and not target.state.is_dead
            and abs(caster.position_ft - target.position_ft) <= range_ft
        ]
        legal.sort(key=lambda target: _priority(caster, target, setup))
        return legal[:target_count]
    except Exception:
        logger.exception("Friendly buff target selection failed for %s.", caster.combatant_id)
        raise
