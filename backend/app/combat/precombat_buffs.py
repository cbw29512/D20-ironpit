from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Literal

from app.combat.defensive_spell_resolution import resolve_defensive_spell
from app.combat.friendly_save_auras import sync_friendly_save_auras
from app.combat.precombat_spells import (
    choose_defensive_spell,
    select_defensive_targets,
)
from app.combat.timed_self_buff_policy import (
    timed_self_buff_active,
    timed_self_buff_resource,
)
from app.combat.timed_self_buffs import resolve_timed_self_buff
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.events import BattleEvent
from app.domain.spells import DefensiveSpellAction
from app.domain.timed_self_buffs import TimedSelfBuffAction

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class OpeningBuffChoice:
    kind: Literal["spell", "timed-self-buff"]
    priority: int
    spell: DefensiveSpellAction | None = None
    slot_level: int | None = None
    resource: object | None = None
    timed_action: TimedSelfBuffAction | None = None


def _timed_choice(member: EncounterCombatant) -> TimedSelfBuffAction | None:
    try:
        choices: list[TimedSelfBuffAction] = []
        for action in member.state.template.timed_self_buff_actions:
            resource = timed_self_buff_resource(member, action)
            if timed_self_buff_active(member, action):
                continue
            if action.resource_id is not None and (
                resource is None or resource.current_uses < action.resource_cost
            ):
                continue
            choices.append(action)
        return max(choices, key=lambda item: item.priority, default=None)
    except Exception as exc:
        logger.exception("Opening timed-buff choice failed for %s.", member.combatant_id)
        raise RuntimeError("Opening timed buff could not be selected.") from exc


def choose_opening_buff(
    member: EncounterCombatant,
    setup: EncounterSetup,
) -> OpeningBuffChoice | None:
    try:
        if member.state.opening_buff_id is not None:
            return None

        candidates: list[OpeningBuffChoice] = []
        spell_choice = choose_defensive_spell(member, setup)
        if spell_choice is not None:
            spell, slot_level, resource = spell_choice
            candidates.append(OpeningBuffChoice(
                kind="spell",
                priority=spell.priority,
                spell=spell,
                slot_level=slot_level,
                resource=resource,
            ))

        timed = _timed_choice(member)
        if timed is not None:
            candidates.append(OpeningBuffChoice(
                kind="timed-self-buff",
                priority=timed.priority,
                timed_action=timed,
            ))

        return max(
            candidates,
            key=lambda item: (
                item.priority,
                item.spell.level if item.spell is not None else 0,
                1 if item.kind == "spell" else 0,
            ),
            default=None,
        )
    except Exception as exc:
        logger.exception("Opening buff choice failed for %s.", member.combatant_id)
        raise RuntimeError("Opening buff could not be selected.") from exc


def resolve_opening_buff(
    sequence: int,
    member: EncounterCombatant,
    setup: EncounterSetup,
    choice: OpeningBuffChoice,
) -> BattleEvent:
    try:
        if member.state.opening_buff_id is not None:
            raise ValueError(
                f"{member.state.template.name} already committed its one opening buff this battle."
            )

        if choice.kind == "spell":
            if choice.spell is None or choice.slot_level is None or choice.resource is None:
                raise ValueError("Opening spell choice is incomplete.")
            targets = select_defensive_targets(
                member,
                setup,
                choice.spell,
                choice.slot_level,
            )
            affected_states = [
                entry.state for entry in [*setup.heroes, *setup.monsters]
            ]
            return resolve_defensive_spell(
                sequence,
                member,
                targets,
                choice.spell,
                choice.slot_level,
                choice.resource,
                affected_states,
            )

        if choice.timed_action is None:
            raise ValueError("Opening timed self-buff choice is incomplete.")
        member.state.opening_buff_id = choice.timed_action.id
        event = resolve_timed_self_buff(
            sequence,
            0,
            member,
            choice.timed_action,
            spend_action_cost=False,
        )
        sync_friendly_save_auras(setup)
        return event.model_copy(update={
            "description": (
                f"Precombat preparation: {member.state.template.name} uses "
                f"{choice.timed_action.name} as the free opening buff."
            ),
        })
    except (ValueError, RuntimeError):
        raise
    except Exception as exc:
        logger.exception("Opening buff resolution failed for %s.", member.combatant_id)
        raise RuntimeError("Opening buff could not be resolved.") from exc


def prepare_opening_buffs(
    setup: EncounterSetup,
    sequence: int = 1,
) -> tuple[list[BattleEvent], int]:
    try:
        events: list[BattleEvent] = []
        for member in [*setup.heroes, *setup.monsters]:
            choice = choose_opening_buff(member, setup)
            if choice is None:
                continue
            events.append(resolve_opening_buff(sequence, member, setup, choice))
            sequence += 1
        return events, sequence
    except Exception:
        logger.exception("Precombat opening-buff preparation failed.")
        raise
