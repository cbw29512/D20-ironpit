from __future__ import annotations

import logging
from typing import Literal

from app.combat.action_economy import is_available
from app.combat.condition_rules import has_condition
from app.combat.encounter_targeting import combatant_distance
from app.combat.hit_points import effective_max_hp
from app.combat.spellcasting import slot_spell_available
from app.combat.suppression_zone_geometry import verbal_casting_blocked
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.timed_self_buffs import TimedSelfBuffAction

logger = logging.getLogger(__name__)


def timed_self_buff_resource(
    member: EncounterCombatant,
    action: TimedSelfBuffAction,
):
    try:
        if action.resource_id is None:
            return None
        return next(
            (item for item in member.state.resources if item.id == action.resource_id),
            None,
        )
    except Exception as exc:
        logger.exception(
            "Timed self-buff resource lookup failed for %s.",
            member.combatant_id,
        )
        raise RuntimeError("Timed self-buff resource could not be resolved.") from exc


def concentration_grant_only(action: TimedSelfBuffAction) -> bool:
    """True when the Action only starts Concentration and has no other live buff."""
    try:
        return bool(action.concentration) and not (
            action.condition_ids
            or action.damage_resistances
            or action.debuff_counters
            or action.saving_throw_advantage_grants
            or action.movement_mode_grants
            or action.friendly_save_advantage_aura
            or action.friendly_cover_aura
            or action.friendly_weapon_damage_aura
            or action.friendly_recovery_aura
            or action.hostile_start_turn_condition_aura
            or action.start_turn_emanation_damage
            or action.emitted_environment_contexts
            or action.melee_hit_retaliation
            or action.spell_save_dc_bonus
            or action.spell_attack_advantage
        )
    except Exception:
        logger.exception("Failed concentration-grant-only check for %s.", action.id)
        raise


def timed_self_buff_active(
    member: EncounterCombatant,
    action: TimedSelfBuffAction,
) -> bool:
    try:
        return (
            action.id in member.state.active_effect_ids
            or any(
                effect.source_id == member.combatant_id
                and effect.source_effect_id == action.id
                for effect in member.state.timed_effects
            )
        )
    except Exception as exc:
        logger.exception(
            "Timed self-buff activity lookup failed for %s.",
            member.combatant_id,
        )
        raise RuntimeError("Timed self-buff activity could not be evaluated.") from exc


def sync_hp_ended_self_buffs(state) -> list[str]:
    """End existing self-buff states whose source says full HP ends them."""
    try:
        if state.current_hp < effective_max_hp(state):
            return []
        ended = [
            action.id for action in state.template.timed_self_buff_actions
            if action.ends_at_full_hp and action.id in state.active_effect_ids
        ]
        if ended:
            state.active_effect_ids = [
                effect_id for effect_id in state.active_effect_ids if effect_id not in ended
            ]
            state.timed_effects = [
                effect for effect in state.timed_effects
                if effect.effect_id not in ended and effect.source_effect_id not in ended
            ]
        return ended
    except Exception as exc:
        logger.exception("Failed full-HP self-buff cleanup for %s.", state.template.name)
        raise RuntimeError("Self-buff HP lifecycle could not be evaluated.") from exc


def _friendly_aura_is_relevant(
    member: EncounterCombatant,
    action: TimedSelfBuffAction,
    setup: EncounterSetup | None,
) -> bool:
    try:
        if action.friendly_weapon_damage_aura is not None:
            return False
        recovery = action.friendly_recovery_aura
        if recovery is not None:
            if setup is None:
                return False
            allies = setup.heroes if member.side == "heroes" else setup.monsters
            return any(
                target.state.is_alive
                and not target.state.is_dead
                and combatant_distance(member, target) <= recovery.radius_ft
                and target.state.current_hp <= 0
                for target in allies
            )
        aura = action.friendly_save_advantage_aura
        if aura is None:
            return True
        if aura.all_saves or aura.attacks_against_disadvantage:
            return False
        if setup is None:
            return False
        allies = setup.heroes if member.side == "heroes" else setup.monsters
        for target in allies:
            if target.state.is_dead or not target.state.is_alive:
                continue
            if combatant_distance(member, target) > aura.radius_ft:
                continue
            if aura.requires_hearing and has_condition(target.state, "deafened"):
                continue
            if any(has_condition(target.state, tag) for tag in aura.required_effect_tags):
                return True
        return False
    except Exception as exc:
        logger.exception(
            "Timed friendly save-aura relevance check failed for %s.",
            member.combatant_id,
        )
        raise RuntimeError("Timed self-buff relevance could not be evaluated.") from exc


def _hostile_aura_is_relevant(
    member: EncounterCombatant,
    action: TimedSelfBuffAction,
    setup: EncounterSetup | None,
) -> bool:
    aura = action.hostile_start_turn_condition_aura
    if aura is None:
        return True
    if setup is None:
        return False
    enemies = setup.monsters if member.side == "heroes" else setup.heroes
    return any(
        target.state.is_alive
        and not target.state.is_dead
        and combatant_distance(member, target) <= aura.radius_ft
        for target in enemies
    )


def choose_timed_self_buff_action(
    member: EncounterCombatant,
    setup: EncounterSetup | None = None,
    *,
    activation_timing: Literal["action", "start_turn"] = "action",
    turn_key: str | None = None,
) -> TimedSelfBuffAction | None:
    """Choose the highest-priority legal inactive tactically relevant self-buff."""
    try:
        choices: list[TimedSelfBuffAction] = []
        for action in member.state.template.timed_self_buff_actions:
            resource = timed_self_buff_resource(member, action)
            if (
                action.activation_timing == activation_timing
                and (
                    activation_timing == "start_turn"
                    or is_available(member.state, action.action_cost)
                )
                and (
                    action.resource_id is None
                    or (
                        resource is not None
                        and resource.current_uses >= action.resource_cost
                    )
                )
                and (
                    action.start_turn_max_current_hp is None
                    or member.state.current_hp <= action.start_turn_max_current_hp
                )
                and not timed_self_buff_active(member, action)
                and (not action.concentration or member.state.concentration is None)
                and not (
                    action.resource_id
                    and action.resource_id.startswith("spell-slot-")
                    and setup is not None
                    and verbal_casting_blocked(member, setup)
                )
                and not (
                    action.resource_id
                    and action.resource_id.startswith("spell-slot-")
                    and turn_key is not None
                    and not slot_spell_available(member.state, turn_key)
                )
                and not concentration_grant_only(action)
                and _friendly_aura_is_relevant(member, action, setup)
                and _hostile_aura_is_relevant(member, action, setup)
            ):
                choices.append(action)
        return max(choices, key=lambda item: item.priority, default=None)
    except Exception as exc:
        logger.exception("Timed self-buff choice failed for %s.", member.combatant_id)
        raise RuntimeError("Timed self-buff policy could not be evaluated.") from exc
