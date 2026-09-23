from __future__ import annotations

import logging

from app.combat.action_economy import is_available, spend
from app.combat.damage_defenses import apply_damage_defenses
from app.combat.saving_throw_rolls import resolve_saving_throw
from app.combat.zero_hp import apply_damage, reduce_to_zero_hit_points
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import BattleEvent, DamageRollComponent, DamageType, DiceRoll
from app.domain.runtime import CombatantState, DeferredEffectState

logger = logging.getLogger(__name__)


def arm_deferred_save_effect(
    attacker: CombatantState,
    target_id: str,
    trigger_attack_id: str,
) -> str | None:
    """Arm the configured deferred effect after a qualifying hit and spend its setup resource."""
    try:
        rule = attacker.template.progression_features.deferred_save_effect
        if rule is None or trigger_attack_id not in rule.trigger_attack_ids:
            return None
        resource = next((item for item in attacker.resources if item.id == rule.resource_id), None)
        if resource is None:
            raise ValueError(
                f"Deferred effect {rule.source_id} references missing resource {rule.resource_id}."
            )
        if resource.current_uses < rule.resource_cost:
            return None
        if any(item.source_id == rule.source_id for item in attacker.deferred_effects):
            return None
        resource.current_uses -= rule.resource_cost
        attacker.deferred_effects.append(
            DeferredEffectState(source_id=rule.source_id, target_id=target_id)
        )
        return rule.source_name
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Failed to arm deferred save effect for %s.", attacker.template.name)
        raise RuntimeError("Deferred save effect could not be armed.") from exc


def _target(setup: EncounterSetup, target_id: str) -> EncounterCombatant | None:
    return next(
        (member for member in [*setup.heroes, *setup.monsters] if member.combatant_id == target_id),
        None,
    )


def deferred_save_effect_candidate(
    actor: EncounterCombatant,
    setup: EncounterSetup,
) -> EncounterCombatant | None:
    """Return the marked living target when the deferred Action is legal."""
    rule = actor.state.template.progression_features.deferred_save_effect
    if rule is None or not is_available(actor.state, "action"):
        return None
    mark = next(
        (item for item in actor.state.deferred_effects if item.source_id == rule.source_id),
        None,
    )
    if mark is None:
        return None
    target = _target(setup, mark.target_id)
    if target is None or target.state.is_dead or not target.state.is_alive or target.state.current_hp <= 0:
        actor.state.deferred_effects = [
            item for item in actor.state.deferred_effects if item.source_id != rule.source_id
        ]
        return None
    return target


def resolve_deferred_save_effect(
    sequence: int,
    round_number: int,
    actor: EncounterCombatant,
    setup: EncounterSetup,
    dice,
) -> BattleEvent | None:
    """Activate one marked target through shared save, damage, and zero-HP rules."""
    try:
        target = deferred_save_effect_candidate(actor, setup)
        if target is None:
            return None
        rule = actor.state.template.progression_features.deferred_save_effect
        assert rule is not None
        hp_before = target.state.current_hp
        temp_before = target.state.temporary_hp
        death_success_before = target.state.death_save_successes
        death_failure_before = target.state.death_save_failures
        roll, succeeded = resolve_saving_throw(
            target.state, rule.save_ability, rule.save_dc, dice
        )
        affected = [member.state for member in [*setup.heroes, *setup.monsters]]
        damage_roll = None
        components: list[DamageRollComponent] = []
        if succeeded and rule.success_damage_dice_count:
            if not rule.success_damage_type:
                raise ValueError(
                    f"Deferred effect {rule.source_id} has damage dice but no damage type."
                )
            rolls = [
                dice.roll(rule.success_damage_dice_size)
                for _ in range(rule.success_damage_dice_count)
            ]
            total = sum(rolls)
            damage_type = DamageType(rule.success_damage_type)
            raw = DamageRollComponent(
                source=rule.source_name,
                notation=f"{rule.success_damage_dice_count}d{rule.success_damage_dice_size}",
                rolls=rolls,
                modifier=0,
                damage_type=damage_type,
                total=total,
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
                target.state, dice=dice, affected_states=affected
            )
        spend(actor.state, "action")
        actor.state.deferred_effects = [
            item for item in actor.state.deferred_effects if item.source_id != rule.source_id
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
