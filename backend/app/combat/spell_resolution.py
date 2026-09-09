from __future__ import annotations

from app.combat.action_economy import is_available, spend
from app.combat.save_targets import resolve_save_targets
from app.combat.spell_policy import SpellChoice
from app.combat.spellcasting import mark_slot_spell_cast
from app.domain.actions import SavingThrowAction
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import BattleEvent


def _resource(state, level: int):
    resource_id = f"spell-slot-{level}"
    return next((item for item in state.resources if item.id == resource_id), None)


def _save_action(choice: SpellChoice) -> SavingThrowAction:
    spell = choice.action
    if choice.slot_level != spell.level:
        raise ValueError("Spell upcasting is not certified; use the spell's printed slot level.")
    return SavingThrowAction(
        id=spell.id,
        name=spell.name,
        save_ability=spell.save_ability,
        dc=spell.dc,
        range_ft=spell.range_ft,
        area=spell.area,
        damage_dice_count=spell.damage_dice_count,
        damage_dice_size=spell.damage_dice_size,
        damage_bonus=spell.damage_bonus,
        damage_type=spell.damage_type,
        success_damage=spell.success_damage,
        animation=spell.animation,
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
    detail = f" Area covers {len(placement.target_ids)} enemies." if placement is not None else ""
    slot_text = "cantrip" if choice.slot_level == 0 else f"level {choice.slot_level} slot"
    events = [BattleEvent(
        sequence=sequence,
        round_number=round_number,
        event_type="feature",
        actor_id=caster.combatant_id,
        actor_name=caster.state.template.name,
        feature_id=spell.id,
        resource_remaining=remaining,
        animation=spell.animation,
        description=f"{caster.state.template.name} casts {spell.name} using a {slot_text}.{detail}",
    )]
    sequence += 1

    save_events, sequence = resolve_save_targets(
        sequence,
        round_number,
        caster,
        setup,
        _save_action(choice),
        choice.target_ids,
        dice,
        skip_range_check=placement is not None,
    )
    events.extend(save_events)
    return events, sequence
