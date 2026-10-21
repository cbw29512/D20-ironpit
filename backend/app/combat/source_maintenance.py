from __future__ import annotations

import logging
from collections import defaultdict

from app.combat.action_economy import is_available, spend
from app.combat.timed_condition_lifecycle import remove_effect_group
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import BattleEvent, TimedEffect

logger = logging.getLogger(__name__)
MaintainedGroup = list[tuple[EncounterCombatant, TimedEffect]]


def _maintained_groups(
    source: EncounterCombatant,
    setup: EncounterSetup,
    *,
    due_only: bool,
) -> dict[str, MaintainedGroup]:
    groups: dict[str, MaintainedGroup] = defaultdict(list)
    for target in [*setup.heroes, *setup.monsters]:
        for effect in target.state.timed_effects:
            if (
                effect.source_id != source.combatant_id
                or effect.source_effect_id is None
                or effect.source_maintenance_action_cost == "none"
            ):
                continue
            applied_turn = effect.source_turn_count_at_application
            if due_only and (
                applied_turn is None or source.state.turns_started <= applied_turn
            ):
                continue
            groups[effect.source_effect_id].append((target, effect))
    return groups


def _selected_group(
    source: EncounterCombatant,
    groups: dict[str, MaintainedGroup],
) -> str | None:
    if not groups:
        return None
    ranked = sorted(
        groups,
        key=lambda effect_id: (
            -len({
                target.combatant_id
                for target, _effect in groups[effect_id]
                if target.side != source.side
            }),
            -len({target.combatant_id for target, _effect in groups[effect_id]}),
            effect_id,
        ),
    )
    return ranked[0]


def _end_group(
    sequence: int,
    round_number: int,
    source: EncounterCombatant,
    group: MaintainedGroup,
) -> tuple[list[BattleEvent], int]:
    events: list[BattleEvent] = []
    handled: set[str] = set()
    for target, effect in group:
        if target.combatant_id in handled:
            continue
        handled.add(target.combatant_id)
        had_group = any(
            item.source_id == effect.source_id
            and item.source_effect_id == effect.source_effect_id
            for item in target.state.timed_effects
        )
        removed = remove_effect_group(
            target.state, effect, grant_source_immunity=False,
        )
        if not had_group:
            continue
        events.append(BattleEvent(
            sequence=sequence, round_number=round_number, event_type="feature",
            actor_id=source.combatant_id, actor_name=source.state.template.name,
            target_id=target.combatant_id, target_name=target.state.template.name,
            removed_condition_ids=removed,
            feature_id=effect.source_effect_id,
            animation="condition-ended",
            description=(
                f"{source.state.template.name} does not continue "
                f"{effect.source_effect_id}; its effects on "
                f"{target.state.template.name} end."
            ),
        ))
        sequence += 1
    return events, sequence


def stop_source_maintained_effects(
    sequence: int,
    round_number: int,
    source: EncounterCombatant,
    setup: EncounterSetup,
) -> tuple[list[BattleEvent], int]:
    """Voluntarily stop every maintained source effect without spending an action."""
    try:
        events: list[BattleEvent] = []
        for group in _maintained_groups(source, setup, due_only=False).values():
            ended, sequence = _end_group(
                sequence, round_number, source, group,
            )
            events.extend(ended)
        return events, sequence
    except Exception:
        logger.exception("Failed to stop source-maintained effects for %s.", source.combatant_id)
        raise


def resolve_source_maintenance(
    sequence: int,
    round_number: int,
    source: EncounterCombatant,
    setup: EncounterSetup,
) -> tuple[list[BattleEvent], int]:
    """Continue one best due group, ending every other due group without immunity."""
    try:
        groups = _maintained_groups(source, setup, due_only=True)
        selected = _selected_group(source, groups)
        events: list[BattleEvent] = []
        can_continue = selected is not None and is_available(
            source.state, groups[selected][0][1].source_maintenance_action_cost,
        )
        for effect_id, group in groups.items():
            if effect_id != selected or not can_continue:
                ended, sequence = _end_group(
                    sequence, round_number, source, group,
                )
                events.extend(ended)
                continue
            cost = group[0][1].source_maintenance_action_cost
            spend(source.state, cost)
            for _target, effect in group:
                effect.source_turn_count_at_application = source.state.turns_started
            events.append(BattleEvent(
                sequence=sequence, round_number=round_number, event_type="feature",
                actor_id=source.combatant_id, actor_name=source.state.template.name,
                feature_id=effect_id, animation="feature",
                description=(
                    f"{source.state.template.name} continues {effect_id} "
                    f"with its {cost.replace('_', ' ').title()}."
                ),
            ))
            sequence += 1
        return events, sequence
    except Exception:
        logger.exception("Failed source-maintenance resolution for %s.", source.combatant_id)
        raise
