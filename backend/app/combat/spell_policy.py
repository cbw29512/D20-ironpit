from __future__ import annotations

from dataclasses import dataclass

from app.combat.action_economy import is_available
from app.combat.encounter_targeting import combatant_distance
from app.combat.spell_area import AreaPlacement, best_area_placement
from app.combat.spellcasting import slot_spell_available
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.spells import SpellSaveAction


@dataclass(frozen=True)
class SpellChoice:
    action: SpellSaveAction
    slot_level: int
    target_ids: tuple[str, ...]
    placement: AreaPlacement | None = None


def _slot_level(caster: EncounterCombatant, action: SpellSaveAction, turn_key: str) -> int | None:
    if action.level == 0:
        return 0
    if not slot_spell_available(caster.state, turn_key):
        return None
    levels = []
    for resource in caster.state.resources:
        if not resource.id.startswith("spell-slot-") or resource.current_uses < 1:
            continue
        try:
            level = int(resource.id.removeprefix("spell-slot-"))
        except ValueError:
            continue
        if level >= action.level:
            levels.append(level)
    return max(levels) if levels else None


def _single_target(caster: EncounterCombatant, setup: EncounterSetup, action: SpellSaveAction):
    enemies = setup.monsters if caster.side == "heroes" else setup.heroes
    legal = [
        target for target in enemies
        if target.state.is_alive and not target.state.is_dead and target.state.current_hp > 0
        and combatant_distance(caster, target) <= action.range_ft
    ]
    return min(legal, key=lambda target: combatant_distance(caster, target), default=None)


def choose_spell(
    caster: EncounterCombatant,
    setup: EncounterSetup,
    turn_key: str,
    protected_ally_ids: set[str] | None = None,
) -> SpellChoice | None:
    """Try highest-level spells first; unsafe AoEs fall through to the next spell."""
    indexed = list(enumerate(caster.state.template.spell_save_actions))
    for _, action in sorted(indexed, key=lambda item: (-item[1].level, item[0])):
        if action.action_cost == "reaction":
            continue
        if action.concentration:
            continue  # Concentration spells remain fail-closed until that subsystem is certified.
        if not is_available(caster.state, action.action_cost):
            continue
        slot_level = _slot_level(caster, action, turn_key)
        if slot_level is None:
            continue
        if action.area_radius_ft is not None:
            placement = best_area_placement(
                caster, setup, action.area_radius_ft, action.range_ft, protected_ally_ids,
            )
            if placement is None:
                continue
            target_ids = (*placement.enemy_ids, *placement.friendly_ids)
            return SpellChoice(action, slot_level, target_ids, placement)
        target = _single_target(caster, setup, action)
        if target is not None:
            return SpellChoice(action, slot_level, (target.combatant_id,))
    return None
