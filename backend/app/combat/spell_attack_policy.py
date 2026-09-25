from __future__ import annotations

import logging
from dataclasses import dataclass

from app.combat.action_economy import is_available
from app.combat.encounter_targeting import combatant_distance
from app.combat.offense_value import spell_attack_expected_damage
from app.combat.spellcasting import slot_spell_available
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.spells import SpellAttackAction

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class SpellAttackChoice:
    action: SpellAttackAction
    target: EncounterCombatant
    slot_level: int
    expected_damage: float


def spell_attack_at_slot(action: SpellAttackAction, slot_level: int) -> SpellAttackAction:
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
        return action.model_copy(update={
            "damage_dice_count": action.damage_dice_count + levels_above * action.upcast_dice_per_level,
        })
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Failed to scale spell attack %s at slot %s.", action.id, slot_level)
        raise RuntimeError("Spell-attack higher-slot scaling could not be evaluated.") from exc


def legal_spell_attack_slots(
    caster: EncounterCombatant,
    action: SpellAttackAction,
    turn_key: str,
) -> tuple[int, ...]:
    try:
        if action.level == 0:
            return (0,)
        if not slot_spell_available(caster.state, turn_key):
            return ()
        maximum = 9 if action.upcast_dice_per_level > 0 else action.level
        return tuple(
            level for level in range(action.level, maximum + 1)
            if any(
                item.id == f"spell-slot-{level}" and item.current_uses > 0
                for item in caster.state.resources
            )
        )
    except Exception as exc:
        logger.exception("Failed to determine legal spell-attack slots for %s.", action.id)
        raise RuntimeError("Spell-attack slot options could not be evaluated.") from exc


def choose_spell_attack(
    caster: EncounterCombatant,
    setup: EncounterSetup,
    turn_key: str,
) -> SpellAttackChoice | None:
    try:
        enemies = setup.monsters if caster.side == "heroes" else setup.heroes
        candidates: list[tuple[float, int, int, int, str, int, SpellAttackChoice]] = []
        for index, action in enumerate(caster.state.template.spell_attack_actions):
            if action.action_cost == "reaction" or not is_available(caster.state, action.action_cost):
                continue
            for slot_level in legal_spell_attack_slots(caster, action, turn_key):
                scaled = spell_attack_at_slot(action, slot_level)
                for target in enemies:
                    if (
                        not target.state.is_alive or target.state.is_dead or target.state.current_hp <= 0
                        or combatant_distance(caster, target) > action.range_ft
                    ):
                        continue
                    score = spell_attack_expected_damage(caster, target, scaled, setup)
                    choice = SpellAttackChoice(action, target, slot_level, score)
                    candidates.append((
                        score, -slot_level, -action.level, -target.state.current_hp,
                        target.combatant_id, -index, choice,
                    ))
        return max(candidates, key=lambda item: item[:6])[6] if candidates else None
    except Exception:
        logger.exception("Failed to choose spell attack for %s.", caster.combatant_id)
        raise
