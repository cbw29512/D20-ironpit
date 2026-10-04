from __future__ import annotations

import logging

from app.combat.action_economy import is_available
from app.combat.encounter_targeting import combatant_distance
from app.combat.grid_geometry import footprint_distance_ft
from app.combat.persistent_save_zone_cast import _resource
from app.combat.spellcasting import slot_spell_available
from app.combat.suppression_zone_geometry import verbal_casting_blocked, zone_center_legal
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.grid import GridPosition
from app.domain.persistent_save_zones import PersistentSaveZoneAction
from app.domain.size import CreatureSize

logger = logging.getLogger(__name__)


def _appear_damage(action: PersistentSaveZoneAction) -> float:
    if not action.damage_dice_count or "appear" not in action.triggers:
        return 0.0
    return action.damage_dice_count * (action.damage_dice_size + 1) / 2


def _coverage(center: GridPosition, enemies: list[EncounterCombatant], radius_ft: int) -> int:
    return sum(
        1
        for enemy in enemies
        if enemy.state.position is not None
        and footprint_distance_ft(
            center, CreatureSize.MEDIUM, enemy.state.position, enemy.state.template.size,
        ) <= radius_ft
    )


def choose_damaging_save_zone(
    caster: EncounterCombatant,
    setup: EncounterSetup,
    turn_key: str,
) -> tuple[PersistentSaveZoneAction, GridPosition, float] | None:
    """Score damaging persistent save zones under landing-damage, never auto-cast them."""
    try:
        if verbal_casting_blocked(caster, setup) or setup.map_definition is None:
            return None
        enemies = [
            enemy
            for enemy in (setup.monsters if caster.side == "heroes" else setup.heroes)
            if enemy.state.is_alive and not enemy.state.is_dead and enemy.state.position is not None
        ]
        if not enemies:
            return None
        best: tuple[float, PersistentSaveZoneAction, GridPosition] | None = None
        for action in caster.state.template.persistent_save_zone_actions:
            if not action.damage_dice_count or not is_available(caster.state, action.action_cost):
                continue
            if action.concentration and caster.state.concentration is not None:
                continue
            if action.expends_spell_slot and not slot_spell_available(caster.state, turn_key):
                continue
            resource = _resource(caster, action.resource_id)
            if action.resource_id and (resource is None or resource.current_uses < action.resource_cost):
                continue
            centers = []
            for enemy in enemies:
                if not zone_center_legal(setup, enemy.state.position, action.cast_range_ft, caster):
                    continue
                count = _coverage(enemy.state.position, enemies, action.radius_ft)
                if count:
                    centers.append((count, combatant_distance(caster, enemy), enemy.state.position))
            if not centers:
                continue
            count, _, center = max(centers, key=lambda item: (item[0], -item[1]))
            score = _appear_damage(action) * count
            if score <= 0:
                continue
            if best is None or score > best[0]:
                best = (score, action, center.model_copy(deep=True))
        return None if best is None else (best[1], best[2], best[0])
    except Exception:
        logger.exception("Failed damaging save-zone landing choice for %s.", caster.combatant_id)
        raise
