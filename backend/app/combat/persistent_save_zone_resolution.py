from __future__ import annotations

import logging

from app.combat.damage_defenses import apply_damage_defenses
from app.combat.persistent_save_zone_geometry import member_in_save_zone
from app.combat.saving_throw_rolls import resolve_saving_throw
from app.combat.timed_conditions import apply_timed_condition
from app.combat.zero_hp import apply_damage
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import BattleEvent, DamageRollComponent, DamageType, DiceRoll
from app.domain.persistent_save_zones import PersistentSaveZoneState
from app.domain.saving_throw_context import SavingThrowContext

logger = logging.getLogger(__name__)


def expire_save_zones(setup: EncounterSetup, round_number: int) -> None:
    try:
        setup.save_zones = [zone for zone in setup.save_zones if zone.expires_round > round_number]
    except Exception:
        logger.exception("Failed to expire save zones at round %s.", round_number)
        raise


def resolve_save_zone_trigger(
    sequence: int,
    round_number: int,
    target: EncounterCombatant,
    setup: EncounterSetup,
    zone: PersistentSaveZoneState,
    dice,
    turn_key: str,
    trigger: str,
) -> tuple[list[BattleEvent], int]:
    try:
        if trigger not in zone.triggers or not member_in_save_zone(target, zone):
            return [], sequence
        if target.combatant_id == zone.source_id or target.side == zone.source_side:
            return [], sequence
        if not target.state.is_alive or target.state.is_dead or target.state.current_hp <= 0:
            return [], sequence
        if zone.once_per_turn and zone.triggered_turn_keys.get(target.combatant_id) == turn_key:
            return [], sequence
        if zone.once_per_turn:
            zone.triggered_turn_keys[target.combatant_id] = turn_key
        requires_save = not zone.save_triggers or trigger in zone.save_triggers
        roll, succeeded = (None, False)
        if requires_save:
            context = SavingThrowContext(magical_effect=True, spell_effect=True)
            roll, succeeded = resolve_saving_throw(target.state, zone.save_ability, zone.dc, dice, context)
        hp_before = target.state.current_hp
        applied_total = 0
        components = []
        damage_roll = None
        if zone.damage_dice_count and zone.damage_type is not None:
            rolls = [dice.roll(zone.damage_dice_size) for _ in range(zone.damage_dice_count)]
            raw_total = sum(rolls)
            if succeeded and zone.success_damage == "none":
                raw_total = 0
            elif succeeded and zone.success_damage == "half":
                raw_total //= 2
            raw = DamageRollComponent(
                source=zone.action_id,
                notation=f"{zone.damage_dice_count}d{zone.damage_dice_size}",
                rolls=rolls,
                modifier=0,
                damage_type=zone.damage_type,
                total=raw_total,
            )
            applied_total, components = apply_damage_defenses(target.state, [raw])
            damage_roll = DiceRoll(notation=raw.notation, rolls=rolls, modifier=0, total=applied_total)
            if applied_total:
                apply_damage(
                    target.state,
                    applied_total,
                    damage_types={DamageType(zone.damage_type)},
                    dice=dice,
                    affected_states=[member.state for member in [*setup.heroes, *setup.monsters]],
                    setup=setup,
                )
        applied_conditions = []
        if not succeeded and zone.failed_save_condition_id and target.state.is_alive:
            applied = apply_timed_condition(
                target.state,
                zone.failed_save_condition_id,
                zone.source_id,
                source_effect_id=zone.action_id,
                applied_round=round_number,
                expires_round=round_number + zone.failed_save_duration_rounds,
                expiry_timing="target_turn_end",
                suppress_action=zone.failed_save_suppress_action,
                suppress_bonus_action=zone.failed_save_suppress_bonus_action,
                use_default_poison_recovery=False,
            )
            if applied is not None:
                applied_conditions.append(applied)
        event = BattleEvent(
            sequence=sequence,
            round_number=round_number,
            event_type="saving_throw",
            actor_id=zone.source_id,
            actor_name=zone.action_name,
            target_id=target.combatant_id,
            target_name=target.state.template.name,
            saving_throw_roll=roll,
            save_ability=zone.save_ability,
            save_dc=zone.dc,
            save_succeeded=succeeded,
            damage_roll=damage_roll,
            damage_components=components,
            applied_condition_ids=applied_conditions,
            hp_before=hp_before,
            hp_after=target.state.current_hp,
            is_dead=target.state.is_dead,
            feature_id=zone.action_id,
            animation=zone.animation,
            description=(
                f"{target.state.template.name} takes damage from {zone.action_name} with no save."
                if not requires_save else
                f"{target.state.template.name} {'succeeds' if succeeded else 'fails'} "
                f"the save against {zone.action_name}."
            ),
        )
        return [event], sequence + 1
    except Exception:
        logger.exception("Failed save-zone trigger %s for %s.", trigger, target.combatant_id)
        raise
