from __future__ import annotations

import logging

from app.combat.action_economy import is_available
from app.combat.area_targeting import legal_area_placements
from app.combat.offense_value import save_spell_expected_damage
from app.combat.spell_area import best_area_placement
from app.combat.spell_choice import SpellChoice
from app.combat.spell_policy import legal_single_spell_targets, spell_at_slot
from app.combat.spellcasting import legal_slot_levels
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.spells import SpellSaveAction

logger = logging.getLogger(__name__)


def choose_spell_action_at_slot(
    caster: EncounterCombatant,
    setup: EncounterSetup,
    action: SpellSaveAction,
    slot_level: int,
    protected_ally_ids: set[str] | None = None,
) -> SpellChoice | None:
    """Choose targets for one already-declared save spell at a fixed slot level."""
    try:
        if action.action_cost == "reaction" or not is_available(caster.state, action.action_cost):
            return None
        scaled = spell_at_slot(action, slot_level)
        protected = protected_ally_ids or set()
        members = {
            member.combatant_id: member
            for member in [*setup.heroes, *setup.monsters]
        }
        if action.area is not None:
            placements = [
                item
                for item in legal_area_placements(caster, setup, action.area, action.range_ft)
                if not item.friendly_ids
            ]
            if not placements:
                return None
            placement = max(
                placements,
                key=lambda item: (
                    len(item.enemy_ids),
                    len([target for target in item.enemy_ids if target not in protected]),
                    -len(item.friendly_ids),
                ),
            )
            return SpellChoice(
                action=action,
                slot_level=slot_level,
                target_ids=tuple(placement.enemy_ids),
                placement=placement,
                expected_damage=sum(
                    save_spell_expected_damage(members[target_id], scaled)
                    for target_id in placement.enemy_ids
                ),
            )
        if action.area_radius_ft is not None:
            placement = best_area_placement(
                caster,
                setup,
                action.area_radius_ft,
                action.range_ft,
                protected,
            )
            if placement is None:
                return None
            return SpellChoice(
                action=action,
                slot_level=slot_level,
                target_ids=tuple((*placement.enemy_ids, *placement.friendly_ids)),
                placement=placement,
                expected_damage=(
                    sum(
                        save_spell_expected_damage(members[target_id], scaled)
                        for target_id in placement.enemy_ids
                    )
                    - sum(
                        save_spell_expected_damage(members[target_id], scaled)
                        for target_id in placement.friendly_ids
                    )
                ),
            )
        legal = legal_single_spell_targets(caster, setup, action)
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
        return SpellChoice(
            action=action,
            slot_level=slot_level,
            target_ids=(target.combatant_id,),
            expected_damage=save_spell_expected_damage(target, scaled),
        )
    except Exception:
        logger.exception(
            "Failed to choose fixed-slot save spell %s for %s.",
            action.id,
            caster.combatant_id,
        )
        raise


def choose_named_spell(
    caster: EncounterCombatant,
    setup: EncounterSetup,
    turn_key: str,
    spell_id: str,
    protected_ally_ids: set[str] | None = None,
) -> SpellChoice | None:
    """Choose one declared save spell by id without changing global spell prioritization."""
    try:
        action = next(
            (item for item in caster.state.template.spell_save_actions if item.id == spell_id),
            None,
        )
        if action is None:
            return None
        levels = legal_slot_levels(
            caster.state,
            turn_key,
            action.level,
            higher_slot_scaling=action.upcast_dice_per_level > 0,
        )
        if not levels:
            return None
        return choose_spell_action_at_slot(
            caster,
            setup,
            action,
            levels[-1],
            protected_ally_ids,
        )
    except Exception:
        logger.exception(
            "Failed to choose named save spell %s for %s.",
            spell_id,
            caster.combatant_id,
        )
        raise
