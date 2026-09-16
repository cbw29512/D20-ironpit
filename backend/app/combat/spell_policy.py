from __future__ import annotations

from dataclasses import dataclass

from app.combat.action_economy import is_available
from app.combat.area_targeting import AreaPlacement as GridAreaPlacement, legal_area_placements
from app.combat.encounter_targeting import combatant_distance
from app.combat.offense_value import save_spell_expected_damage
from app.combat.persistent_spells import initial_spell_cast_allowed
from app.combat.spell_area import AreaPlacement as LegacyAreaPlacement, best_area_placement
from app.combat.spell_immunity import spell_affects_target
from app.combat.spellcasting import slot_spell_available
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.spells import SpellSaveAction


@dataclass(frozen=True)
class SpellChoice:
    action: SpellSaveAction
    slot_level: int
    target_ids: tuple[str, ...]
    placement: LegacyAreaPlacement | GridAreaPlacement | None = None
    expected_damage: float = 0.0
    resource_id: str | None = None


def _resource(caster: EncounterCombatant, resource_id: str):
    return next((item for item in caster.state.resources if item.id == resource_id), None)


def _cast_access(caster: EncounterCombatant, action: SpellSaveAction, turn_key: str) -> tuple[int, str | None] | None:
    innate_id = f"innate-{action.id}"
    innate = _resource(caster, innate_id)
    if innate is not None:
        return (action.level, innate_id) if innate.current_uses > 0 else None

    # Cantrips never consume a spell slot. Leveled save spells currently bind to
    # their exact certified slot level; explicit upcasting is handled only by
    # mechanics that model it directly rather than silently borrowing any
    # higher-level slot.
    if action.level == 0:
        return 0, None

    slot_id = f"spell-slot-{action.level}"
    slot = _resource(caster, slot_id)
    if slot is None:
        return None
    if not slot_spell_available(caster.state, turn_key) or slot.current_uses < 1:
        return None
    return action.level, slot_id


def _creature_type(target: EncounterCombatant) -> str:
    return (target.state.template.creature_type or "").lower()


def _spell_affects(action: SpellSaveAction, target: EncounterCombatant) -> bool:
    return (
        _creature_type(target) not in action.excluded_creature_types
        and spell_affects_target(target.state, action.level)
    )


def _legal_single_targets(caster: EncounterCombatant, setup: EncounterSetup, action: SpellSaveAction):
    enemies = setup.monsters if caster.side == "heroes" else setup.heroes
    return [
        target for target in enemies
        if target.state.is_alive and not target.state.is_dead and target.state.current_hp > 0
        and combatant_distance(caster, target) <= action.range_ft and _spell_affects(action, target)
    ]


def _area_score(placement, members, action: SpellSaveAction) -> float:
    score = sum(save_spell_expected_damage(members[target_id], action) for target_id in placement.enemy_ids)
    return score - sum(save_spell_expected_damage(members[target_id], action) for target_id in placement.friendly_ids)


def choose_spell(
    caster: EncounterCombatant,
    setup: EncounterSetup,
    turn_key: str,
    protected_ally_ids: set[str] | None = None,
) -> SpellChoice | None:
    candidates: list[tuple[float, int, int, SpellChoice]] = []
    members = {member.combatant_id: member for member in [*setup.heroes, *setup.monsters]}
    protected = protected_ally_ids or set()
    for index, action in enumerate(caster.state.template.spell_save_actions):
        if action.action_cost == "reaction" or not is_available(caster.state, action.action_cost):
            continue
        if not initial_spell_cast_allowed(caster.state, action.id, concentration=action.concentration):
            continue
        access = _cast_access(caster, action, turn_key)
        if access is None:
            continue
        slot_level, resource_id = access
        if action.area is not None:
            for placement in legal_area_placements(caster, setup, action.area, action.range_ft):
                if protected.intersection(placement.friendly_ids):
                    continue
                score = _area_score(placement, members, action)
                target_ids = (*placement.enemy_ids, *placement.friendly_ids)
                candidates.append((score, -action.level, -index, SpellChoice(action, slot_level, target_ids, placement, score, resource_id)))
            continue
        if action.area_radius_ft is not None:
            placement = best_area_placement(caster, setup, action.area_radius_ft, action.range_ft, protected)
            if placement is None:
                continue
            target_ids = (*placement.enemy_ids, *placement.friendly_ids)
            score = _area_score(placement, members, action)
            choice = SpellChoice(action, slot_level, target_ids, placement, score, resource_id)
            candidates.append((score, -action.level, -index, choice))
            continue
        legal = _legal_single_targets(caster, setup, action)
        if not legal:
            continue
        target = max(
            legal,
            key=lambda item: (save_spell_expected_damage(item, action), -item.state.current_hp, item.combatant_id),
        )
        score = save_spell_expected_damage(target, action)
        choice = SpellChoice(action, slot_level, (target.combatant_id,), expected_damage=score, resource_id=resource_id)
        candidates.append((score, -action.level, -index, choice))
    return max(candidates, key=lambda item: item[:3])[3] if candidates else None
