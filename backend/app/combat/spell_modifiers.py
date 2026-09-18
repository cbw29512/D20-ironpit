from __future__ import annotations

from collections.abc import Iterable

from app.combat.concentration import start_concentration
from app.combat.modifier_stack import add_modifier
from app.domain.combatants import DamageType
from app.domain.modifiers import CombatModifier, ModifierKind
from app.domain.runtime import CombatantState
from app.domain.spells import DefensiveSpellAction, SpellModifierEffect


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
        condition_id=effect.condition_id,
        source_creature_types=list(effect.source_creature_types),
        save_ability=effect.save_ability,
        save_dc=effect.save_dc,
        concentration_required=concentration_required,
        consume_on_attack_against=effect.consume_on_attack_against,
        ends_on_owner_attack=effect.ends_on_owner_attack,
        expires_source_turn_end_round=expiry,
    )


def apply_spell_modifiers(
    owner: CombatantState,
    targets: list[tuple[str, CombatantState]],
    source_id: str,
    spell: DefensiveSpellAction,
    round_number: int,
    affected_states: Iterable[CombatantState] | None = None,
) -> list[CombatModifier]:
    built = [
        (target, build_spell_modifier(
            source_id, target_id, spell.id, effect, index,
            concentration_required=spell.concentration, round_number=round_number,
        ))
        for target_id, target in targets
        for index, effect in enumerate(spell.modifier_effects)
    ]
    modifiers = [modifier for _, modifier in built]
    if spell.concentration:
        duration_rounds = spell.duration_minutes * 10
        expires_round = round_number + duration_rounds + (1 if round_number == 0 else 0)
        start_concentration(
            owner, source_id, spell.id, round_number, affected_states,
            expires_round=expires_round,
        )
    for target, modifier in built:
        add_modifier(target, modifier)
    return modifiers
