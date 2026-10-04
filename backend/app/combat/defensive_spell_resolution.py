from __future__ import annotations

from collections.abc import Iterable

from app.combat.selectable_spell_resistance import choose_spell_resistance_type
from app.combat.spell_modifiers import apply_spell_modifiers
from app.combat.spell_duration_modifiers import effective_spell_duration_minutes, spend_spell_duration_modifier
from app.combat.temporary_hp import grant_temporary_hit_points
from app.combat.timed_conditions import apply_timed_condition
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import BattleEvent, DamageType
from app.domain.runtime import CombatantState
from app.domain.spell_cast_modifiers import ResourceBackedSpellDurationModifier
from app.domain.spells import DefensiveSpellAction, SpellModifierEffect


def _modifier_detail(effect: SpellModifierEffect) -> str:
    if effect.kind == "armor-class":
        return f"{effect.flat_bonus:+d} AC"
    if effect.kind == "armor-class-minimum":
        return f"minimum AC {effect.minimum_value}"
    if effect.kind == "speed":
        return f"{effect.flat_bonus:+d} Speed"
    if effect.dice_count:
        return f"{effect.dice_count}d{effect.dice_size} {effect.kind}"
    return effect.kind


def resolve_defensive_spell(
    sequence: int,
    member: EncounterCombatant,
    targets: list[EncounterCombatant],
    spell: DefensiveSpellAction,
    slot_level: int,
    resource,
    affected_states: Iterable[CombatantState] | None = None,
    *,
    duration_modifier: ResourceBackedSpellDurationModifier | None = None,
    setup: EncounterSetup | None = None,
) -> BattleEvent:
    if slot_level != spell.level:
        raise ValueError("Spell upcasting is not certified; use the spell's printed slot level.")
    if resource.current_uses < 1:
        raise ValueError(f"No level {slot_level} spell slot remains for {spell.name}.")
    if not targets:
        raise ValueError(f"{spell.name} has no legal precombat targets.")
    if member.state.opening_buff_id is not None:
        raise ValueError(f"{member.state.template.name} already committed its one opening buff this battle.")
    if spell.concentration and member.state.concentration is not None:
        raise ValueError(f"{member.state.template.name} is already concentrating and will not replace the active buff automatically.")
    if any(
        spell.id in target.state.active_buff_effect_ids
        or any(modifier.source_effect_id == spell.id for modifier in target.state.active_modifiers)
        or any(effect.source_effect_id == spell.id for effect in target.state.timed_effects)
        for target in targets
    ):
        raise ValueError(f"{spell.name} is already active on a selected target.")
    member.state.opening_buff_id = spell.id
    if not spell.free_opening_cast:
        resource.current_uses -= 1
    duration_remaining = spend_spell_duration_modifier(member.state, duration_modifier)
    effective_duration = effective_spell_duration_minutes(spell.duration_minutes, duration_modifier)
    temp_hp_details: list[str] = []
    for target in targets:
        before = target.state.temporary_hp
        after = grant_temporary_hit_points(target.state, spell.temporary_hp)
        if after > before:
            temp_hp_details.append(f"{target.state.template.name} {after} Temporary HP")
        if spell.max_hp_increase:
            target.state.max_hp_bonus += spell.max_hp_increase
        if spell.current_hp_increase:
            target.state.current_hp += spell.current_hp_increase
        resistances = list(spell.damage_resistances)
        if spell.selectable_resistance_types and setup is not None:
            chosen = choose_spell_resistance_type(member, setup, spell)
            if chosen is not None:
                resistances.append(chosen.value)
        if resistances and (spell.concentration or spell.share_damage_with_source):
            apply_timed_condition(
                target.state,
                spell.id,
                member.combatant_id,
                source_effect_id=spell.id,
                source_template=member.state.template,
                source_is_magical=True,
                owned_damage_resistances=[DamageType(item) for item in resistances],
                applied_round=0,
                expires_round=effective_duration * 10 + 1,
                expiry_timing="source_turn_start",
                ends_if_source_dead=spell.share_damage_with_source,
                use_default_poison_recovery=False,
            )
        else:
            for damage_type in resistances:
                typed = DamageType(damage_type)
                if typed not in target.state.temporary_damage_resistances:
                    target.state.temporary_damage_resistances.append(typed)
        if spell.share_damage_with_source and target.combatant_id != member.combatant_id:
            target.state.damage_share_source_id = member.combatant_id
            target.state.damage_share_range_ft = spell.share_range_ft
            target.state.damage_share_effect_id = spell.id
        if not spell.concentration and spell.id not in target.state.active_buff_effect_ids:
            target.state.active_buff_effect_ids.append(spell.id)
    apply_spell_modifiers(
        member.state,
        [(target.combatant_id, target.state) for target in targets],
        member.combatant_id, spell, 0, affected_states,
        duration_minutes=effective_duration,
    )
    details = [*temp_hp_details]
    if spell.max_hp_increase:
        details.append(f"+{spell.max_hp_increase} Hit Point maximum")
    if spell.current_hp_increase:
        details.append(f"+{spell.current_hp_increase} current Hit Points")
    if spell.damage_resistances or spell.selectable_resistance_types:
        details.append("resistance")
    if spell.share_damage_with_source:
        details.append(f"shared damage within {spell.share_range_ft} feet")
    details.extend(spell.condition_ids)
    details.extend(_modifier_detail(effect) for effect in spell.modifier_effects)
    if duration_modifier is not None:
        details.append(f"{duration_modifier.name}: {effective_duration} minutes")
    if spell.concentration:
        details.append("Concentration")
    names = ", ".join(target.state.template.name for target in targets)
    single = targets[0] if len(targets) == 1 else None
    return BattleEvent(
        sequence=sequence, round_number=0, event_type="feature",
        actor_id=member.combatant_id, actor_name=member.state.template.name,
        target_id=single.combatant_id if single else None,
        target_name=single.state.template.name if single else None,
        feature_id=duration_modifier.id if duration_modifier is not None else spell.id,
        resource_remaining=duration_remaining if duration_modifier is not None else resource.current_uses,
        concentration_started_effect_id=spell.id if spell.concentration else None,
        animation=spell.animation,
        description=(
            f"Precombat preparation: {member.state.template.name} casts {spell.name} "
            f"{'as the free opening buff' if spell.free_opening_cast else f'with a level {slot_level} slot'} "
            f"on {names} ({'; '.join(details)})."
        ),
    )
