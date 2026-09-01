from __future__ import annotations

from dataclasses import dataclass

from app.combat.action_economy import is_available
from app.combat.encounter_targeting import combatant_distance
from app.combat.offense_value import save_spell_expected_damage
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
    resource_id = f"spell-slot-{action.level}"
    resource = next((item for item in caster.state.resources if item.id == resource_id), None)
    return action.level if resource is not None and resource.current_uses > 0 else None


def _legal_single_targets(caster: EncounterCombatant, setup: EncounterSetup, action: SpellSaveAction):
    enemies = setup.monsters if caster.side == "heroes" else setup.heroes
    return [
        target for target in enemies
        if target.state.is_alive and not target.state.is_dead and target.state.current_hp > 0
        and combatant_distance(caster, target) <= action.range_ft
    ]


def choose_spell(
    caster: EncounterCombatant,
    setup: EncounterSetup,
    turn_key: str,
    protected_ally_ids: set[str] | None = None,
) -> SpellChoice | None:
    candidates: list[tuple[float, int, int, SpellChoice]] = []
    members = {member.combatant_id: member for member in [*setup.heroes, *setup.monsters]}
    for index, action in enumerate(caster.state.template.spell_save_actions):
        if action.action_cost == "reaction" or action.concentration or not is_available(caster.state, action.action_cost):
            continue
        slot_level = _slot_level(caster, action, turn_key)
        if slot_level is None:
            continue
        if action.area_radius_ft is not None:
            placement = best_area_placement(caster, setup, action.area_radius_ft, action.range_ft, protected_ally_ids)
            if placement is None:
                continue
            target_ids = (*placement.enemy_ids, *placement.friendly_ids)
            score = sum(save_spell_expected_damage(members[target_id], action) for target_id in placement.enemy_ids)
            score -= sum(save_spell_expected_damage(members[target_id], action) for target_id in placement.friendly_ids)
            candidates.append((score, -action.level, -index, SpellChoice(action, slot_level, target_ids, placement)))
            continue
        legal = _legal_single_targets(caster, setup, action)
        if not legal:
            continue
        target = max(
            legal,
            key=lambda item: (save_spell_expected_damage(item, action), -item.state.current_hp, item.combatant_id),
        )
        score = save_spell_expected_damage(target, action)
        candidates.append((score, -action.level, -index, SpellChoice(action, slot_level, (target.combatant_id,))))
    return max(candidates, key=lambda item: item[:3])[3] if candidates else None
