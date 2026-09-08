from __future__ import annotations

import logging

from app.domain.models import CombatantState, WeaponAttack
from app.domain.traits import CombatTrait

logger = logging.getLogger(__name__)


def conditional_attack_advantage_sources(
    attacker: CombatantState,
    defender: CombatantState,
    attack: WeaponAttack,
) -> int:
    try:
        target_missing_hp = defender.current_hp < defender.template.max_hp
        if not target_missing_hp:
            return 0
        explicit = sum(
            1
            for modifier in attack.conditional_attack_modifiers
            if modifier.mode == "advantage" and modifier.trigger == "target_missing_hp"
        )
        trait = int(CombatTrait.BLOOD_FRENZY in attacker.template.combat_traits)
        return explicit + trait
    except Exception as exc:
        logger.exception("Conditional attack Advantage resolution failed for %s.", attack.id)
        raise RuntimeError("Conditional attack Advantage resolution failed.") from exc


def conditional_attack_disadvantage_sources(
    attacker: CombatantState,
    defender: CombatantState,
    attack: WeaponAttack,
) -> int:
    try:
        del attacker
        if defender.current_hp >= defender.template.max_hp:
            return 0
        return sum(
            1
            for modifier in attack.conditional_attack_modifiers
            if modifier.mode == "disadvantage" and modifier.trigger == "target_missing_hp"
        )
    except Exception as exc:
        logger.exception("Conditional attack Disadvantage resolution failed for %s.", attack.id)
        raise RuntimeError("Conditional attack Disadvantage resolution failed.") from exc
