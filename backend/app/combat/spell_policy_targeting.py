from __future__ import annotations

import logging
from dataclasses import replace

from app.combat.barrier_line_of_effect import clear_line_between_members
from app.combat.area_spell_ally_protection import eligible_area_spell_allies
from app.combat.area_targeting import legal_area_placements
from app.combat.condition_rules import can_see
from app.combat.encounter_targeting import combatant_distance
from app.combat.offense_value import save_spell_expected_damage
from app.combat.spell_area import best_area_placement
from app.combat.spell_choice import SpellChoice
from app.combat.spell_range_modifiers import choose_spell_range_modifier, effective_spell_range_ft
from app.content.monster_creature_types import is_creature_type
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.spells import SpellSaveAction

logger = logging.getLogger(__name__)


def legal_single_spell_targets(
    caster: EncounterCombatant,
    setup: EncounterSetup,
    action: SpellSaveAction,
    *,
    range_ft: int | None = None,
) -> list[EncounterCombatant]:
    try:
        enemies = setup.monsters if caster.side == "heroes" else setup.heroes
        limit = action.range_ft if range_ft is None else range_ft
        return [
            target for target in enemies
            if target.state.is_alive
            and not target.state.is_dead
            and target.state.current_hp > 0
            and combatant_distance(caster, target) <= limit
            and clear_line_between_members(caster, target, setup)
            and (not action.requires_target_hearing or "deafened" not in target.state.active_effect_ids)
            and (not action.requires_target_sight or can_see(caster.state, target.state))
            and (
                not action.required_target_creature_types
                or any(
                    is_creature_type(target.state.template, kind)
                    for kind in action.required_target_creature_types
                )
            )
        ]
    except Exception as exc:
        logger.exception("Failed to determine legal targets for spell %s.", action.id)
        raise RuntimeError("Spell targets could not be evaluated.") from exc


def area_spell_choice(
    caster: EncounterCombatant,
    setup: EncounterSetup,
    action: SpellSaveAction,
    slot_level: int,
    scaled: SpellSaveAction,
    members: dict[str, EncounterCombatant],
) -> SpellChoice | None:
    base_range = action.range_ft
    effective_range = (
        effective_spell_range_ft(caster.state, base_range)
        if action.area is not None and action.area.origin == "point"
        else base_range
    )
    base_placements = legal_area_placements(caster, setup, action.area, base_range)
    protected_ids, protected_limit = eligible_area_spell_allies(caster, setup, action, slot_level)
    placements = []
    for item in legal_area_placements(caster, setup, action.area, effective_range):
        friendly = tuple(item.friendly_ids)
        can_protect = (
            bool(friendly)
            and len(friendly) <= protected_limit
            and set(friendly).issubset(protected_ids)
        )
        if friendly and not can_protect:
            continue
        placements.append(
            replace(item, friendly_ids=(), protected_friendly_ids=friendly)
            if can_protect else item
        )
    if not placements:
        return None
    placement = max(placements, key=lambda item: (len(item.enemy_ids), -len(item.friendly_ids)))
    score = sum(save_spell_expected_damage(members[target_id], scaled) for target_id in placement.enemy_ids)
    modifier = None
    if placement not in base_placements:
        modifier = choose_spell_range_modifier(
            caster.state,
            base_range_ft=base_range,
            required_range_ft=effective_range,
        )
    return SpellChoice(action, slot_level, tuple(placement.enemy_ids), placement, score, modifier)


def legacy_radius_spell_choice(
    caster: EncounterCombatant,
    setup: EncounterSetup,
    action: SpellSaveAction,
    slot_level: int,
    scaled: SpellSaveAction,
    members: dict[str, EncounterCombatant],
    protected_ally_ids: set[str] | None,
) -> SpellChoice | None:
    base_range = action.range_ft
    effective_range = effective_spell_range_ft(caster.state, base_range)
    eligible_ids, protected_limit = eligible_area_spell_allies(caster, setup, action, slot_level)
    explicit_ids = protected_ally_ids or set()
    placement = best_area_placement(
        caster,
        setup,
        action.area_radius_ft,
        effective_range,
        eligible_ids | explicit_ids,
        protected_limit if eligible_ids else None,
    )
    if placement is None:
        return None
    target_ids = (*placement.enemy_ids, *placement.friendly_ids)
    score = sum(save_spell_expected_damage(members[target_id], scaled) for target_id in placement.enemy_ids)
    score -= sum(save_spell_expected_damage(members[target_id], scaled) for target_id in placement.friendly_ids)
    required_range = abs(caster.position_ft - placement.center_ft)
    modifier = choose_spell_range_modifier(
        caster.state,
        base_range_ft=base_range,
        required_range_ft=required_range,
    )
    return SpellChoice(action, slot_level, target_ids, placement, score, modifier)


def single_target_spell_choice(
    caster: EncounterCombatant,
    setup: EncounterSetup,
    action: SpellSaveAction,
    slot_level: int,
    scaled: SpellSaveAction,
) -> SpellChoice | None:
    effective_range = effective_spell_range_ft(caster.state, action.range_ft)
    legal = legal_single_spell_targets(caster, setup, action, range_ft=effective_range)
    if not legal:
        return None
    target = max(
        legal,
        key=lambda item: (
            save_spell_expected_damage(item, scaled),
            -item.state.current_hp,
            item.combatant_id,
        ),
    )
    score = save_spell_expected_damage(target, scaled)
    if scaled.failed_save_timed_effect is not None:
        score += max(8.0, target.state.current_hp * 0.35)
    modifier = choose_spell_range_modifier(
        caster.state,
        base_range_ft=action.range_ft,
        required_range_ft=combatant_distance(caster, target),
    )
    return SpellChoice(
        action,
        slot_level,
        (target.combatant_id,),
        expected_damage=score,
        range_modifier=modifier,
    )
