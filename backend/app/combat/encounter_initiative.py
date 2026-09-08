from __future__ import annotations

import logging
from collections import defaultdict

from app.combat.condition_rules import is_incapacitated
from app.combat.dice import DiceProvider
from app.combat.rolls import roll_d20
from app.domain.encounters import EncounterCombatant, EncounterInitiative, EncounterSetup, InitiativeGroup
from app.domain.models import RollMode

logger = logging.getLogger(__name__)


def _initiative_mode(member: EncounterCombatant) -> RollMode:
    advantage = member.state.template.progression_features.initiative_advantage
    disadvantage = is_incapacitated(member.state)
    if advantage == disadvantage:
        return RollMode.NORMAL
    return RollMode.ADVANTAGE if advantage else RollMode.DISADVANTAGE


def _roll_group(members: list[EncounterCombatant], dice: DiceProvider) -> InitiativeGroup:
    template = members[0].state.template
    roll = roll_d20(dice, template.initiative_bonus, _initiative_mode(members[0]))
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
    monster_groups: dict[tuple[str, bool], list[EncounterCombatant]] = defaultdict(list)
    monster_order: list[tuple[str, bool]] = []
    for monster in setup.monsters:
        key = (monster.state.template.id, is_incapacitated(monster.state))
        if key not in monster_groups:
            monster_order.append(key)
        monster_groups[key].append(monster)
    groups.extend(_roll_group(monster_groups[key], dice) for key in monster_order)
    return groups


def _priority(group: InitiativeGroup) -> int:
    if group.natural_roll == 20:
        return 2
    if group.natural_roll == 1:
        return 0
    return 1


def _resolve_ties(groups: list[InitiativeGroup], dice: DiceProvider) -> None:
    """Reroll only unresolved exact ties until every initiative group has a stable order."""
    while True:
        tied_by_signature: dict[tuple[int, int, tuple[int, ...]], list[InitiativeGroup]] = defaultdict(list)
        for group in groups:
            tied_by_signature[(_priority(group), group.initiative_count, tuple(group.tie_break_rolls))].append(group)
        unresolved = [tied for tied in tied_by_signature.values() if len(tied) > 1]
        if not unresolved:
            return
        for tied in unresolved:
            for group in tied:
                value = dice.roll(20)
                group.tie_break_rolls.append(value)
                group.tie_break_roll = value


def roll_encounter_initiative(setup: EncounterSetup, dice: DiceProvider) -> EncounterInitiative:
    """Resolve initiative with Iron Pit natural-20/natural-1 buckets and pure d20 tie rerolls."""
    try:
        groups = _base_groups(setup, dice)
        _resolve_ties(groups, dice)
        indexed = {id(group): index for index, group in enumerate(groups)}
        groups.sort(
            key=lambda group: (
                _priority(group),
                group.initiative_count,
                tuple(group.tie_break_rolls),
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