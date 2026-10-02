from __future__ import annotations

import logging

from app.combat.damage_defenses import adjusted_damage_amount
from app.domain.models import CombatantState, DamageType, WeaponAttack

logger = logging.getLogger(__name__)


def choose_attack_damage_type(
    attacker: CombatantState,
    attack: WeaponAttack,
    target: CombatantState | None,
    *,
    source_qualifiers: set | None = None,
) -> DamageType:
    """Choose the most effective legal damage type for one attack without source-name branching."""
    try:
        options = [attack.weapon.damage_type, *attack.weapon.damage_type_choices]
        if not options or target is None:
            return attack.weapon.damage_type
        ignored_resistance_types = {
            damage_type
            for grant in attacker.template.progression_features.damage_resistance_bypass_grants
            for damage_type in grant.damage_types
        }
        scored = [
            (
                adjusted_damage_amount(
                    1000,
                    damage_type,
                    target,
                    source_qualifiers=source_qualifiers or set(),
                    ignored_resistance_types=ignored_resistance_types,
                ),
                -index,
                damage_type,
            )
            for index, damage_type in enumerate(options)
        ]
        return max(scored, key=lambda item: (item[0], item[1]))[2]
    except Exception as exc:
        logger.exception(
            "Failed to choose attack damage type for %s against %s.",
            attack.id,
            target.template.name if target is not None else "no target",
        )
        raise RuntimeError("Attack damage type choice could not be resolved.") from exc
