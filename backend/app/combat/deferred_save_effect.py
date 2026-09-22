from __future__ import annotations

from dataclasses import dataclass
import logging

from app.combat.action_economy import is_available, spend
from app.combat.damage_defenses import apply_damage_defenses
from app.combat.saving_throw_rolls import resolve_saving_throw
from app.combat.zero_hp import apply_damage, reduce_to_zero_hit_points
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import BattleEvent, CombatantState, DamageRollComponent, DamageType, DiceRoll, WeaponAttack
from app.domain.runtime import DeferredEffectState

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class DeferredEffectArmResult:
    source_id: str
    source_name: str
    target_id: str
    resource_remaining: int
    armed_round: int


def arm_deferred_save_effect(
    attacker: CombatantState,
    defender: CombatantState,
    target_id: str,
    attack: WeaponAttack,
    round_number: int,
) -> DeferredEffectArmResult | None:
    """Arm one declarative deferred effect after a qualifying successful hit."""
    try:
        rule = attacker.template.progression_features.deferred_save_effect
        if rule is None or attack.weapon.id not in rule.trigger_weapon_ids:
            return None
        if defender.is_dead or not defender.is_alive or defender.current_hp <= 0:
            return None
        active = [item for item in attacker.deferred_effects if item.source_id == rule.source_id]
        if len(active) >= rule.max_active_targets:
            return None
        resource = next((item for item in attacker.resources if item.id == rule.resource_id), None)
        if resource is None:
            raise ValueError(
                f"Deferred effect {rule.source_id} references missing resource {rule.resource_id}."
            )
        if resource.current_uses < rule.resource_cost:
            return None
        resource.current_uses -= rule.resource_cost
        attacker.deferred_effects.append(
            DeferredEffectState(
                source_id=rule.source_id,
                target_id=target_id,
                armed_round=round_number,
            )
        )
        return DeferredEffectArmResult(
            source_id=rule.source_id,
            source_name=rule.source_name,
            target_id=target_id,
            resource_remaining=resource.current_uses,
            armed_round=round_number,
        )
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Failed to arm deferred save effect for %s.", attacker.template.name)
        raise RuntimeError("Deferred save effect could not be armed.") from exc


def cleanup_deferred_effects(setup: EncounterSetup) -> None:
    """Remove armed marks whose target no longer exists or can no longer be affected."""
    try:
        members = [*setup.heroes, *setup.monsters]
        by_id = {member.combatant_id: member for member in members}
        for source in members:
            source.state.deferred_effects = [
                mark
                for mark in source.state.deferred_effects
                if (
                    (target := by_id.get(mark.target_id)) is not None
                    and target.state.is_alive
                    and not target.state.is_dead
                    and target.state.current_hp > 0
                )
            ]
    except Exception as exc:
        logger.exception("Failed deferred-effect lifecycle cleanup.")
        raise RuntimeError("Deferred-effect lifecycle cleanup failed.") from exc


def deferred_save_effect_candidate(
    actor: EncounterCombatant,
    setup: EncounterSetup,
) -> EncounterCombatant | None:
    """Return the first living marked target when the deferred Action is legal."""
    try:
        rule = actor.state.template.progression_features.deferred_save_effect
        if rule is None or not is_available(actor.state, "action"):
            return None
        members = [*setup.heroes, *setup.monsters]
        by_id = {member.combatant_id: member for member in members}
        for mark in actor.state.deferred_effects:
            if mark.source_id != rule.source_id:
                continue
            target = by_id.get(mark.target_id)
            if target is not None and target.state.is_alive and not target.state.is_dead and target.state.current_hp > 0:
                return target
        return None
    except Exception as exc:
        logger.exception("Failed to select deferred save effect target for %s.", actor.combatant_id)
        raise RuntimeError("Deferred save effect target could not be selected.") from exc


def resolve_deferred_save_effect(
    sequence: int,
    round_number: int,
    actor: EncounterCombatant,
    setup: EncounterSetup,
    dice,
) -> BattleEvent | None:
    """Resolve an armed effect through shared save, typed damage, and zero-HP lifecycles."""
    try:
        target = deferred_save_effect_candidate(actor, setup)
        if target is None:
            return None
        rule = actor.state.template.progression_features.deferred_save_effect
        if rule is None:
            raise ValueError("Deferred effect candidate exists without immutable source data.")

        hp_before = target.state.current_hp
        temp_before = target.state.temporary_hp
        death_success_before = target.state.death_save_successes
        death_failure_before = target.state.death_save_failures
        roll, succeeded = resolve_saving_throw(target.state, rule.save_ability, rule.save_dc, dice)
        affected = [member.state for member in [*setup.heroes, *setup.monsters]]
        damage_roll = None
        components: list[DamageRollComponent] = []

        if succeeded and rule.success_damage_dice_count:
            if rule.success_damage_type is None:
                raise ValueError(f"Deferred effect {rule.source_id} has damage dice without a damage type.")
            rolls = [
                dice.roll(rule.success_damage_dice_size)
                for _ in range(rule.success_damage_dice_count)
            ]
            raw_total = sum(rolls)
            damage_type = DamageType(rule.success_damage_type)
            raw = DamageRollComponent(
                source=rule.source_name,
                notation=f"{rule.success_damage_dice_count}d{rule.success_damage_dice_size}",
                rolls=rolls,
                modifier=0,
                damage_type=damage_type,
                total=raw_total,
            )
            applied, components = apply_damage_defenses(target.state, [raw])
            apply_damage(
                target.state,
                applied,
                damage_types={damage_type},
                dice=dice,
                affected_states=affected,
            )
            damage_roll = DiceRoll(
                notation=raw.notation,
                rolls=rolls,
                modifier=0,
                total=applied,
            )
        elif not succeeded and rule.failure_sets_zero_hp:
            reduce_to_zero_hit_points(
                target.state,
                dice=dice,
                affected_states=affected,
            )

        spend(actor.state, "action")
        actor.state.deferred_effects = [
            item for item in actor.state.deferred_effects
            if not (item.source_id == rule.source_id and item.target_id == target.combatant_id)
        ]
        description = (
            f"{actor.state.template.name} activates {rule.source_name} on "
            f"{target.state.template.name}; the {rule.save_ability.title()} save "
            f"{'succeeds' if succeeded else 'fails'}."
        )
        return BattleEvent(
            sequence=sequence,
            round_number=round_number,
            event_type="feature",
            actor_id=actor.combatant_id,
            actor_name=actor.state.template.name,
            target_id=target.combatant_id,
            target_name=target.state.template.name,
            saving_throw_roll=roll,
            save_ability=rule.save_ability,
            save_dc=rule.save_dc,
            save_succeeded=succeeded,
            damage_roll=damage_roll,
            damage_components=components,
            hp_before=hp_before,
            hp_after=target.state.current_hp,
            temporary_hp_before=temp_before,
            temporary_hp_after=target.state.temporary_hp,
            death_save_successes_before=death_success_before,
            death_save_failures_before=death_failure_before,
            death_save_successes=target.state.death_save_successes,
            death_save_failures=target.state.death_save_failures,
            is_stable=target.state.is_stable,
            is_dead=target.state.is_dead,
            feature_id=rule.source_id,
            animation="save-effect",
            description=description,
        )
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Failed to resolve deferred save effect for %s.", actor.combatant_id)
        raise RuntimeError("Deferred save effect could not be resolved.") from exc
