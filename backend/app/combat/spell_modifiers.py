from __future__ import annotations

from collections.abc import Iterable

from app.combat.concentration import start_concentration
from app.combat.modifier_stack import add_modifier
from app.domain.combatants import DamageType
from app.domain.modifiers import CombatModifier, ModifierKind
from app.domain.reactive_damage import MeleeHitReactiveDamage
from app.domain.runtime import CombatantState
from app.domain.spells import DefensiveSpellAction, SpellModifierEffect

_REACTIVE_KIND = "adjacent-melee-hit-reactive-damage"


def build_spell_modifier(
    source_id: str,
    target_id: str,
    spell_id: str,
    effect: SpellModifierEffect,
    index: int,
    *,
    concentration_required: bool = False,
    round_number: int | None = None,
) -> CombatModifier:
    if effect.kind == _REACTIVE_KIND:
        raise ValueError("Reactive spell effects compile to combat state, not CombatModifier.")
    expiry = None
    if effect.expires_after_source_turns is not None:
        if round_number is None:
            raise ValueError("Source-turn modifier expiry requires the application round.")
        expiry = round_number + effect.expires_after_source_turns
    return CombatModifier(
        id=f"{source_id}:{spell_id}:{target_id}:{index}",
        source_id=source_id,
        source_effect_id=spell_id,
        kind=ModifierKind(effect.kind),
        flat_bonus=effect.flat_bonus,
        dice_count=effect.dice_count,
        dice_size=effect.dice_size,
        damage_type=DamageType(effect.damage_type) if effect.damage_type else None,
        target_id=target_id,
        concentration_required=concentration_required,
        consume_on_attack_against=effect.consume_on_attack_against,
        expires_at_start_of_source_turn=effect.expires_at_start_of_source_turn,
        expires_source_turn_end_round=expiry,
    )


def _apply_reactive_effect(target: CombatantState, spell_id: str, effect: SpellModifierEffect, index: int) -> None:
    if effect.damage_type is None:
        raise ValueError("Reactive spell damage requires a damage type.")
    rule = MeleeHitReactiveDamage(
        id=f"{spell_id}:{index}", range_ft=5, dice_count=effect.dice_count,
        dice_size=effect.dice_size, damage_bonus=effect.flat_bonus,
        damage_type=effect.damage_type,
    )
    if rule.id not in {item.id for item in target.temporary_melee_hit_reactive_damage}:
        target.temporary_melee_hit_reactive_damage.append(rule)


def apply_spell_modifiers(
    owner: CombatantState,
    targets: list[tuple[str, CombatantState]],
    source_id: str,
    spell: DefensiveSpellAction,
    round_number: int,
    affected_states: Iterable[CombatantState] | None = None,
) -> list[CombatModifier]:
    ordinary = [(index, effect) for index, effect in enumerate(spell.modifier_effects) if effect.kind != _REACTIVE_KIND]
    modifiers = [
        build_spell_modifier(
            source_id, target_id, spell.id, effect, index,
            concentration_required=spell.concentration, round_number=round_number,
        )
        for target_id, _ in targets
        for index, effect in ordinary
    ]
    if spell.concentration:
        duration_rounds = spell.duration_minutes * 10
        expires_round = round_number + duration_rounds + (1 if round_number == 0 else 0)
        start_concentration(
            owner, source_id, spell.id, round_number, affected_states,
            expires_round=expires_round,
        )
    for target_id, target in targets:
        for index, effect in enumerate(spell.modifier_effects):
            if effect.kind == _REACTIVE_KIND:
                _apply_reactive_effect(target, spell.id, effect, index)
                continue
            add_modifier(target, build_spell_modifier(
                source_id, target_id, spell.id, effect, index,
                concentration_required=spell.concentration, round_number=round_number,
            ))
    return modifiers
