from __future__ import annotations

import logging
from dataclasses import replace

from app.combat.action_economy import is_available
from app.combat.spell_choice import SpellChoice
from app.combat.spell_feature_rules import legal_save_spell_levels, should_auto_maximize_damage
from app.combat.spell_policy_targeting import (
    area_spell_choice,
    legacy_radius_spell_choice,
    legal_single_spell_targets,
    single_target_spell_choice,
)
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
            for slot_level in legal_save_spell_levels(caster.state, turn_key, action):
                scaled = spell_at_slot(action, slot_level)
                if action.area is not None:
                    choice = area_spell_choice(
                        caster, setup, action, slot_level, scaled, members,
                    )
                elif action.area_radius_ft is not None:
                    choice = legacy_radius_spell_choice(
                        caster,
                        setup,
                        action,
                        slot_level,
                        scaled,
                        members,
                        protected_ally_ids,
                    )
                else:
                    choice = single_target_spell_choice(
                        caster, setup, action, slot_level, scaled,
                    )
                if choice is not None:
                    if should_auto_maximize_damage(caster.state, action):
                        choice = replace(choice, maximize_damage=True)
                    candidates.append((
                        choice.expected_damage,
                        -action.level,
                        -index,
                        choice,
                    ))
        return max(candidates, key=lambda item: item[:3])[3] if candidates else None
    except Exception:
        logger.exception(
            "Failed to choose save-based spell for %s.",
            caster.combatant_id,
        )
        raise
