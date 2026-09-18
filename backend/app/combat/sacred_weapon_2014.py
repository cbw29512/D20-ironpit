from __future__ import annotations

import logging

from app.combat.action_economy import is_available, spend
from app.combat.modifier_stack import add_modifier
from app.domain.encounters import EncounterCombatant
from app.domain.events import BattleEvent
from app.domain.modifiers import CombatModifier, ModifierKind

logger = logging.getLogger(__name__)
_EFFECT_ID = "sacred-weapon"


def _channel_resource(member: EncounterCombatant):
    return next((item for item in member.state.resources if item.id == "channel-divinity"), None)


def sacred_weapon_active(member: EncounterCombatant) -> bool:
    return any(
        item.source_effect_id == _EFFECT_ID
        for item in member.state.active_modifiers
    )


def resolve_sacred_weapon(
    sequence: int,
    round_number: int,
    member: EncounterCombatant,
) -> BattleEvent | None:
    """Activate a 2014 weapon-scoped flat attack bonus through generic modifier state."""
    try:
        bonus = member.state.template.progression_features.sacred_weapon_2014_bonus
        resource = _channel_resource(member)
        if bonus <= 0 or sacred_weapon_active(member) or not is_available(member.state, "action"):
            return None
        if resource is None or resource.current_uses < 1:
            return None
        weapon_id = member.state.template.weapon_attack.weapon.id
        spend(member.state, "action")
        resource.current_uses -= 1
        add_modifier(member.state, CombatModifier(
            id=f"{member.combatant_id}:{_EFFECT_ID}",
            source_id=member.combatant_id,
            source_effect_id=_EFFECT_ID,
            kind=ModifierKind.ATTACK_ROLL_FLAT,
            flat_bonus=bonus,
            weapon_id=weapon_id,
            expires_source_turn_end_round=round_number + 10,
        ))
        return BattleEvent(
            sequence=sequence,
            round_number=round_number,
            event_type="feature",
            actor_id=member.combatant_id,
            actor_name=member.state.template.name,
            feature_id=_EFFECT_ID,
            resource_remaining=resource.current_uses,
            animation="bless",
            description=(
                f"{member.state.template.name} uses Sacred Weapon on "
                f"{member.state.template.weapon_attack.weapon.name}, gaining +{bonus} to its attack rolls."
            ),
        )
    except Exception:
        logger.exception("Failed to resolve Sacred Weapon for %s", member.combatant_id)
        raise
