from __future__ import annotations

from app.combat.action_economy import is_available, spend
from app.combat.saving_throw_rolls import resolve_saving_throw
from app.combat.saving_throws import resolve_save_action
from app.combat.spell_policy import SpellChoice
from app.combat.spell_reflection import reflection_target, spend_spell_reflection
from app.combat.spellcasting import mark_slot_spell_cast
from app.domain.actions import SavingThrowAction
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import BattleEvent


def _resource(state, level: int):
    resource_id = f"spell-slot-{level}"
    return next((item for item in state.resources if item.id == resource_id), None)


def _effect_reach(choice: SpellChoice) -> int:
    spell = choice.action
    if spell.area is None:
        return spell.range_ft + (spell.area_radius_ft or 0)
    area = spell.area
    extent = area.radius_ft or area.length_ft or 0
    return spell.range_ft + extent if area.origin == "point" else extent


def _save_action(choice: SpellChoice) -> SavingThrowAction:
    spell = choice.action
    if choice.slot_level != spell.level:
        raise ValueError("Spell upcasting is not certified; use the spell's printed slot level.")
    return SavingThrowAction(
        id=spell.id, name=spell.name, save_ability=spell.save_ability, dc=spell.dc,
        range_ft=_effect_reach(choice), damage_dice_count=spell.damage_dice_count,
        damage_dice_size=spell.damage_dice_size, damage_bonus=spell.damage_bonus,
        damage_type=spell.damage_type, success_damage=spell.success_damage,
        magical_effect=True, animation=spell.animation,
    )


def resolve_spell(
    sequence: int,
    round_number: int,
    caster: EncounterCombatant,
    setup: EncounterSetup,
    choice: SpellChoice,
    turn_key: str,
    dice,
) -> tuple[list[BattleEvent], int]:
    spell = choice.action
    if spell.action_cost == "reaction":
        raise ValueError("Reaction spells require their own trigger window.")
    if choice.slot_level != spell.level:
        raise ValueError("Spell upcasting is not certified; use the spell's printed slot level.")
    if not is_available(caster.state, spell.action_cost):
        raise ValueError(f"{spell.action_cost} is unavailable for {spell.name}.")

    remaining = None
    if choice.slot_level > 0:
        resource = _resource(caster.state, choice.slot_level)
        if resource is None or resource.current_uses < 1:
            raise ValueError(f"No level {choice.slot_level} spell slot remains.")
        mark_slot_spell_cast(caster.state, turn_key)
        resource.current_uses -= 1
        remaining = resource.current_uses
    spend(caster.state, spell.action_cost)

    placement = choice.placement
    detail = ""
    if placement is not None:
        detail = (
            f" Area covers {len(placement.enemy_ids)} enemies and "
            f"{len(placement.friendly_ids)} allies."
        )
    slot_text = "cantrip" if choice.slot_level == 0 else f"level {choice.slot_level} slot"
    events = [BattleEvent(
        sequence=sequence, round_number=round_number, event_type="feature",
        actor_id=caster.combatant_id, actor_name=caster.state.template.name,
        feature_id=spell.id, resource_remaining=remaining, animation=spell.animation,
        description=f"{caster.state.template.name} casts {spell.name} using a {slot_text}.{detail}",
    )]
    sequence += 1

    members = [*setup.heroes, *setup.monsters]
    by_id = {member.combatant_id: member for member in members}
    affected_states = [member.state for member in members]
    save_action = _save_action(choice)
    reflectable = spell.area is None and spell.area_radius_ft is None and len(choice.target_ids) == 1
    shared_damage_rolls: list[int] | None = None
    for target_id in choice.target_ids:
        target = by_id[target_id]
        precomputed = None
        reflected_from = None
        if reflectable and target.state.template.spell_reflection_reaction is not None:
            precomputed = resolve_saving_throw(
                target.state, save_action.save_ability, save_action.dc, dice, magical_effect=True,
            )
            if precomputed[1]:
                reflected = reflection_target(target, caster, setup)
                if reflected is not None:
                    spend_spell_reflection(target); reflected_from = target; target = reflected; precomputed = None
        event = resolve_save_action(
            sequence, round_number, caster, target, save_action,
            0 if placement is not None or reflected_from is not None else abs(caster.position_ft - target.position_ft),
            dice, spend_action=False, shared_damage_rolls=shared_damage_rolls,
            affected_states=affected_states, setup=setup, precomputed_save=precomputed,
        )
        if reflected_from is not None:
            event.description = f"{reflected_from.state.template.name} uses Spell Reflection; {spell.name} targets {target.state.template.name} instead. {event.description}"
        events.append(event)
        if shared_damage_rolls is None and event.damage_components:
            shared_damage_rolls = list(event.damage_components[0].rolls)
        sequence += 1
    return events, sequence
