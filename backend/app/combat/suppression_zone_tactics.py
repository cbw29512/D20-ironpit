"""Universal tactical gate for physical obscuration; not a source-name rule.

Fog is legal whenever its printed Action is available, but AI does not spend an
Action on mutual concealment with no measurable sight-based advantage.
"""
from __future__ import annotations

import logging

from app.combat.obscuration_visibility import _line_crosses_zone
from app.combat.visibility_rules import can_see, visibility_distance_ft
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.grid import GridPosition
from app.domain.suppression_zones import (
    PersistentSuppressionZoneAction, PersistentSuppressionZoneState,
)

logger = logging.getLogger(__name__)
_SIGHT_ACTION_FIELDS = (
    "saving_throw_actions", "spell_save_actions",
    "hp_threshold_condition_actions", "hp_threshold_instant_death_actions",
)


def _can_use_sight_action_against(
    source: EncounterCombatant, target: EncounterCombatant,
) -> bool:
    try:
        distance = visibility_distance_ft(source.state, target.state)
        if distance is None or not can_see(source.state, target.state, distance):
            return False
        return any(
            getattr(action, "requires_target_sight", False)
            and (getattr(action, "range_ft", 0) >= distance)
            for field in _SIGHT_ACTION_FIELDS
            for action in getattr(source.state.template, field, [])
        )
    except Exception:
        logger.exception("Failed evaluating source-neutral sight Action for %s.",
                         source.combatant_id)
        raise


def heavy_obscuration_has_tactical_benefit(
    caster: EncounterCombatant, setup: EncounterSetup,
    action: PersistentSuppressionZoneAction, center: GridPosition,
) -> bool:
    """Avoid casts whose mutual unseen attack modifiers would merely cancel."""
    try:
        if action.obscuration_kind != "heavy-physical":
            return True
        allies = setup.monsters if caster.side == "monsters" else setup.heroes
        enemies = setup.heroes if caster.side == "monsters" else setup.monsters
        zone = PersistentSuppressionZoneState(
            zone_id="candidate", source_id=caster.combatant_id,
            action_id=action.id, action_name=action.name,
            position=center, radius_ft=action.radius_ft,
            expires_round=1, deafens=False, blocks_verbal_spells=False,
            thunder_immunity=False, obscuration_kind="heavy-physical",
            concentration=action.concentration,
        )
        def blocked_sight_actions(attackers, targets) -> int:
            return sum(
                1 for attacker in attackers for target in targets
                if attacker.state.is_alive and target.state.is_alive
                and attacker.state.position is not None
                and target.state.position is not None
                and _can_use_sight_action_against(attacker, target)
                and _line_crosses_zone(attacker.state, target.state, zone)
            )
        enemy_actions_stopped = blocked_sight_actions(enemies, allies)
        allied_actions_stopped = blocked_sight_actions(allies, enemies)
        return enemy_actions_stopped > allied_actions_stopped
    except Exception:
        logger.exception("Could not value physical-obscuration Action for %s.",
                         caster.combatant_id)
        raise
