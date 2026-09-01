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
    spell: DefensiveSpellAction,
    effect: SpellModifierEffect,
    index: int,
) -> CombatModifier:
    return CombatModifier(
        id=f"{source_id}:{spell.id}:{target_id}:{index}",
        source_id=source_id,
        source_effect_id=spell.id,
        kind=ModifierKind(effect.kind),
        flat_bonus=effect.flat_bonus,
        dice_count=effect.dice_count,
        dice_size=effect.dice_size,
        damage_type=DamageType(effect.damage_type) if effect.damage_type else None,
        target_id=target_id,
        concentration_required=spell.concentration,
    )


def apply_spell_modifiers(
    owner: CombatantState,
    target: CombatantState,
    source_id: str,
    target_id: str,
    spell: DefensiveSpellAction,
    round_number: int,
    affected_states: Iterable[CombatantState] | None = None,
) -> list[CombatModifier]:
    modifiers = [
        build_spell_modifier(source_id, target_id, spell, effect, index)
        for index, effect in enumerate(spell.modifier_effects)
    ]
    if spell.concentration:
        start_concentration(owner, source_id, spell.id, round_number, affected_states)
    for modifier in modifiers:
        add_modifier(target, modifier)
    return modifiers
