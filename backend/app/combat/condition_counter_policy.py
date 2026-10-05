from __future__ import annotations

import logging

from app.combat.action_economy import is_available
from app.combat.alternate_spell_casts import available_alternate_casts
from app.combat.debuff_answers import (
    active_condition_ids,
    countered_condition_ids,
    failed_save_is_beneficial,
)
from app.combat.encounter_targeting import combatant_distance
from app.combat.spell_choice import SpellChoice
from app.combat.spell_policy import spell_at_slot
from app.combat.spellcasting import legal_slot_levels
from app.content.monster_creature_types import is_creature_type
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.spells import SpellSaveAction

logger = logging.getLogger(__name__)


def _allies(member: EncounterCombatant, setup: EncounterSetup) -> list[EncounterCombatant]:
    roster = setup.heroes if member.side == "heroes" else setup.monsters
    return [
        ally for ally in roster
        if ally.state.is_alive and not ally.state.is_dead and ally.state.current_hp > 0
    ]


def _type_ok(action: SpellSaveAction, target: EncounterCombatant) -> bool:
    template = target.state.template
    if action.required_target_creature_types and not any(
        is_creature_type(template, kind) for kind in action.required_target_creature_types
    ):
        return False
    if any(is_creature_type(template, kind) for kind in action.excluded_target_creature_types):
        return False
    return True


def _reachable(caster: EncounterCombatant, target: EncounterCombatant, action: SpellSaveAction) -> bool:
    radius = action.area.radius_ft if action.area is not None and action.area.radius_ft else (
        action.area_radius_ft or 0
    )
    return combatant_distance(caster, target) <= action.range_ft + radius


def _covered(center: EncounterCombatant, target: EncounterCombatant, action: SpellSaveAction) -> bool:
    radius = action.area.radius_ft if action.area is not None and action.area.radius_ft else (
        action.area_radius_ft or 0
    )
    if radius <= 0:
        return center.combatant_id == target.combatant_id
    return combatant_distance(center, target) <= radius


def choose_condition_counter_spell(
    caster: EncounterCombatant,
    setup: EncounterSetup,
    turn_key: str,
) -> SpellChoice | None:
    """Cast a beneficial counter-buff only when a friend still has the matching debuff."""
    try:
        if not is_available(caster.state, "action"):
            return None
        needy = [
            ally for ally in _allies(caster, setup)
            if active_condition_ids(ally.state)
        ]
        if not needy:
            return None
        for action in caster.state.template.spell_save_actions:
            answered = countered_condition_ids(action)
            if not answered or not failed_save_is_beneficial(action):
                continue
            if action.action_cost != "action" or action.cast_rounds > 1 or action.repeat_only:
                continue
            if action.concentration and caster.state.concentration is not None:
                continue
            patients = [
                ally for ally in needy
                if answered.intersection(active_condition_ids(ally.state))
                and _type_ok(action, ally)
                and _reachable(caster, ally, action)
            ]
            if not patients:
                continue
            center = patients[0]
            targets = tuple(
                ally.combatant_id for ally in _allies(caster, setup)
                if _type_ok(action, ally) and _covered(center, ally, action)
            )
            if center.combatant_id not in targets:
                continue
            slots = legal_slot_levels(
                caster.state, turn_key, action.level,
                higher_slot_scaling=False,
            )
            grants = [
                grant for grant in available_alternate_casts(caster.state, action.id)
            ]
            if grants:
                grant = grants[0]
                return SpellChoice(
                    action=spell_at_slot(action, grant.cast_level),
                    slot_level=grant.cast_level,
                    target_ids=targets,
                    expected_damage=0.0,
                    alternate_cast=grant,
                )
            if action.level == 0 or slots:
                slot_level = 0 if action.level == 0 else min(slots)
                return SpellChoice(
                    action=spell_at_slot(action, slot_level),
                    slot_level=slot_level,
                    target_ids=targets,
                    expected_damage=0.0,
                )
        return None
    except Exception:
        logger.exception("Failed condition-counter choice for %s.", caster.combatant_id)
        raise
