"""Targeting and casting choice for a generic non-saving-throw HP-pool spell."""
from __future__ import annotations

import logging
from dataclasses import dataclass

from app.combat.action_economy import is_available
from app.combat.alternate_spell_casts import available_alternate_casts
from app.combat.condition_immunity import condition_is_immune
from app.combat.condition_rules import has_condition
from app.combat.spell_area import AreaPlacement, best_area_placement
from app.combat.spellcasting import legal_slot_levels
from app.domain.alternate_spell_casts import AlternateSpellCastGrant
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.hit_point_pool_spells import HitPointPoolSpellAction

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class PoolSpellChoice:
    action: HitPointPoolSpellAction
    slot_level: int
    placement: AreaPlacement
    alternate_cast: AlternateSpellCastGrant | None
    expected_damage: float  # Tactical impact score, never applied as HP damage.


def eligible_pool_target(
    caster: EncounterCombatant, target: EncounterCombatant,
    action: HitPointPoolSpellAction, setup: EncounterSetup,
) -> bool:
    """Evaluate source-declared exclusions before allocating the universal pool."""
    try:
        state = target.state
        if not state.is_alive or state.is_dead or state.current_hp <= 0:
            return False
        if (state.template.creature_type or "").casefold() in action.excluded_creature_types:
            return False
        if action.skip_unconscious and (
            state.is_unconscious or has_condition(state, "unconscious", setup=setup)
        ):
            return False
        for condition_id in [*action.excluded_condition_immunities, action.condition_id]:
            if condition_is_immune(
                state, condition_id, caster.state.template,
                source_is_magical=True, actor=target, setup=setup,
            ):
                return False
        return True
    except Exception:
        logger.exception("HP-pool target eligibility failed: %s -> %s.", caster.combatant_id, target.combatant_id)
        raise


def choose_hp_pool_spell(
    caster: EncounterCombatant, setup: EncounterSetup, turn_key: str,
) -> PoolSpellChoice | None:
    """Prefer affordable, ally-safe disabling spells using existing slot/area policies."""
    try:
        choices: list[tuple[float, int, int, PoolSpellChoice]] = []
        enemies = setup.monsters if caster.side == "heroes" else setup.heroes
        if not enemies:
            return None
        for index, action in enumerate(caster.state.template.hit_point_pool_spell_actions):
            if action.action_cost == "reaction" or not is_available(caster.state, action.action_cost):
                continue
            eligible_ids = {
                member.combatant_id for member in enemies
                if eligible_pool_target(caster, member, action, setup)
            }
            if not eligible_ids:
                continue
            placement = best_area_placement(
                caster, setup, action.area_radius_ft, action.range_ft,
                eligible_enemy_ids=eligible_ids,
            )
            if placement is None:
                continue
            affected_candidates = sorted(
                member.state.current_hp for member in enemies
                if member.combatant_id in placement.enemy_ids
                and member.combatant_id in eligible_ids
            )
            if not affected_candidates:
                continue
            cast_options = [
                (level, None) for level in legal_slot_levels(
                    caster.state, turn_key, action.level,
                    higher_slot_scaling=action.extra_dice_per_upcast_level > 0,
                )
            ]
            cast_options.extend(
                (grant.cast_level, grant) for grant in available_alternate_casts(caster.state, action.id)
            )
            for slot_level, grant in cast_options:
                count = action.pool_dice_count + (slot_level - action.level) * action.extra_dice_per_upcast_level
                max_pool = count * action.pool_dice_size
                if affected_candidates[0] > max_pool:
                    continue
                mean_pool = count * (action.pool_dice_size + 1) / 2
                covered = 0
                for hp in affected_candidates:
                    if hp > mean_pool:
                        break
                    covered += 1
                    mean_pool -= hp
                # A control action is worth considering even when a low dice roll could fail.
                impact = float(max(1, covered) * 3)
                choice = PoolSpellChoice(action, slot_level, placement, grant, impact)
                choices.append((impact, action.level, -index, choice))
        return max(choices, key=lambda row: row[:3])[3] if choices else None
    except Exception:
        logger.exception("HP-pool spell choice failed for %s.", caster.combatant_id)
        raise
