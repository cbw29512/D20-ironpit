from __future__ import annotations

import logging

from app.combat.card_effects import rage_effect_change
from app.combat.conditions import is_incapacitated, require_activity
from app.domain.models import (
    AbilityKind,
    BattleEvent,
    CombatantState,
    DamageRollComponent,
    DamageType,
    WeaponAttack,
)

logger = logging.getLogger(__name__)
RAGE = "rage"
PHYSICAL_DAMAGE = {DamageType.BLUDGEONING, DamageType.PIERCING, DamageType.SLASHING}


def rage_damage_bonus(level: int | None) -> int:
    if level is None or level < 1:
        return 0
    if level >= 16:
        return 4
    if level >= 9:
        return 3
    return 2


def is_raging(state: CombatantState) -> bool:
    return bool(state.raging and not is_incapacitated(state))


def _rage_resource(state: CombatantState):
    return next((resource for resource in state.resources if resource.id == RAGE), None)


def enter_rage(sequence: int, round_number: int, actor: CombatantState) -> BattleEvent:
    try:
        if RAGE not in actor.template.bonus_action_features:
            raise ValueError("Combatant does not have Rage.")
        require_activity(actor, "Bonus Action")
        if actor.template.wearing_heavy_armor:
            raise ValueError("Rage cannot be entered while wearing Heavy armor.")
        if actor.raging:
            raise ValueError("Combatant is already raging.")
        resource = _rage_resource(actor)
        if resource is None or resource.current_uses <= 0:
            raise ValueError("No Rage uses remain.")
        if not actor.bonus_action_available:
            raise ValueError("Bonus Action is not available for Rage.")
        resource.current_uses -= 1
        actor.bonus_action_available = False
        actor.raging = True
        actor.rage_extension_required = False
        actor.rage_extended_this_turn = False
        actor.temporary_damage_resistances |= PHYSICAL_DAMAGE
        return BattleEvent(
            sequence=sequence,
            round_number=round_number,
            event_type="status",
            actor_id=actor.template.id,
            actor_name=actor.template.name,
            effect_changes=[rage_effect_change(actor, "apply")],
            feature_id=RAGE,
            resource_remaining=resource.current_uses,
            animation="status",
            description=f"{actor.template.name} enters Rage. {resource.current_uses} uses remain.",
        )
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Rage activation failed for %s.", actor.template.name)
        raise RuntimeError("Rage could not be activated.") from exc


def begin_rage_turn(actor: CombatantState) -> bool:
    try:
        if not actor.raging:
            return False
        if is_incapacitated(actor) or actor.template.wearing_heavy_armor:
            end_rage(actor)
            return True
        actor.rage_extension_required = True
        actor.rage_extended_this_turn = False
        return False
    except Exception as exc:
        logger.exception("Rage turn start failed for %s.", actor.template.name)
        raise RuntimeError("Rage turn could not begin.") from exc


def extend_rage_by_attack(actor: CombatantState) -> None:
    if is_raging(actor):
        actor.rage_extension_required = False
        actor.rage_extended_this_turn = True


def extend_rage_with_bonus_action(actor: CombatantState) -> None:
    try:
        if not is_raging(actor):
            raise ValueError("Rage is not active.")
        require_activity(actor, "Bonus Action")
        if not actor.bonus_action_available:
            raise ValueError("Bonus Action is not available to extend Rage.")
        actor.bonus_action_available = False
        actor.rage_extension_required = False
        actor.rage_extended_this_turn = True
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Rage extension failed for %s.", actor.template.name)
        raise RuntimeError("Rage could not be extended.") from exc


def end_rage(actor: CombatantState) -> None:
    actor.raging = False
    actor.rage_extension_required = False
    actor.rage_extended_this_turn = False
    actor.temporary_damage_resistances -= PHYSICAL_DAMAGE


def end_rage_if_unextended(actor: CombatantState) -> bool:
    try:
        if actor.raging and actor.rage_extension_required:
            end_rage(actor)
            return True
        return False
    except Exception as exc:
        logger.exception("Rage expiration failed for %s.", actor.template.name)
        raise RuntimeError("Rage expiration could not be resolved.") from exc


def rage_strength_save_advantage(actor: CombatantState, ability: AbilityKind) -> int:
    return int(is_raging(actor) and ability is AbilityKind.STRENGTH)


def rage_damage_component(
    actor: CombatantState,
    attack: WeaponAttack,
) -> DamageRollComponent | None:
    try:
        if not is_raging(actor) or attack.ability is not AbilityKind.STRENGTH:
            return None
        bonus = rage_damage_bonus(actor.template.level)
        if bonus <= 0:
            return None
        return DamageRollComponent(
            source="Rage",
            notation=f"{bonus:+d}",
            rolls=[],
            modifier=bonus,
            damage_type=attack.weapon.damage_type,
            total=bonus,
        )
    except Exception as exc:
        logger.exception("Rage damage failed for %s.", actor.template.name)
        raise RuntimeError("Rage damage could not be resolved.") from exc
