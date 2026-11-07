"""Generic on-hit delivery for Swallow actions embedded in an attack."""
from __future__ import annotations

import logging

from app.combat.swallow_state import swallow_after_bite
from app.domain.models import CombatantState, WeaponAttack

logger = logging.getLogger(__name__)


def apply_attack_hit_swallow(
    attacker: CombatantState,
    defender: CombatantState,
    attack: WeaponAttack,
    *,
    attacker_id: str,
    defender_id: str,
    pre_hit_grappled_by_attacker: bool,
) -> bool:
    """Apply only an attack-hit Swallow whose grapple existed before this hit."""
    try:
        if not pre_hit_grappled_by_attacker:
            return False
        rule = next(
            (
                item for item in attacker.template.swallow_actions
                if item.delivery_mode == "attack_hit"
                and item.attack_id == attack.id
            ),
            None,
        )
        if rule is None:
            return False
        return swallow_after_bite(
            attacker_id,
            attacker,
            defender_id,
            defender,
            rule,
            bite_hit=True,
        )
    except Exception:
        logger.exception(
            "Attack-hit Swallow delivery failed for %s with %s.",
            attacker.template.name,
            attack.id,
        )
        raise



def resolve_attack_hit_swallow_save(
    attacker: CombatantState,
    defender: CombatantState,
    attack: WeaponAttack,
    dice,
    *,
    attacker_id: str,
    defender_id: str,
):
    """On a successful Bite hit, use printed save before universal Swallow.

    An unrelated card can declare the same profile. A source without a
    printed on-hit save continues through grapple-first Swallow unchanged.
    """
    from app.combat.on_hit_condition_save import OnHitConditionSaveResolution
    from app.combat.saving_throw_rolls import resolve_saving_throw
    from app.domain.saving_throw_context import SavingThrowContext
    from app.domain.size import size_at_most

    try:
        action = next((
            item for item in attacker.template.swallow_actions
            if item.delivery_mode == "attack_hit"
            and item.attack_id == attack.id
            and not item.requires_existing_grapple
            and item.on_hit_save_ability is not None
            and item.on_hit_save_dc is not None
        ), None)
        if action is None or not size_at_most(defender.template.size, action.max_target_size):
            return OnHitConditionSaveResolution()
        if (not defender.is_alive or defender.is_dead or defender.current_hp <= 0
                or defender.swallowed is not None):
            return OnHitConditionSaveResolution()
        roll, succeeded = resolve_saving_throw(
            defender, action.on_hit_save_ability, action.on_hit_save_dc,
            dice, SavingThrowContext(),
        )
        applied = not succeeded and swallow_after_bite(
            attacker_id, attacker, defender_id, defender, action, bite_hit=True,
        )
        return OnHitConditionSaveResolution(
            save_roll=roll,
            save_ability=action.on_hit_save_ability,
            save_dc=action.on_hit_save_dc,
            save_succeeded=succeeded,
            additional_conditions=("blinded", "restrained") if applied else (),
        )
    except Exception:
        logger.exception(
            "Generic failed-save Bite-to-Swallow failed for %s.", attack.id,
        )
        raise
