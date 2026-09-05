from __future__ import annotations

from app.combat.condition_rules import automatically_fails_strength_dexterity_save, close_hit_is_automatic_critical
from app.combat.conditions import attack_roll_condition_sources
from app.combat.damage_defenses import adjusted_damage_amount
from app.combat.encounter_targeting import close_ranged_threat_exists, combatant_distance
from app.combat.modifier_stack import attacks_against_advantage_sources, effective_armor_class
from app.combat.rolls import attack_roll_hits, resolve_roll_mode
from app.combat.saving_throw_rolls import saving_throw_mode
from app.domain.combatants import DamageType
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import RollMode
from app.domain.modifiers import ModifierKind
from app.domain.spells import SpellAttackAction, SpellSaveAction


def _d20_distribution(mode: RollMode) -> dict[int, float]:
    if mode is RollMode.NORMAL:
        return {value: 1 / 20 for value in range(1, 21)}
    if mode is RollMode.ADVANTAGE:
        return {value: (value * value - (value - 1) * (value - 1)) / 400 for value in range(1, 21)}
    return {value: ((21 - value) ** 2 - (20 - value) ** 2) / 400 for value in range(1, 21)}


def _bonus_distribution(state, kind: ModifierKind) -> dict[int, float]:
    distribution = {0: 1.0}
    for modifier in state.active_modifiers:
        if modifier.kind is not kind:
            continue
        for _ in range(modifier.dice_count):
            next_distribution: dict[int, float] = {}
            for subtotal, probability in distribution.items():
                for face in range(1, modifier.dice_size + 1):
                    value = subtotal + face
                    next_distribution[value] = next_distribution.get(value, 0.0) + probability / modifier.dice_size
            distribution = next_distribution
    return distribution


def _damage_factor(target, damage_type: DamageType | None) -> float:
    if damage_type is None:
        return 0.0
    return adjusted_damage_amount(2, damage_type, target) / 2


def _mean_damage(count: int, size: int, bonus: int = 0) -> float:
    return count * (size + 1) / 2 + bonus


def _attack_probabilities(state, bonus: int, armor_class: int, mode: RollMode, critical_minimum: int = 20) -> tuple[float, float]:
    bonus_distribution = _bonus_distribution(state, ModifierKind.ATTACK_ROLL_BONUS_DIE)
    hit = critical = 0.0
    for natural, natural_probability in _d20_distribution(mode).items():
        for extra, extra_probability in bonus_distribution.items():
            probability = natural_probability * extra_probability
            succeeds = attack_roll_hits(natural, natural + bonus + extra, armor_class)
            if succeeds:
                hit += probability
                if natural >= critical_minimum:
                    critical += probability
    return hit, critical


def spell_attack_expected_damage(
    caster: EncounterCombatant, target: EncounterCombatant, spell: SpellAttackAction, setup: EncounterSetup,
) -> float:
    distance = combatant_distance(caster, target)
    advantage, disadvantage = attack_roll_condition_sources(caster.state, target.state, distance, target.combatant_id)
    advantage += attacks_against_advantage_sources(target.state)
    disadvantage += int(close_ranged_threat_exists(caster, setup))
    mode = resolve_roll_mode(advantage, disadvantage)
    hit, critical = _attack_probabilities(caster.state, spell.attack_bonus, effective_armor_class(target.state), mode)
    if close_hit_is_automatic_critical(target.state) and distance <= 5:
        critical = hit
    factor = _damage_factor(target.state, DamageType(spell.damage_type) if spell.damage_type else None)
    normal = _mean_damage(spell.damage_dice_count, spell.damage_dice_size, spell.damage_bonus) * factor
    crit = _mean_damage(spell.damage_dice_count * 2, spell.damage_dice_size, spell.damage_bonus) * factor
    return max(0.0, (hit - critical) * normal + critical * crit)


def _save_success_probability(target, action: SpellSaveAction) -> float:
    if action.save_ability in {"strength", "dexterity"} and automatically_fails_strength_dexterity_save(target.state):
        return 0.0
    bonus = target.state.template.saving_throw_bonuses[action.save_ability]
    mode = saving_throw_mode(target.state, action.save_ability, magical=True)
    bonus_distribution = _bonus_distribution(target.state, ModifierKind.SAVING_THROW_BONUS_DIE)
    success = 0.0
    for natural, natural_probability in _d20_distribution(mode).items():
        for extra, extra_probability in bonus_distribution.items():
            if natural + bonus + extra >= action.dc:
                success += natural_probability * extra_probability
    return success


def save_spell_expected_damage(target: EncounterCombatant, action: SpellSaveAction) -> float:
    if not action.damage_dice_count or not action.damage_type:
        return 0.0
    success = _save_success_probability(target, action)
    factor = _damage_factor(target.state, DamageType(action.damage_type))
    full = _mean_damage(action.damage_dice_count, action.damage_dice_size, action.damage_bonus) * factor
    on_success = full * 0.5 if action.success_damage == "half" else 0.0
    return max(0.0, (1 - success) * full + success * on_success)
