from __future__ import annotations

import logging

from app.combat.condition_rules import is_incapacitated
from app.combat.dice import roll_dice
from app.combat.encounter_targeting import combatant_distance
from app.combat.hit_points import effective_max_hp
from app.combat.timed_conditions import apply_timed_condition
from app.combat.zero_hp import restore_hit_points
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.timed_self_buffs import TimedSelfBuffAction

logger = logging.getLogger(__name__)
_SHARE = "recovery-share"


def _members(setup: EncounterSetup) -> list[EncounterCombatant]:
    return [*setup.heroes, *setup.monsters]


def _allies(source: EncounterCombatant, setup: EncounterSetup) -> list[EncounterCombatant]:
    return setup.heroes if source.side == "heroes" else setup.monsters


def _active(source: EncounterCombatant, action_id: str) -> bool:
    state = source.state
    if state.is_dead or not state.is_alive or state.current_hp <= 0 or is_incapacitated(state):
        return False
    return any(
        effect.source_id == source.combatant_id and effect.source_effect_id == action_id
        for effect in state.timed_effects
    )


def _in_aura(source: EncounterCombatant, target: EncounterCombatant, radius_ft: int) -> bool:
    return combatant_distance(source, target) <= radius_ft


def choose_recovery_heal_target(
    source: EncounterCombatant,
    setup: EncounterSetup,
    radius_ft: int,
) -> EncounterCombatant | None:
    """Pick the most wounded living creature currently inside the aura."""
    try:
        candidates = []
        for target in _allies(source, setup):
            if target.state.is_dead or not target.state.is_alive:
                continue
            if not _in_aura(source, target, radius_ft):
                continue
            missing = effective_max_hp(target.state) - target.state.current_hp
            if missing <= 0:
                continue
            candidates.append((target.state.current_hp > 0, -missing, target.combatant_id, target))
        if not candidates:
            return None
        return min(candidates, key=lambda item: item[:3])[3]
    except Exception:
        logger.exception("Failed recovery-aura target choice for %s.", source.combatant_id)
        raise


def heal_recovery_aura_target(
    source: EncounterCombatant,
    action: TimedSelfBuffAction,
    setup: EncounterSetup | None,
    dice,
) -> int:
    """Restore printed aura HP to one creature inside the emanation."""
    try:
        aura = action.friendly_recovery_aura
        if aura is None or setup is None or dice is None:
            return 0
        if not (aura.heal_dice_count or aura.heal_flat):
            return 0
        target = choose_recovery_heal_target(source, setup, aura.radius_ft)
        if target is None:
            return 0
        total = aura.heal_flat
        if aura.heal_dice_count:
            total += roll_dice(dice, aura.heal_dice_count, aura.heal_dice_size)
        return restore_hit_points(target.state, total)
    except Exception:
        logger.exception("Failed recovery-aura heal for %s.", source.combatant_id)
        raise


def activate_source_recovery_aura(
    source: EncounterCombatant,
    action: TimedSelfBuffAction,
    setup: EncounterSetup | None,
    dice,
    *,
    round_number: int,
) -> None:
    """Stamp source-owned recovery flags and apply the printed create-window heal."""
    try:
        aura = action.friendly_recovery_aura
        if aura is None:
            return
        for effect in source.state.timed_effects:
            if effect.source_id == source.combatant_id and effect.source_effect_id == action.id:
                effect.prevent_hit_point_maximum_reduction = aura.prevent_hp_maximum_reduction
        if aura.heal_on_create:
            heal_recovery_aura_target(source, action, setup, dice)
        if setup is not None:
            sync_friendly_recovery_auras(setup)
    except Exception:
        logger.exception("Failed to activate recovery aura %s.", action.id)
        raise


def sync_friendly_recovery_auras(setup: EncounterSetup) -> None:
    """Share necrotic Resistance and HP-max lock with allies currently inside the aura."""
    try:
        for member in _members(setup):
            member.state.timed_effects = [
                effect for effect in member.state.timed_effects
                if effect.source_effect_id != _SHARE
            ]
            if _SHARE in member.state.active_effect_ids and not any(
                effect.effect_id == _SHARE for effect in member.state.timed_effects
            ):
                member.state.active_effect_ids = [
                    item for item in member.state.active_effect_ids if item != _SHARE
                ]
        for source in _members(setup):
            for action in source.state.template.timed_self_buff_actions:
                aura = action.friendly_recovery_aura
                if aura is None or not _active(source, action.id):
                    continue
                if not (aura.necrotic_resistance or aura.prevent_hp_maximum_reduction):
                    continue
                for target in _allies(source, setup):
                    if target.combatant_id == source.combatant_id:
                        continue
                    if target.state.is_dead or not target.state.is_alive:
                        continue
                    if not _in_aura(source, target, aura.radius_ft):
                        continue
                    apply_timed_condition(
                        target.state,
                        _SHARE,
                        source.combatant_id,
                        source_effect_id=_SHARE,
                        source_template=source.state.template,
                        source_is_magical=True,
                        applied_round=source.state.current_round,
                        owned_damage_resistances=["necrotic"] if aura.necrotic_resistance else [],
                        use_default_poison_recovery=False,
                    )
                    for effect in target.state.timed_effects:
                        if effect.effect_id == _SHARE and effect.source_id == source.combatant_id:
                            effect.prevent_hit_point_maximum_reduction = (
                                aura.prevent_hp_maximum_reduction
                            )
    except Exception:
        logger.exception("Failed to synchronize friendly recovery auras.")
        raise


def aura_is_active(source: EncounterCombatant, action_id: str) -> bool:
    return _active(source, action_id)


def target_in_aura(source: EncounterCombatant, target: EncounterCombatant, radius_ft: int) -> bool:
    return _in_aura(source, target, radius_ft)


def encounter_members(setup: EncounterSetup) -> list[EncounterCombatant]:
    return _members(setup)
