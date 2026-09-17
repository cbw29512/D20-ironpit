from __future__ import annotations

import logging

from app.combat.action_economy import is_available, spend
from app.combat.dice import DiceProvider
from app.combat.encounter_targeting import combatant_distance
from app.combat.sacred_weapon_2014 import resolve_sacred_weapon
from app.combat.saving_throw_rolls import resolve_saving_throw
from app.combat.turn_creature_effects import apply_turned_creature_effects
from app.content.character_math import proficiency_bonus
from app.content.monster_creature_types import is_creature_type
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import BattleEvent

logger = logging.getLogger(__name__)
_CHANNEL = "channel-divinity"
_TURN_UNHOLY = "turn-the-unholy"
_TURNED = "turned-unholy"


def _resource(member: EncounterCombatant):
    return next((item for item in member.state.resources if item.id == _CHANNEL), None)


def _save_dc(member: EncounterCombatant) -> int:
    level = member.state.template.level
    scores = member.state.template.ability_scores
    if level is None or scores is None:
        raise ValueError("Turn the Unholy requires certified character level and ability scores.")
    return 8 + proficiency_bonus(level) + scores.modifier("charisma")


def legal_unholy_targets(member: EncounterCombatant, setup: EncounterSetup) -> tuple[EncounterCombatant, ...]:
    enemies = setup.monsters if member.side == "heroes" else setup.heroes
    return tuple(
        target for target in enemies
        if target.state.is_alive and not target.state.is_dead and target.state.current_hp > 0
        and combatant_distance(member, target) <= 30
        and any(is_creature_type(target.state.template, creature_type) for creature_type in ("fiend", "undead"))
    )


def resolve_turn_unholy(
    sequence: int,
    round_number: int,
    member: EncounterCombatant,
    setup: EncounterSetup,
    targets: tuple[EncounterCombatant, ...],
    dice: DiceProvider,
) -> tuple[list[BattleEvent], int]:
    try:
        if not member.state.template.progression_features.turn_unholy_2014:
            return [], sequence
        resource = _resource(member)
        if not targets or resource is None or resource.current_uses < 1 or not is_available(member.state, "action"):
            return [], sequence
        legal = set(target.combatant_id for target in legal_unholy_targets(member, setup))
        if any(target.combatant_id not in legal for target in targets):
            raise ValueError("Turn the Unholy targets must be living Fiends or Undead within 30 feet.")
        spend(member.state, "action")
        resource.current_uses -= 1
        dc = _save_dc(member)
        events: list[BattleEvent] = []
        for target in targets:
            roll, succeeded = resolve_saving_throw(target.state, "wisdom", dc, dice)
            applied = [] if succeeded else apply_turned_creature_effects(
                member, target, setup, round_number,
                source_effect_id=_TURN_UNHOLY, turned_effect_id=_TURNED,
            )
            events.append(BattleEvent(
                sequence=sequence, round_number=round_number, event_type="saving_throw",
                actor_id=member.combatant_id, actor_name=member.state.template.name,
                target_id=target.combatant_id, target_name=target.state.template.name,
                saving_throw_roll=roll, save_ability="wisdom", save_dc=dc, save_succeeded=succeeded,
                applied_condition_ids=applied, feature_id=_TURN_UNHOLY,
                resource_remaining=resource.current_uses, animation="turn-undead",
                description=(
                    f"{target.state.template.name} {'resists' if succeeded else 'fails'} "
                    f"{member.state.template.name}'s Turn the Unholy."
                ),
            ))
            sequence += 1
        return events, sequence
    except Exception:
        logger.exception("Failed to resolve Turn the Unholy for %s", member.combatant_id)
        raise


def resolve_paladin_channel_support(
    sequence: int,
    round_number: int,
    member: EncounterCombatant,
    setup: EncounterSetup,
    dice: DiceProvider,
) -> tuple[list[BattleEvent], int]:
    """Prefer Turn the Unholy when legal targets exist; otherwise use Sacred Weapon."""
    try:
        if not member.state.template.progression_features.turn_unholy_2014:
            return [], sequence
        targets = legal_unholy_targets(member, setup)
        if targets:
            return resolve_turn_unholy(sequence, round_number, member, setup, targets, dice)
        sacred = resolve_sacred_weapon(sequence, round_number, member)
        return ([sacred], sequence + 1) if sacred is not None else ([], sequence)
    except Exception:
        logger.exception("Failed 2014 Paladin Channel Divinity support for %s", member.combatant_id)
        raise
