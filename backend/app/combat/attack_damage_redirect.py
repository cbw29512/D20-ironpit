from __future__ import annotations

import logging

from app.combat.barrier_line_of_effect import clear_line_between_members
from app.combat.condition_rules import can_see
from app.combat.encounter_targeting import combatant_distance
from app.combat.saving_throws import resolve_save_action
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import BattleEvent, SavingThrowAction, WeaponAttack

logger = logging.getLogger(__name__)


def _attack_by_id(source: EncounterCombatant, attack_id: str | None) -> WeaponAttack | None:
    try:
        if not attack_id:
            return None
        attacks = [source.state.template.weapon_attack, *source.state.template.alternate_weapon_attacks]
        return next((attack for attack in attacks if attack.id == attack_id), None)
    except Exception as exc:
        logger.exception("Failed to resolve triggering attack %s.", attack_id)
        raise RuntimeError("Triggering attack lookup failed.") from exc


def _legal_targets(
    reactor: EncounterCombatant,
    setup: EncounterSetup,
    range_ft: int,
    *,
    requires_sight: bool,
    requires_clear_line: bool,
) -> list[EncounterCombatant]:
    try:
        opponents = setup.monsters if reactor.side == "heroes" else setup.heroes
        targets = []
        for target in opponents:
            if not target.state.is_alive or target.state.is_dead or target.state.current_hp <= 0:
                continue
            distance = combatant_distance(reactor, target)
            if distance > range_ft:
                continue
            if requires_sight and not can_see(reactor.state, target.state, distance):
                continue
            if requires_clear_line and not clear_line_between_members(reactor, target, setup):
                continue
            targets.append(target)
        return sorted(targets, key=lambda item: (combatant_distance(reactor, item), item.combatant_id))
    except Exception as exc:
        logger.exception("Failed to select zero-damage redirect targets for %s.", reactor.combatant_id)
        raise RuntimeError("Zero-damage redirect targeting failed.") from exc


def resolve_attack_damage_zero_redirect(
    sequence: int,
    round_number: int,
    source: EncounterCombatant,
    triggering_event: BattleEvent,
    setup: EncounterSetup,
    dice,
) -> BattleEvent | None:
    """Resolve an optional save-damage follow-up after an attack reduction reaches zero."""
    try:
        if not triggering_event.damage_reduction_zeroed_attack:
            return None
        reactor = next(
            (member for member in [*setup.heroes, *setup.monsters]
             if member.combatant_id == triggering_event.target_id),
            None,
        )
        if reactor is None:
            return None
        reduction = reactor.state.template.attack_damage_reduction_reaction
        redirect = reduction.zero_damage_redirect if reduction is not None else None
        if redirect is None:
            return None
        resource = next((item for item in reactor.state.resources if item.id == redirect.resource_id), None)
        if resource is None or resource.current_uses < redirect.resource_cost:
            return None
        attack = _attack_by_id(source, triggering_event.attack_id)
        if attack is None:
            return None
        range_ft = (
            redirect.melee_range_ft
            if attack.weapon.attack_kind.value == "melee"
            else redirect.ranged_range_ft
        )
        targets = _legal_targets(
            reactor,
            setup,
            range_ft,
            requires_sight=redirect.requires_sight,
            requires_clear_line=redirect.requires_clear_line,
        )
        if not targets:
            return None
        scores = reactor.state.template.ability_scores
        if scores is None:
            raise ValueError(f"{redirect.source_name} requires certified ability scores.")
        damage_bonus = (
            scores.modifier(redirect.damage_bonus_ability)
            if redirect.damage_bonus_ability is not None else 0
        )
        action = SavingThrowAction(
            id=redirect.source_id,
            name=redirect.source_name,
            action_cost="reaction",
            save_ability=redirect.save_ability,
            dc=redirect.save_dc,
            range_ft=range_ft,
            damage_dice_count=redirect.damage_dice_count,
            damage_dice_size=redirect.damage_dice_size,
            damage_bonus=damage_bonus,
            damage_type=attack.weapon.damage_type.value,
            success_damage="none",
            resource_id=redirect.resource_id,
            resource_cost=redirect.resource_cost,
            requires_target_sight=redirect.requires_sight,
            animation="deflect",
        )
        target = targets[0]
        return resolve_save_action(
            sequence,
            round_number,
            reactor,
            target,
            action,
            combatant_distance(reactor, target),
            dice,
            spend_action=False,
            affected_states=[member.state for member in [*setup.heroes, *setup.monsters]],
            setup=setup,
        )
    except ValueError:
        raise
    except Exception as exc:
        logger.exception(
            "Failed zero-damage attack redirect after event %s.",
            triggering_event.sequence,
        )
        raise RuntimeError("Zero-damage attack redirect could not be resolved.") from exc
