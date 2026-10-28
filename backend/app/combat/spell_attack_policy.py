from __future__ import annotations

from dataclasses import dataclass
import logging

from app.combat.barrier_line_of_effect import clear_line_between_members
from app.combat.action_economy import is_available
from app.combat.alternate_spell_casts import available_alternate_casts
from app.combat.encounter_targeting import combatant_distance
from app.combat.offense_value import spell_attack_expected_damage
from app.combat.spell_range_modifiers import choose_spell_range_modifier, effective_spell_range_ft
from app.combat.spellcasting import legal_slot_levels
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.spell_cast_modifiers import ResourceBackedSpellRangeModifier
from app.domain.spells import SpellAttackAction
from app.domain.alternate_spell_casts import AlternateSpellCastGrant

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class SpellAttackChoice:
    action: SpellAttackAction
    target: EncounterCombatant
    expected_damage: float
    slot_level: int = 0
    range_modifier: ResourceBackedSpellRangeModifier | None = None
    alternate_cast: AlternateSpellCastGrant | None = None


def _cast_options(
    caster: EncounterCombatant, action: SpellAttackAction, turn_key: str,
) -> tuple[tuple[int, AlternateSpellCastGrant | None], ...]:
    try:
        slots = legal_slot_levels(
            caster.state,
            turn_key,
            action.level,
            higher_slot_scaling=(
                action.attacks_per_slot_above > 0 or action.upcast_dice_per_level > 0
            ),
        )
        alternates = available_alternate_casts(caster.state, action.id)
        return tuple((level, None) for level in slots) + tuple(
            (grant.cast_level, grant) for grant in alternates
        )
    except Exception:
        logger.exception(
            "Failed to build spell-attack cast options for %s using %s on %s.",
            caster.combatant_id,
            action.id,
            turn_key,
        )
        raise


def choose_spell_attack(
    caster: EncounterCombatant,
    setup: EncounterSetup,
    turn_key: str,
) -> SpellAttackChoice | None:
    enemies = setup.monsters if caster.side == "heroes" else setup.heroes
    candidates: list[tuple[float, int, int, int, int, str, SpellAttackAction, EncounterCombatant, ResourceBackedSpellRangeModifier | None, AlternateSpellCastGrant | None]] = []
    for index, action in enumerate(caster.state.template.spell_attack_actions):
        if action.action_cost == "reaction" or not is_available(caster.state, action.action_cost):
            continue
        cast_options = _cast_options(caster, action, turn_key)
        if not cast_options:
            continue
        effective_range = effective_spell_range_ft(caster.state, action.range_ft)
        for slot_level, alternate_cast in cast_options:
            attack_count = action.attack_count_at_slot(slot_level)
            for target in enemies:
                distance = combatant_distance(caster, target)
                if (
                    not target.state.is_alive or target.state.is_dead or target.state.current_hp <= 0
                    or distance > effective_range
                    or not clear_line_between_members(caster, target, setup)
                ):
                    continue
                range_modifier = choose_spell_range_modifier(
                    caster.state,
                    base_range_ft=action.range_ft,
                    required_range_ft=distance,
                )
                scaled = action.model_copy(
                    update={"damage_dice_count": action.damage_dice_at_slot(slot_level)},
                )
                score = spell_attack_expected_damage(caster, target, scaled, setup) * attack_count
                candidates.append((
                    score, -int(alternate_cast is not None), -slot_level, -action.level,
                    -target.state.current_hp, target.combatant_id, action, target,
                    range_modifier, alternate_cast,
                ))
    if not candidates:
        return None
    score, _, neg_slot, _, _, _, action, target, range_modifier, alternate_cast = max(
        candidates, key=lambda item: item[:6]
    )
    return SpellAttackChoice(action, target, score, -neg_slot, range_modifier, alternate_cast)
