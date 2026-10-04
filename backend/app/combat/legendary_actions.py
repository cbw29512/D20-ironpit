from __future__ import annotations

import logging

from app.combat.attacks import resolve_attack
from app.combat.condition_rules import is_incapacitated
from app.combat.encounter_targeting import combatant_distance, living_opponents
from app.combat.resources import resource_available, spend_resource
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.legendary_actions import LegendaryActionOption
from app.domain.models import BattleEvent, WeaponAttack

logger = logging.getLogger(__name__)
RESOURCE_ID = "legendary-actions"


def _attack_for(member: EncounterCombatant, attack_id: str) -> WeaponAttack | None:
    attacks = [member.state.template.weapon_attack, *member.state.template.alternate_weapon_attacks]
    return next((item for item in attacks if item.id == attack_id), None)


def _attack_damage(attack: WeaponAttack) -> int:
    if attack.fixed_damage is not None:
        return attack.fixed_damage + attack.damage_bonus
    return attack.weapon.dice_count * ((attack.weapon.dice_size + 1) // 2) + attack.damage_bonus


def choose_legendary_attack(
    actor: EncounterCombatant,
    setup: EncounterSetup,
) -> tuple[LegendaryActionOption, EncounterCombatant, WeaponAttack] | None:
    """Pick the highest-damage landable legendary attack the actor can afford."""
    try:
        if is_incapacitated(actor.state) or actor.state.is_dead or actor.state.current_hp <= 0:
            return None
        options = [
            item for item in actor.state.template.legendary_actions
            if item.kind == "attack" and resource_available(actor.state, RESOURCE_ID, item.cost)
        ]
        if not options:
            return None
        best: tuple[LegendaryActionOption, EncounterCombatant, WeaponAttack] | None = None
        best_damage = -1
        for option in options:
            attack = _attack_for(actor, option.attack_id)
            if attack is None:
                raise ValueError(f"{actor.state.template.name} legendary action {option.id} references missing attack {option.attack_id}.")
            reach = attack.weapon.reach_ft
            for target in living_opponents(actor, setup):
                if combatant_distance(actor, target) > reach:
                    continue
                damage = _attack_damage(attack)
                if damage > best_damage:
                    best = (option, target, attack)
                    best_damage = damage
        return best
    except Exception:
        logger.exception("Failed to choose a legendary action for %s.", actor.combatant_id)
        raise


def resolve_legendary_actions_after_turn(
    sequence: int,
    round_number: int,
    just_acted: EncounterCombatant,
    setup: EncounterSetup,
    dice,
) -> tuple[list[BattleEvent], int]:
    """Each other combatant may spend one legendary action option after this turn."""
    try:
        events: list[BattleEvent] = []
        others = [
            item for item in [*setup.heroes, *setup.monsters]
            if item.combatant_id != just_acted.combatant_id
        ]
        for actor in others:
            choice = choose_legendary_attack(actor, setup)
            if choice is None:
                continue
            option, target, attack = choice
            spend_resource(actor.state, RESOURCE_ID, option.cost)
            event = resolve_attack(
                sequence, round_number, actor.state, target.state, attack,
                combatant_distance(actor, target), dice,
                actor_event_id=actor.combatant_id, target_event_id=target.combatant_id,
                spend_action=False, off_turn=True, feature_id=option.id,
                affected_states=[item.state for item in [*setup.heroes, *setup.monsters]],
                reaction_setup=setup, reaction_roller=actor,
            )
            event = event.model_copy(update={
                "description": f"{actor.state.template.name} uses Legendary Action: {option.name}. {event.description}",
            })
            events.append(event)
            sequence += 1
        return events, sequence
    except Exception:
        logger.exception("Failed legendary actions after %s.", just_acted.combatant_id)
        raise
