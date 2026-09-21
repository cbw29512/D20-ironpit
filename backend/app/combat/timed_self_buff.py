from __future__ import annotations

import logging

from app.combat.action_economy import is_available, spend
from app.combat.modifier_stack import add_modifier
from app.combat.timed_conditions import apply_timed_condition
from app.domain.encounters import EncounterCombatant
from app.domain.models import BattleEvent, DamageType
from app.domain.modifiers import CombatModifier, ModifierKind

logger = logging.getLogger(__name__)


def can_activate_timed_self_buff(actor: EncounterCombatant) -> bool:
    rule = actor.state.template.progression_features.timed_self_buff
    if rule is None or not is_available(actor.state, "action"):
        return False
    if any(item.source_effect_id == rule.source_id for item in actor.state.timed_effects):
        return False
    resource = next((item for item in actor.state.resources if item.id == rule.resource_id), None)
    return resource is not None and resource.current_uses >= rule.resource_cost


def resolve_timed_self_buff(
    sequence: int, round_number: int, actor: EncounterCombatant,
) -> BattleEvent | None:
    try:
        if not can_activate_timed_self_buff(actor):
            return None
        rule = actor.state.template.progression_features.timed_self_buff
        assert rule is not None
        resource = next(item for item in actor.state.resources if item.id == rule.resource_id)
        resource.current_uses -= rule.resource_cost
        spend(actor.state, "action")
        expires = round_number + rule.duration_rounds
        for effect_id in rule.effect_ids:
            apply_timed_condition(
                actor.state, effect_id, actor.combatant_id,
                source_effect_id=rule.source_id, applied_round=round_number,
                expires_round=expires, expiry_timing="source_turn_start",
            )
        for damage_type in rule.damage_resistances:
            add_modifier(actor.state, CombatModifier(
                id=f"{actor.combatant_id}:{rule.source_id}:resistance:{damage_type}",
                source_id=actor.combatant_id, source_effect_id=rule.source_id,
                kind=ModifierKind.DAMAGE_RESISTANCE, damage_type=DamageType(damage_type),
            ))
        return BattleEvent(
            sequence=sequence, round_number=round_number, event_type="feature",
            actor_id=actor.combatant_id, actor_name=actor.state.template.name,
            target_id=actor.combatant_id, target_name=actor.state.template.name,
            feature_id=rule.source_id, resource_remaining=resource.current_uses,
            animation="buff",
            description=f"{actor.state.template.name} activates {rule.source_id.replace('-', ' ').title()}.",
        )
    except Exception as exc:
        logger.exception("Timed self-buff activation failed for %s.", actor.combatant_id)
        raise RuntimeError("Timed self-buff could not be activated.") from exc
