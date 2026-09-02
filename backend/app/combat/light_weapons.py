from __future__ import annotations

import logging
from dataclasses import dataclass

from app.combat.weapon_mastery import weapon_mastery_active
from app.content.fighting_style_rules import has_fighting_style
from app.domain.models import CombatantState, WeaponAttack

logger = logging.getLogger(__name__)
LIGHT_EXTRA_ATTACK_MARKER = "light-extra-attack"
NICK_FEATURE_ID = "weapon-mastery-nick"


@dataclass(frozen=True)
class LightExtraAttackPlan:
    attack: WeaponAttack
    uses_bonus_action: bool
    feature_id: str


def nick_mastery_active(state: CombatantState, attack: WeaponAttack) -> bool:
    return attack.weapon.light and weapon_mastery_active(state, attack, "Nick")


def light_extra_attack_used(state: CombatantState, turn_key: str) -> bool:
    return state.feature_last_turn_keys.get(LIGHT_EXTRA_ATTACK_MARKER) == turn_key


def mark_light_extra_attack_used(state: CombatantState, turn_key: str) -> None:
    state.feature_last_turn_keys[LIGHT_EXTRA_ATTACK_MARKER] = turn_key


def _extra_attack_profile(state: CombatantState, attack: WeaponAttack) -> WeaponAttack:
    modifier = attack.attack_ability_modifier
    if modifier is None:
        raise ValueError(
            f"Light extra attack {attack.id!r} requires an explicit attack ability modifier."
        )
    if has_fighting_style(state.template.fighting_styles, "Two-Weapon Fighting"):
        return attack.model_copy(deep=True)
    return attack.model_copy(update={"damage_bonus": attack.damage_bonus - max(0, modifier)})


def plan_light_extra_attack(
    state: CombatantState,
    trigger_attack: WeaponAttack,
    turn_key: str,
) -> LightExtraAttackPlan | None:
    """Plan the shared one-per-turn Light extra attack; Nick applies only to the Nick weapon's extra attack."""
    try:
        if not trigger_attack.weapon.light or light_extra_attack_used(state, turn_key):
            return None
        attacks = [state.template.weapon_attack, *state.template.alternate_weapon_attacks]
        candidates = [
            attack for attack in attacks
            if attack.weapon.light and attack.weapon.id != trigger_attack.weapon.id
        ]
        if not candidates:
            return None
        nick_candidate = next((attack for attack in candidates if nick_mastery_active(state, attack)), None)
        chosen = nick_candidate or candidates[0]
        nick_active = nick_candidate is not None
        return LightExtraAttackPlan(
            attack=_extra_attack_profile(state, chosen),
            uses_bonus_action=not nick_active,
            feature_id=NICK_FEATURE_ID if nick_active else LIGHT_EXTRA_ATTACK_MARKER,
        )
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Light extra attack planning failed for %s.", state.template.name)
        raise RuntimeError("Light extra attack could not be planned.") from exc
