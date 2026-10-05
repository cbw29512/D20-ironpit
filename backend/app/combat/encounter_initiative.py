from __future__ import annotations

import logging
from collections import defaultdict

from app.combat.ability_checks import ability_check_roll_mode
from app.combat.condition_rules import is_incapacitated
from app.combat.dice import DiceProvider
from app.combat.exhaustion import ability_check_disadvantage_sources, d20_modifier
from app.combat.rolls import roll_d20
from app.domain.encounters import EncounterCombatant, EncounterInitiative, EncounterSetup, FirstRoundExtraTurn, InitiativeGroup
from app.domain.models import RollMode

logger = logging.getLogger(__name__)


def _initiative_mode(member: EncounterCombatant) -> RollMode:
    try:
        state = member.state
        return ability_check_roll_mode(
            state,
            advantage_sources=int(state.template.progression_features.initiative_advantage),
            disadvantage_sources=int(is_incapacitated(state)) + ability_check_disadvantage_sources(state),
        )
    except Exception as exc:
        logger.exception("Failed to resolve initiative roll mode for %s.", member.state.template.name)
        raise RuntimeError("Initiative roll mode could not be resolved.") from exc


def _roll_group(members: list[EncounterCombatant], dice: DiceProvider) -> InitiativeGroup:
    state = members[0].state
    template = state.template
    roll = roll_d20(dice, template.initiative_bonus + d20_modifier(state), _initiative_mode(members[0]))
    for member in members:
        member.state.initiative_roll = roll.selected_roll
        member.state.initiative_total = roll.total
    return InitiativeGroup(
        side=members[0].side,
        template_id=template.id,
        combatant_ids=[member.combatant_id for member in members],
        initiative_roll=roll,
        natural_roll=roll.selected_roll or 1,
        initiative_bonus=template.initiative_bonus,
        initiative_count=roll.total,
    )


def _base_groups(setup: EncounterSetup, dice: DiceProvider) -> list[InitiativeGroup]:
    groups = [_roll_group([hero], dice) for hero in setup.heroes]
    monster_groups: dict[tuple[str, bool, int], list[EncounterCombatant]] = defaultdict(list)
    monster_order: list[tuple[str, bool, int]] = []
    for monster in setup.monsters:
        key = (monster.state.template.id, is_incapacitated(monster.state), monster.state.exhaustion_level)
        if key not in monster_groups:
            monster_order.append(key)
        monster_groups[key].append(monster)
    groups.extend(_roll_group(monster_groups[key], dice) for key in monster_order)
    return groups


def _priority_bucket(group: InitiativeGroup) -> int:
    """Return the Iron Pit initiative bucket. Natural 20 is not special; natural 1 stays last."""
    try:
        return 0 if group.natural_roll == 1 else 1
    except Exception as exc:
        logger.exception("Failed to resolve the initiative priority bucket.")
        raise RuntimeError("Initiative priority bucket could not be resolved.") from exc


def _ownership_rank(group: InitiativeGroup) -> int:
    """Deterministic RAW-compatible tie ownership: DM lets heroes act before monsters."""
    try:
        return 1 if group.side == "heroes" else 0
    except Exception as exc:
        logger.exception("Failed to resolve initiative tie ownership for %s.", group.template_id)
        raise RuntimeError("Initiative tie ownership could not be resolved.") from exc


def _first_round_schedule(
    groups: list[InitiativeGroup],
    setup: EncounterSetup,
) -> tuple[list[str], list[FirstRoundExtraTurn]]:
    try:
        members = {member.combatant_id: member for member in [*setup.heroes, *setup.monsters]}
        slots: list[tuple[tuple[object, ...], str]] = []
        extras: list[FirstRoundExtraTurn] = []
        for group_index, group in enumerate(groups):
            for member_index, combatant_id in enumerate(group.combatant_ids):
                normal_key = (
                    _priority_bucket(group), group.initiative_count, 1,
                    _ownership_rank(group),
                    -group_index, -member_index,
                )
                slots.append((normal_key, combatant_id))
                member = members[combatant_id]
                grants = list(member.state.template.progression_features.first_round_extra_turn_grants)
                if not grants:
                    legacy_offset = member.state.template.progression_features.first_round_extra_turn_initiative_offset
                    if legacy_offset is not None:
                        grants = [{
                            "source_id": "first-round-extra-turn",
                            "source_name": "Extra First-Round Turn",
                            "initiative_offset": legacy_offset,
                        }]
                for grant in grants:
                    if isinstance(grant, dict):
                        source_id = grant["source_id"]
                        source_name = grant["source_name"]
                        initiative_offset = grant["initiative_offset"]
                    else:
                        source_id = grant.source_id
                        source_name = grant.source_name
                        initiative_offset = grant.initiative_offset
                    count = group.initiative_count + initiative_offset
                    # Extra turns have an initiative count, not a second roll, and stay in the normal bucket.
                    extra_key = (
                        1, count, 0,
                        _ownership_rank(group),
                        -group_index, -member_index,
                    )
                    slots.append((extra_key, combatant_id))
                    extras.append(FirstRoundExtraTurn(
                        combatant_id=combatant_id,
                        initiative_count=count,
                        source_id=source_id,
                        source_name=source_name,
                    ))
        slots.sort(key=lambda item: item[0], reverse=True)
        return [combatant_id for _, combatant_id in slots], extras
    except Exception as exc:
        logger.exception("Failed to build the first-round extra-turn schedule.")
        raise RuntimeError("First-round extra-turn schedule could not be resolved.") from exc

def turn_order_for_round(
    round_number: int,
    initiative: EncounterInitiative,
    combatants: dict[str, EncounterCombatant],
) -> list[str]:
    """Return the canonical precomputed schedule for one round."""
    try:
        if round_number == 1:
            return list(initiative.first_round_turn_order)
        return list(initiative.turn_order)
    except Exception as exc:
        logger.exception("Encounter turn scheduling failed for round %s.", round_number)
        raise RuntimeError("Encounter turn schedule could not be resolved.") from exc

def roll_encounter_initiative(setup: EncounterSetup, dice: DiceProvider) -> EncounterInitiative:
    """Resolve initiative by check total, natural-1 house bucket, and deterministic RAW tie ownership."""
    try:
        groups = _base_groups(setup, dice)
        indexed = {id(group): index for index, group in enumerate(groups)}
        groups.sort(
            key=lambda group: (
                _priority_bucket(group),
                group.initiative_count,
                _ownership_rank(group),
                -indexed[id(group)],
            ),
            reverse=True,
        )
        turn_order = [combatant_id for group in groups for combatant_id in group.combatant_ids]
        first_round_turn_order, extra_turns = _first_round_schedule(groups, setup)
        return EncounterInitiative(
            groups=groups,
            turn_order=turn_order,
            first_round_turn_order=first_round_turn_order,
            first_round_extra_turns=extra_turns,
        )
    except Exception as exc:
        logger.exception("Encounter initiative failed.")
        raise RuntimeError("Encounter initiative could not be resolved.") from exc
