from __future__ import annotations

import logging

from app.combat.state import build_combatant_state
from app.content.roster import build_arena_roster
from app.domain.encounters import EncounterCombatant, EncounterSelection, EncounterSetup
from app.domain.models import CombatantTemplate

logger = logging.getLogger(__name__)


def _index_templates(items: list[CombatantTemplate]) -> dict[str, CombatantTemplate]:
    return {item.id: item for item in items}


def _resolve_card(card_id: str, cards: dict[str, CombatantTemplate], side: str) -> CombatantTemplate:
    try:
        return cards[card_id]
    except KeyError as exc:
        logger.warning("Unknown %s card requested: %s", side, card_id)
        raise ValueError(f"Unknown {side} card: {card_id}") from exc


def build_encounter_setup(selection: EncounterSelection) -> EncounterSetup:
    try:
        roster = build_arena_roster()
        heroes = _index_templates(roster.characters)
        monsters = _index_templates(roster.monsters)

        hero_states = [
            EncounterCombatant(
                combatant_id=f"hero-{index}:{card_id}",
                side="heroes",
                position_ft=0,
                state=build_combatant_state(_resolve_card(card_id, heroes, "hero")),
            )
            for index, card_id in enumerate(selection.hero_ids, start=1)
        ]
        monster_states = [
            EncounterCombatant(
                combatant_id=f"monster-{index}:{card_id}",
                side="monsters",
                position_ft=selection.starting_distance_ft,
                state=build_combatant_state(_resolve_card(card_id, monsters, "monster")),
            )
            for index, card_id in enumerate(selection.monster_ids, start=1)
        ]
        return EncounterSetup(
            heroes=hero_states,
            monsters=monster_states,
            starting_distance_ft=selection.starting_distance_ft,
        )
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Failed to build encounter setup.")
        raise RuntimeError("Encounter setup could not be created.") from exc
