from __future__ import annotations

import logging

from app.combat.conditional_damage import round1_initiative_lead
from app.combat.hit_points import effective_max_hp
from app.domain.models import CombatantState, WeaponAttack
from app.domain.traits import CombatTrait

logger = logging.getLogger(__name__)


def _grappled_by(target: CombatantState, attacker_event_id: str | None) -> bool:
    if attacker_event_id is None:
        return False
    return any(source.source_id == attacker_event_id for source in target.grapple_sources)


def assassinate_advantage(attacker: CombatantState, target: CombatantState, round_number: int | None) -> int:
    return int(
        CombatTrait.ASSASSINATE in attacker.template.combat_traits
        and round1_initiative_lead(attacker, target, round_number)
    )


def assassinate_critical(attacker: CombatantState, target: CombatantState) -> bool:
    return CombatTrait.ASSASSINATE in attacker.template.combat_traits and "surprised" in target.active_effect_ids


def conditional_attack_advantage_sources(
    attack: WeaponAttack,
    target: CombatantState,
    attacker_event_id: str | None = None,
    attacker: CombatantState | None = None,
    round_number: int | None = None,
) -> int:
    """Return declarative attack-roll Advantage sources satisfied by target state."""
    try:
        total = 0
        for spec in attack.conditional_attack_advantage:
            if spec.trigger == "target_not_full_hp":
                total += int(target.current_hp < effective_max_hp(target))
                continue
            if spec.trigger == "target_grappled_by_self":
                total += int(_grappled_by(target, attacker_event_id))
                continue
            if spec.trigger == "round1_initiative_lead":
                if attacker is None:
                    raise ValueError("Opening initiative Advantage requires attacker state.")
                total += int(round1_initiative_lead(attacker, target, round_number))
                continue
            raise ValueError(f"Unsupported conditional attack Advantage trigger: {spec.trigger!r}.")
        if attacker is not None:
            total += assassinate_advantage(attacker, target, round_number)
        return total
    except Exception:
        logger.exception("Failed to evaluate conditional attack Advantage for %s.", attack.id)
        raise
