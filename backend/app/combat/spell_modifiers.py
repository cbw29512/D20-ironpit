from __future__ import annotations

from collections.abc import Iterable
import logging

from app.combat.concentration import start_concentration
from app.combat.modifier_stack import add_modifier
from app.combat.timed_conditions import apply_timed_condition
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
    source_name: str | None = None,
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
        source_name=source_name,
        source_is_magical=True,
        kind=ModifierKind(effect.kind),
        flat_bonus=effect.flat_bonus,
        minimum_value=effect.minimum_value,
        dice_count=effect.dice_count,
        dice_size=effect.dice_size,
        damage_type=DamageType(effect.damage_type) if effect.damage_type else None,
        target_id=None if effect.kind == "bonus-damage" and target_id == source_id else target_id,
        condition_id=effect.condition_id,
        debuff_counter=effect.debuff_counter,
        replacement_hp=effect.replacement_hp,
        prevents_instant_death=effect.prevents_instant_death,
        source_creature_types=list(effect.source_creature_types),
        required_effect_tags=list(effect.required_effect_tags),
        bypass_attacker_senses=list(effect.bypass_attacker_senses),
        save_ability=effect.save_ability,
        save_dc=effect.save_dc,
        concentration_required=concentration_required,
        consume_on_attack_against=effect.consume_on_attack_against,
        ends_on_owner_attack=effect.ends_on_owner_attack,
        expires_at_start_of_source_turn=effect.expires_at_start_of_source_turn,
        expires_source_turn_end_round=expiry,
    )


def apply_spell_modifiers(
    owner: CombatantState,
    targets: list[tuple[str, CombatantState]],
    source_id: str,
    spell: DefensiveSpellAction,
    round_number: int,
    affected_states: Iterable[CombatantState] | None = None,
    *,
    duration_minutes: int | None = None,
) -> list[CombatModifier]:
    try:
        built = [
            (target, build_spell_modifier(
                source_id, target_id, spell.id, effect, index, spell.name,
                concentration_required=spell.concentration, round_number=round_number,
            ))
            for target_id, target in targets
            for index, effect in enumerate(spell.modifier_effects)
        ]
        modifiers = [modifier for _, modifier in built]
        duration_rounds = (spell.duration_minutes if duration_minutes is None else duration_minutes) * 10
        expires_round = round_number + duration_rounds + (1 if round_number == 0 else 0)
        if spell.concentration:
            start_concentration(
                owner, source_id, spell.id, round_number, affected_states,
                expires_round=expires_round,
            )
        for target_id, target in targets:
            # Finite nonconcentration modifiers need a source-owned lifetime too.
            # Preserve owned defenses already attached to this same source-owned effect.
            if not spell.concentration and spell.modifier_effects and duration_rounds > 0:
                existing = next(
                    (
                        effect for effect in target.timed_effects
                        if effect.effect_id == spell.id
                        and effect.source_id == source_id
                        and effect.source_effect_id == spell.id
                    ),
                    None,
                )
                apply_timed_condition(
                    target, spell.id, source_id, source_effect_id=spell.id,
                    source_template=owner.template, source_is_magical=True,
                    applied_round=round_number, expires_round=expires_round,
                    expiry_timing="source_turn_start", use_default_poison_recovery=False,
                    owned_damage_resistances=list(existing.owned_damage_resistances) if existing else [],
                    owned_debuff_counters=list(existing.owned_debuff_counters) if existing else [],
                    owned_movement_mode_grants=list(existing.owned_movement_mode_grants) if existing else [],
                    ends_if_source_dead=existing.ends_if_source_dead if existing else False,
                    ends_if_source_incapacitated=existing.ends_if_source_incapacitated if existing else False,
                )
            if spell.movement_mode_grants:
                apply_timed_condition(
                    target,
                    spell.id,
                    source_id,
                    source_effect_id=spell.id,
                    source_template=owner.template,
                    source_is_magical=True,
                    applied_round=round_number,
                    expires_round=expires_round,
                    expiry_timing="source_turn_start",
                    owned_movement_mode_grants=spell.movement_mode_grants,
                    affected_states=list(affected_states or []),
                    use_default_poison_recovery=False,
                )
            for condition_id in spell.condition_ids:
                apply_timed_condition(
                    target,
                    condition_id,
                    source_id,
                    source_effect_id=spell.id,
                    source_template=owner.template,
                    source_is_magical=True,
                    applied_round=round_number,
                    expires_round=expires_round,
                    expiry_timing="source_turn_start",
                    affected_states=list(affected_states or []),
                    use_default_poison_recovery=False,
                )
        for target, modifier in built:
            add_modifier(target, modifier)
        return modifiers
    except Exception:
        logging.getLogger(__name__).exception("Spell modifier application failed for %s from %s.", spell.id, source_id)
        raise
