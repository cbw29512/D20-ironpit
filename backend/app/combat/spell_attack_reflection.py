from __future__ import annotations

from app.combat.condition_rules import close_hit_is_automatic_critical
from app.combat.conditions import attack_roll_condition_sources
from app.combat.encounter_targeting import close_ranged_threat_exists, combatant_distance
from app.combat.modifier_stack import (
    apply_d20_bonus_dice, attacks_against_advantage_sources, consume_attacks_against_advantage,
    consume_next_attack_against_advantage, effective_armor_class, next_attack_against_advantage_sources,
)
from app.combat.reckless_attack import attacks_against_reckless_advantage
from app.combat.rolls import resolve_roll_mode, roll_d20
from app.combat.spell_reflection import reflection_target, spend_spell_reflection
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.modifiers import ModifierKind
from app.domain.spells import SpellAttackAction


def reflect_missed_spell_attack(
    caster: EncounterCombatant,
    reflector: EncounterCombatant,
    spell: SpellAttackAction,
    setup: EncounterSetup,
    dice,
):
    """Reroll one missed single-target spell attack against a deterministic reflected target."""
    target = reflection_target(reflector, caster, setup)
    if target is None:
        return None
    spend_spell_reflection(reflector)
    distance = combatant_distance(caster, target)
    advantage, disadvantage = attack_roll_condition_sources(caster.state, target.state, distance, target.combatant_id)
    advantage += attacks_against_advantage_sources(target.state)
    advantage += attacks_against_reckless_advantage(target.state)
    advantage += next_attack_against_advantage_sources(caster.state, target.combatant_id)
    close_threat = spell.attack_kind == "ranged" and close_ranged_threat_exists(caster, setup)
    mode = resolve_roll_mode(advantage, disadvantage + int(close_threat))
    roll = apply_d20_bonus_dice(
        caster.state, ModifierKind.ATTACK_ROLL_BONUS_DIE,
        roll_d20(dice, spell.attack_bonus, mode), dice,
    )
    consume_next_attack_against_advantage(caster.state, target.combatant_id)
    consume_attacks_against_advantage(target.state)
    ac = effective_armor_class(target.state); natural = roll.selected_roll or 0
    hit = natural != 1 and (natural == 20 or roll.total >= ac)
    critical = bool(hit and (natural == 20 or (close_hit_is_automatic_critical(target.state) and distance <= 5)))
    return target, roll, ac, hit, critical, distance
