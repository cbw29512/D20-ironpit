from __future__ import annotations

import logging

from app.combat.action_economy import is_available
from app.combat.condition_rules import can_see
from app.combat.encounter_targeting import combatant_distance
from app.combat.offense_value import save_spell_expected_damage
from app.combat.spell_area import best_area_placement
from app.combat.spell_choice import SpellChoice
from app.combat.spellcasting import legal_slot_levels
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.spells import SpellSaveAction

logger = logging.getLogger(__name__)


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
            raise ValueError(
                "Multi-component spell upcasting requires component-specific scaling data."
            )
        return action.model_copy(update={
            "damage_dice_count": (
                action.damage_dice_count
                + levels_above * action.upcast_dice_per_level
            ),
        })
    except ValueError:
        raise
    except Exception as exc:
        logger.exception(
            "Failed to scale spell %s for slot level %s.",
            action.id,
            slot_level,
        )
        raise RuntimeError("Spell higher-slot scaling could not be evaluated.") from exc


def legal_single_spell_targets(
    caster: EncounterCombatant,
    setup: EncounterSetup,
    action: SpellSaveAction,
) -> list[EncounterCombatant]:
    """Return legal hostile targets for one single-target save spell."""
    try:
        enemies = setup.monsters if caster.side == "heroes" else setup.heroes
        return [
            target
            for target in enemies
            if target.state.is_alive
            and not target.state.is_dead
            and target.state.current_hp > 0
            and combatant_distance(caster, target) <= action.range_ft
            and (
                not action.requires_target_hearing
                or "deafened" not in target.state.active_effect_ids
            )
            and (
                not action.requires_target_sight
                or can_see(caster.state, target.state)
            )
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
    """Choose the highest-value legal non-Concentration save spell."""
    try:
        candidates: list[tuple[float, int, int, SpellChoice]] = []
        members = {
            member.combatant_id: member
            for member in [*setup.heroes, *setup.monsters]
        }
        for index, action in enumerate(caster.state.template.spell_save_actions):
            if (
                action.action_cost == "reaction"
                or action.concentration
                or not is_available(caster.state, action.action_cost)
            ):
                continue
            for slot_level in legal_slot_levels(
                caster.state,
                turn_key,
                action.level,
                higher_slot_scaling=action.upcast_dice_per_level > 0,
            ):
                scaled = spell_at_slot(action, slot_level)
                if action.area_radius_ft is not None:
                    placement = best_area_placement(
                        caster,
                        setup,
                        action.area_radius_ft,
                        action.range_ft,
                        protected_ally_ids,
                    )
                    if placement is None:
                        continue
                    target_ids = (*placement.enemy_ids, *placement.friendly_ids)
                    score = sum(
                        save_spell_expected_damage(members[target_id], scaled)
                        for target_id in placement.enemy_ids
                    )
                    score -= sum(
                        save_spell_expected_damage(members[target_id], scaled)
                        for target_id in placement.friendly_ids
                    )
                    choice = SpellChoice(
                        action,
                        slot_level,
                        target_ids,
                        placement,
                        score,
                    )
                    candidates.append((score, -action.level, -index, choice))
                    continue

                legal = legal_single_spell_targets(caster, setup, action)
                if not legal:
                    continue
                target = max(
                    legal,
                    key=lambda item: (
                        save_spell_expected_damage(item, scaled),
                        -item.state.current_hp,
                        item.combatant_id,
                    ),
                )
                score = save_spell_expected_damage(target, scaled)
                candidates.append((
                    score,
                    -action.level,
                    -index,
                    SpellChoice(
                        action,
                        slot_level,
                        (target.combatant_id,),
                        expected_damage=score,
                    ),
                ))
        return max(candidates, key=lambda item: item[:3])[3] if candidates else None
    except Exception:
        logger.exception(
            "Failed to choose save-based spell for %s.",
            caster.combatant_id,
        )
        raise
