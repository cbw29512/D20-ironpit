from __future__ import annotations

import logging
from fractions import Fraction

from app.combat.formation import FRONT_LINE_DISTANCE_FT, starting_position_ft
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


def _format_fraction(value: Fraction) -> str:
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def _hero_level_total(heroes: list[EncounterCombatant]) -> int:
    levels = [hero.state.template.level for hero in heroes]
    if any(level is None for level in levels):
        raise ValueError("Every hero card must have a character level.")
    return sum(int(level) for level in levels)


def _monster_cr_total(monsters: list[EncounterCombatant]) -> str:
    total = Fraction(0, 1)
    for monster in monsters:
        challenge_rating = monster.state.template.challenge_rating
        if challenge_rating is None:
            raise ValueError("Every monster card must have a challenge rating.")
        total += Fraction(challenge_rating)
    return _format_fraction(total)


def _member(card_id: str, index: int, side: str, cards: dict[str, CombatantTemplate]) -> EncounterCombatant:
    label = "hero" if side == "heroes" else "monster"
    template = _resolve_card(card_id, cards, label)
    return EncounterCombatant(
        combatant_id=f"{label}-{index}:{card_id}",
        side=side,
        position_ft=starting_position_ft(template, side),
        state=build_combatant_state(template),
    )


def build_encounter_setup(selection: EncounterSelection) -> EncounterSetup:
    try:
        roster = build_arena_roster()
        heroes = _index_templates(roster.characters)
        monsters = _index_templates(roster.monsters)
        hero_states = [_member(card_id, index, "heroes", heroes) for index, card_id in enumerate(selection.hero_ids, start=1)]
        monster_states = [_member(card_id, index, "monsters", monsters) for index, card_id in enumerate(selection.monster_ids, start=1)]
        return EncounterSetup(
            heroes=hero_states,
            monsters=monster_states,
            hero_total_levels=_hero_level_total(hero_states),
            monster_total_cr=_monster_cr_total(monster_states),
            starting_distance_ft=FRONT_LINE_DISTANCE_FT,
        )
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Failed to build encounter setup.")
        raise RuntimeError("Encounter setup could not be created.") from exc
