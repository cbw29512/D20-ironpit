from __future__ import annotations

import logging
from dataclasses import dataclass

from app.combat.action_economy import is_available
from app.combat.encounter_targeting import combatant_distance
from app.combat.offense_value import save_spell_expected_damage
from app.combat.spell_area import AreaPlacement, best_area_placement
from app.combat.spellcasting import slot_spell_available
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.spells import SpellSaveAction

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class SpellChoice:
    action: SpellSaveAction
    slot_level: int
    target_ids: tuple[str, ...]
    placement: AreaPlacement | None = None
    expected_damage: float = 0.0


def spell_at_slot(action: SpellSaveAction, slot_level: int) -> SpellSaveAction:
    """Return the source spell scaled only by its declared higher-slot rule."""
    try:
        if action.level == 0:
            if slot_level != 0:
                raise ValueError("Cantrips cannot expend spell slots.")
            return action
        if slot_level < action.level or slot_level > 9:
            raise ValueError(f"Illegal slot level {slot_level} for {action.name}.")
        levels_above = slot_level - action.level
        if levels_above == 0:
            return action
        if action.upcast_dice_per_level <= 0:
            raise ValueError(f"{action.name} has no certified higher-slot scaling.")
        if action.damage_components:
            raise ValueError("Multi-component spell upcasting requires component-specific scaling data.")
        return action.model_copy(update={
            "damage_dice_count": action.damage_dice_count + levels_above * action.upcast_dice_per_level,
        })
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Failed to scale spell %s for slot level %s.", action.id, slot_level)
        raise RuntimeError("Spell higher-slot scaling could not be evaluated.") from exc


def _slot_levels(caster: EncounterCombatant, action: SpellSaveAction, turn_key: str) -> tuple[int, ...]:
    try:
        if action.level == 0:
            return (0,)
        if not slot_spell_available(caster.state, turn_key):
            return ()
        maximum = 9 if action.upcast_dice_per_level > 0 else action.level
        levels = []
        for level in range(action.level, maximum + 1):
            resource = next((item for item in caster.state.resources if item.id == f"spell-slot-{level}"), None)
            if resource is not None and resource.current_uses > 0:
                levels.append(level)
        return tuple(levels)
    except Exception as exc:
        logger.exception("Failed to determine legal slot levels for %s.", action.id)
        raise RuntimeError("Spell-slot options could not be evaluated.") from exc


def _legal_single_targets(caster: EncounterCombatant, setup: EncounterSetup, action: SpellSaveAction):
    try:
        enemies = setup.monsters if caster.side == "heroes" else setup.heroes
        return [
            target for target in enemies
            if target.state.is_alive and not target.state.is_dead and target.state.current_hp > 0
            and combatant_distance(caster, target) <= action.range_ft
        ]
    except Exception as exc:
        logger.exception("Failed to determine legal targets for spell %s.", action.id)
        raise RuntimeError("Spell targets could not be evaluated.") from exc


def choose_spell(
    caster: EncounterCombatant,
    setup: EncounterSetup,
    turn_key: str,
    protected_ally_ids: set[str] | None = None,
) -> SpellChoice | None:
    try:
        candidates: list[tuple[float, int, int, SpellChoice]] = []
        members = {member.combatant_id: member for member in [*setup.heroes, *setup.monsters]}
        for index, action in enumerate(caster.state.template.spell_save_actions):
            if action.action_cost == "reaction" or action.concentration or not is_available(caster.state, action.action_cost):
                continue
            for slot_level in _slot_levels(caster, action, turn_key):
                scaled = spell_at_slot(action, slot_level)
                if action.area_radius_ft is not None:
                    placement = best_area_placement(caster, setup, action.area_radius_ft, action.range_ft, protected_ally_ids)
                    if placement is None:
                        continue
                    target_ids = (*placement.enemy_ids, *placement.friendly_ids)
                    score = sum(save_spell_expected_damage(members[target_id], scaled) for target_id in placement.enemy_ids)
                    score -= sum(save_spell_expected_damage(members[target_id], scaled) for target_id in placement.friendly_ids)
                    choice = SpellChoice(action, slot_level, target_ids, placement, score)
                    candidates.append((score, -action.level, -index, choice))
                    continue
                legal = _legal_single_targets(caster, setup, action)
                if not legal:
                    continue
                target = max(
                    legal,
                    key=lambda item: (save_spell_expected_damage(item, scaled), -item.state.current_hp, item.combatant_id),
                )
                score = save_spell_expected_damage(target, scaled)
                candidates.append((score, -action.level, -index, SpellChoice(
                    action, slot_level, (target.combatant_id,), expected_damage=score,
                )))
        return max(candidates, key=lambda item: item[:3])[3] if candidates else None
    except Exception:
        logger.exception("Failed to choose save-based spell for %s.", caster.combatant_id)
        raise
