from __future__ import annotations

import logging

from app.combat.selectable_damage_resistance import score_enemy_damage_types
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.spells import DefensiveSpellAction
from app.domain.weapons_base import DamageType

logger = logging.getLogger(__name__)


def choose_spell_resistance_type(
    member: EncounterCombatant,
    setup: EncounterSetup,
    spell: DefensiveSpellAction,
) -> DamageType | None:
    """Choose one printed selectable resistance from visible opposing damage."""
    try:
        allowed = [DamageType(item) for item in spell.selectable_resistance_types]
        if not allowed:
            return None
        scores = score_enemy_damage_types(member, setup, allowed)
        order = {item: index for index, item in enumerate(allowed)}
        return max(allowed, key=lambda item: (scores.get(item, 0.0), -order[item]))
    except Exception:
        logger.exception("Failed to choose selectable resistance for %s.", spell.id)
        raise
