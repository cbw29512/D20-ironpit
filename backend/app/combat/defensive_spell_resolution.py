from __future__ import annotations

from collections.abc import Iterable

from app.combat.spell_modifiers import apply_spell_modifiers
from app.combat.temporary_hp import grant_temporary_hit_points
from app.domain.encounters import EncounterCombatant
from app.domain.models import BattleEvent, DamageType
from app.domain.runtime import CombatantState
from app.domain.spells import DefensiveSpellAction, SpellModifierEffect


def _modifier_detail(effect: SpellModifierEffect) -> str:
    if effect.kind == "armor-class":
        return f"{effect.flat_bonus:+d} AC"
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
) -> BattleEvent:
    if slot_level != spell.level:
        raise ValueError("Spell upcasting is not certified; use the spell's printed slot level.")
    if resource.current_uses < 1:
        raise ValueError(f"No level {slot_level} spell slot remains for {spell.name}.")
    if not targets:
        raise ValueError(f"{spell.name} has no legal precombat targets.")
    if member.state.opening_buff_spell_id is not None:
        raise ValueError(f"{member.state.template.name} already committed its one opening buff this battle.")
    if spell.concentration and member.state.concentration is not None:
        raise ValueError(f"{member.state.template.name} is already concentrating and will not replace the active buff automatically.")
    if any(
        spell.id in target.state.active_buff_effect_ids
        or any(modifier.source_effect_id == spell.id for modifier in target.state.active_modifiers)
        for target in targets
    ):
        raise ValueError(f"{spell.name} is already active on a selected target.")
    member.state.opening_buff_spell_id = spell.id
    resource.current_uses -= 1
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
        for damage_type in spell.damage_resistances:
            typed = DamageType(damage_type)
            if typed not in target.state.temporary_damage_resistances:
                target.state.temporary_damage_resistances.append(typed)
        if not spell.concentration and spell.id not in target.state.active_buff_effect_ids:
            target.state.active_buff_effect_ids.append(spell.id)
    apply_spell_modifiers(
        member.state,
        [(target.combatant_id, target.state) for target in targets],
        member.combatant_id, spell, 0, affected_states,
    )
    details = [*temp_hp_details]
    if spell.max_hp_increase:
        details.append(f"+{spell.max_hp_increase} Hit Point maximum")
    if spell.current_hp_increase:
        details.append(f"+{spell.current_hp_increase} current Hit Points")
    if spell.damage_resistances:
        details.append("resistance to " + ", ".join(spell.damage_resistances))
    details.extend(_modifier_detail(effect) for effect in spell.modifier_effects)
    if spell.concentration:
        details.append("Concentration")
    names = ", ".join(target.state.template.name for target in targets)
    single = targets[0] if len(targets) == 1 else None
    return BattleEvent(
        sequence=sequence, round_number=0, event_type="feature",
        actor_id=member.combatant_id, actor_name=member.state.template.name,
        target_id=single.combatant_id if single else None,
        target_name=single.state.template.name if single else None,
        feature_id=spell.id, resource_remaining=resource.current_uses,
        concentration_started_effect_id=spell.id if spell.concentration else None,
        animation=spell.animation,
        description=(
            f"Precombat preparation: {member.state.template.name} casts {spell.name} with a level {slot_level} slot "
            f"on {names} ({'; '.join(details)})."
        ),
    )
