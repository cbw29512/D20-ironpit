from __future__ import annotations

import logging
from collections import defaultdict

from app.combat.dice import DiceProvider
from app.combat.rolls import roll_d20
from app.domain.encounters import EncounterCombatant, EncounterInitiative, EncounterSetup, InitiativeGroup

logger = logging.getLogger(__name__)


def _roll_group(members: list[EncounterCombatant], dice: DiceProvider) -> InitiativeGroup:
    template = members[0].state.template
    roll = roll_d20(dice, template.initiative_bonus)
    for member in members:
        member.state.initiative_roll = roll.selected_roll
        member.state.initiative_total = roll.total
    return InitiativeGroup(
        side=members[0].side,
        template_id=template.id,
        combatant_ids=[member.combatant_id for member in members],
        natural_roll=roll.selected_roll or 1,
        initiative_bonus=template.initiative_bonus,
        initiative_count=roll.total,
    )


def _base_groups(setup: EncounterSetup, dice: DiceProvider) -> list[InitiativeGroup]:
    groups = [_roll_group([hero], dice) for hero in setup.heroes]
    monster_groups: dict[str, list[EncounterCombatant]] = defaultdict(list)
    monster_order: list[str] = []
    for monster in setup.monsters:
        template_id = monster.state.template.id
        if template_id not in monster_groups:
            monster_order.append(template_id)
        monster_groups[template_id].append(monster)
    groups.extend(_roll_group(monster_groups[template_id], dice) for template_id in monster_order)
    return groups


def _resolve_cross_side_ties(groups: list[InitiativeGroup], dice: DiceProvider) -> None:
    by_count: dict[int, list[InitiativeGroup]] = defaultdict(list)
    for group in groups:
        by_count[group.initiative_count].append(group)
    for tied in by_count.values():
        if len({group.side for group in tied}) < 2:
            continue
        used: set[int] = set()
        for group in tied:
            value = dice.roll(20)
            while value in used:
                value = dice.roll(20)
            used.add(value)
            group.tie_break_roll = value


def roll_encounter_initiative(setup: EncounterSetup, dice: DiceProvider) -> EncounterInitiative:
    """Apply SRD 5.2.1 initiative, grouping identical monsters under one GM roll."""
    try:
        groups = _base_groups(setup, dice)
        _resolve_cross_side_ties(groups, dice)
        indexed = {id(group): index for index, group in enumerate(groups)}
        groups.sort(
            key=lambda group: (
                group.initiative_count,
                group.tie_break_roll or 0,
                -indexed[id(group)],
            ),
            reverse=True,
        )
        return EncounterInitiative(
            groups=groups,
            turn_order=[combatant_id for group in groups for combatant_id in group.combatant_ids],
        )
    except Exception as exc:
        logger.exception("Encounter initiative failed.")
        raise RuntimeError("Encounter initiative could not be resolved.") from exc
