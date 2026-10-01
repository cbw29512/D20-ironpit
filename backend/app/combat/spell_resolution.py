from __future__ import annotations

import logging

from app.combat.action_economy import is_available, spend
from app.combat.alternate_spell_casts import spend_alternate_cast
from app.combat.concentration import start_concentration
from app.combat.defensive_modifier_rules import remove_owner_attack_ending_modifiers
from app.combat.spell_cast_effects import apply_spell_cast_timed_resistance
from app.combat.spell_choice import SpellChoice
from app.combat.spell_policy import spell_at_slot
from app.combat.spell_range_modifiers import spend_spell_range_modifier
from app.combat.spell_save_effect_resolution import resolve_spell_save_effect
from app.combat.spell_damage_maximizers import resolve_maximizer_after_cast
from app.combat.spellcasting import mark_spell_cast, spell_cast_available
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import BattleEvent

logger = logging.getLogger(__name__)


def _resource(state, level: int):
    try:
        resource_id = f"spell-slot-{level}"
        return next((item for item in state.resources if item.id == resource_id), None)
    except Exception as exc:
        logger.exception("Failed to load spell-slot resource level %s.", level)
        raise RuntimeError("Spell-slot resource could not be loaded.") from exc


def resolve_spell(
    sequence: int,
    round_number: int,
    caster: EncounterCombatant,
    setup: EncounterSetup,
    choice: SpellChoice,
    turn_key: str,
    dice,
) -> tuple[list[BattleEvent], int]:
    try:
        spell = choice.action
        spell_at_slot(spell, choice.slot_level)
        if spell.action_cost == "reaction":
            raise ValueError("Reaction spells require their own trigger window.")
        if not is_available(caster.state, spell.action_cost):
            raise ValueError(f"{spell.action_cost} is unavailable for {spell.name}.")
        expends_spell_slot = choice.alternate_cast is None and choice.slot_level > 0
        if not spell_cast_available(
            caster.state, turn_key, spell.level, spell.action_cost,
            expends_spell_slot=expends_spell_slot,
        ):
            raise ValueError(f"{spell.name} is not legal under the active edition's per-turn casting rule.")

        remaining = None
        if choice.alternate_cast is not None:
            if choice.alternate_cast.cast_level != choice.slot_level:
                raise ValueError("Alternate spell cast level does not match the selected cast level.")
            remaining = spend_alternate_cast(caster.state, choice.alternate_cast)
        elif choice.slot_level > 0:
            resource = _resource(caster.state, choice.slot_level)
            if resource is None or resource.current_uses < 1:
                raise ValueError(f"No level {choice.slot_level} spell slot remains.")
            resource.current_uses -= 1
            remaining = resource.current_uses

        mark_spell_cast(
            caster.state, turn_key, spell.level, spell.action_cost,
            expends_spell_slot=expends_spell_slot,
        )
        spend(caster.state, spell.action_cost)
        range_remaining = spend_spell_range_modifier(caster.state, choice.range_modifier)
        remove_owner_attack_ending_modifiers(caster.state)
        apply_spell_cast_timed_resistance(caster, spell, round_number)

        members = [*setup.heroes, *setup.monsters]
        if spell.concentration:
            duration_rounds = (spell.duration_minutes or 0) * 10
            start_concentration(
                caster.state,
                caster.combatant_id,
                spell.id,
                round_number,
                [member.state for member in members],
                expires_round=round_number + duration_rounds,
                slot_level=choice.slot_level if choice.slot_level > 0 else None,
            )

        placement = choice.placement
        detail = ""
        if placement is not None:
            protected_count = len(getattr(placement, "protected_friendly_ids", ()))
            detail = (
                f" Area covers {len(placement.enemy_ids)} enemies, "
                f"{len(placement.friendly_ids)} unprotected allies, and "
                f"{protected_count} protected allies."
            )
        slot_text = (
            choice.alternate_cast.source_name
            if choice.alternate_cast is not None
            else ("cantrip" if choice.slot_level == 0 else f"level {choice.slot_level} slot")
        )
        events: list[BattleEvent] = []
        if choice.range_modifier is not None:
            events.append(BattleEvent(
                sequence=sequence,
                round_number=round_number,
                event_type="feature",
                actor_id=caster.combatant_id,
                actor_name=caster.state.template.name,
                feature_id=choice.range_modifier.id,
                resource_remaining=range_remaining,
                animation="spell-range",
                description=(
                    f"{caster.state.template.name} uses {choice.range_modifier.name} "
                    f"to extend {spell.name}'s range."
                ),
            ))
            sequence += 1
        events.append(BattleEvent(
            sequence=sequence,
            round_number=round_number,
            event_type="feature",
            actor_id=caster.combatant_id,
            actor_name=caster.state.template.name,
            feature_id=spell.id,
            resource_remaining=remaining,
            animation=spell.animation,
            description=f"{caster.state.template.name} casts {spell.name} using a {slot_text}.{detail}",
        ))
        sequence += 1

        effect_events, sequence = resolve_spell_save_effect(
            sequence,
            round_number,
            caster,
            setup,
            choice,
            turn_key,
            dice,
        )
        events.extend(effect_events)
        if choice.damage_maximizer is not None:
            follow_up, sequence = resolve_maximizer_after_cast(
                sequence,
                round_number,
                caster,
                setup,
                choice.damage_maximizer,
                choice.slot_level,
                dice,
            )
            events.extend(follow_up)
        return events, sequence
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Save-based spell resolution failed for %s.", caster.combatant_id)
        raise RuntimeError("Save-based spell could not be resolved.") from exc
