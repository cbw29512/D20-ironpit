from __future__ import annotations

import logging
from fractions import Fraction

from app.combat.formation import starting_position_ft
from app.combat.grid_placement import apply_placement, pack_deployment_zone
from app.combat.state import build_combatant_state
from app.content.arena_map import (
    build_hero_deployment_zone,
    build_monster_deployment_zone,
    build_standard_iron_pit_map,
)
from app.content.roster import build_arena_roster
from app.domain.encounters import EncounterCombatant, EncounterSelection, EncounterSetup
from app.domain.grid import BattleMapDefinition
from app.domain.models import CombatantTemplate

logger = logging.getLogger(__name__)


def _index_templates(items: list[CombatantTemplate]) -> dict[str, CombatantTemplate]:
    try:
        return {item.id: item for item in items}
    except Exception:
        logger.exception("Failed to index encounter templates.")
        raise


def _resolve_card(card_id: str, cards: dict[str, CombatantTemplate], side: str) -> CombatantTemplate:
    try:
        return cards[card_id]
    except KeyError as exc:
        logger.warning("Unknown %s card requested: %s", side, card_id)
        raise ValueError(f"Unknown {side} card: {card_id}") from exc


def _format_fraction(value: Fraction) -> str:
    try:
        return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"
    except Exception:
        logger.exception("Failed to format encounter fraction %s.", value)
        raise


def _hero_level_total(heroes: list[EncounterCombatant]) -> int:
    try:
        levels = [hero.state.template.level for hero in heroes]
        if any(level is None for level in levels):
            raise ValueError("Every hero card must have a character level.")
        return sum(int(level) for level in levels)
    except Exception:
        logger.exception("Failed to total hero levels.")
        raise


def _monster_cr_total(monsters: list[EncounterCombatant]) -> str:
    try:
        total = Fraction(0, 1)
        for monster in monsters:
            challenge_rating = monster.state.template.challenge_rating
            if challenge_rating is None:
                raise ValueError("Every monster card must have a challenge rating.")
            total += Fraction(challenge_rating)
        return _format_fraction(total)
    except Exception:
        logger.exception("Failed to total monster challenge ratings.")
        raise


def _member(card_id: str, index: int, side: str, cards: dict[str, CombatantTemplate]) -> EncounterCombatant:
    try:
        label = "hero" if side == "heroes" else "monster"
        template = _resolve_card(card_id, cards, label)
        return EncounterCombatant(
            combatant_id=f"{label}-{index}:{card_id}",
            side=side,
            position_ft=starting_position_ft(template, side),
            state=build_combatant_state(template),
        )
    except Exception:
        logger.exception("Failed to build %s encounter member %s.", side, card_id)
        raise


def _apply_standard_grid_placement(
    heroes: list[EncounterCombatant],
    monsters: list[EncounterCombatant],
) -> BattleMapDefinition:
    try:
        battle_map = build_standard_iron_pit_map()
        apply_placement(
            heroes,
            pack_deployment_zone(battle_map, build_hero_deployment_zone(), heroes),
        )
        apply_placement(
            monsters,
            pack_deployment_zone(battle_map, build_monster_deployment_zone(), monsters),
        )
        return battle_map
    except Exception:
        logger.exception("Failed to apply standard Iron Pit grid deployment.")
        raise


def build_encounter_setup(selection: EncounterSelection) -> EncounterSetup:
    try:
        roster = build_arena_roster()
        heroes = _index_templates(roster.characters)
        monsters = _index_templates(roster.monsters)
        hero_states = [
            _member(card_id, index, "heroes", heroes)
            for index, card_id in enumerate(selection.hero_ids, start=1)
        ]
        monster_states = [
            _member(card_id, index, "monsters", monsters)
            for index, card_id in enumerate(selection.monster_ids, start=1)
        ]
        battle_map = _apply_standard_grid_placement(hero_states, monster_states)
        return EncounterSetup(
            heroes=hero_states,
            monsters=monster_states,
            hero_total_levels=_hero_level_total(hero_states),
            monster_total_cr=_monster_cr_total(monster_states),
            map_definition=battle_map,
        )
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Failed to build encounter setup.")
        raise RuntimeError("Encounter setup could not be created.") from exc
