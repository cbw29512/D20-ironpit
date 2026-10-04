from __future__ import annotations

import logging

from app.combat.concentration import start_concentration
from app.combat.condition_removal import remove_condition
from app.combat.exile import EXILED_EFFECT_ID
from app.combat.forced_movement import push_straight_away
from app.combat.modifier_stack import add_modifier
from app.combat.saving_throw_rolls import resolve_saving_throw
from app.combat.spell_modifiers import build_spell_modifier
from app.combat.timed_conditions import apply_timed_condition
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import CombatantState
from app.domain.post_hit_spell import PostHitSpellOption
from app.domain.saving_throw_context import SavingThrowContext
from app.domain.spells import SpellModifierEffect

logger = logging.getLogger(__name__)


def _paid_option(attacker: CombatantState, turn_key: str) -> PostHitSpellOption | None:
    option_id = attacker.feature_last_turn_keys.get("paid-post-hit-spell")
    if not option_id or attacker.feature_last_turn_keys.get(option_id) != turn_key:
        return None
    return next(
        (item for item in attacker.template.progression_features.post_hit_spell_options if item.id == option_id),
        None,
    )


def resolve_paid_post_hit_spell_riders(
    attacker: EncounterCombatant,
    defender: EncounterCombatant,
    setup: EncounterSetup,
    dice,
    *,
    round_number: int,
    turn_key: str,
    affected_states: list[CombatantState] | None,
) -> list[str]:
    """Apply printed extra-smite riders after the triggering attack's damage resolves."""
    try:
        option = _paid_option(attacker.state, turn_key)
        if option is None:
            return []
        applied: list[str] = []
        members = [member.state for member in [*setup.heroes, *setup.monsters]]
        states = affected_states or members
        if option.concentration:
            start_concentration(
                attacker.state,
                attacker.combatant_id,
                option.id,
                round_number,
                states,
                expires_round=round_number + max(1, option.duration_rounds),
            )
        if option.attacks_against_advantage or option.suppress_invisible:
            effects = []
            if option.attacks_against_advantage:
                effects.append(SpellModifierEffect(kind="attacks-against-advantage"))
            if option.suppress_invisible:
                effects.append(SpellModifierEffect(kind="condition-immunity", condition_id="invisible"))
                if "invisible" in defender.state.active_effect_ids:
                    remove_condition(defender, "invisible")
            for index, effect in enumerate(effects):
                add_modifier(defender.state, build_spell_modifier(
                    attacker.combatant_id,
                    defender.combatant_id,
                    option.id,
                    effect,
                    index,
                    option.name,
                    concentration_required=option.concentration,
                    round_number=round_number,
                ))
        if option.save_ability and option.save_dc and option.failed_condition_id:
            _, succeeded = resolve_saving_throw(
                defender.state,
                option.save_ability,
                option.save_dc,
                dice,
                SavingThrowContext(condition_id=option.failed_condition_id, effect_tags=frozenset({"spell"})),
                round_number=round_number,
                encounter_roller=defender,
                setup=setup,
            )
            if not succeeded:
                if (
                    option.failed_condition_expiry_timing
                    or option.repeat_save_ability
                    or option.duration_rounds
                ):
                    apply_timed_condition(
                        defender.state,
                        option.failed_condition_id,
                        attacker.combatant_id,
                        source_effect_id=option.id,
                        source_template=attacker.state.template,
                        source_is_magical=True,
                        applied_round=round_number,
                        expires_round=(
                            round_number + max(1, option.duration_rounds)
                            if option.duration_rounds
                            else round_number + 1
                        ),
                        expires_at_start_of_source_turn=False,
                        expiry_timing=option.failed_condition_expiry_timing,
                        repeat_save_ability=option.repeat_save_ability,
                        repeat_save_dc=option.repeat_save_dc,
                        repeat_save_timing=option.repeat_save_timing,
                        affected_states=states,
                        use_default_poison_recovery=False,
                    )
                elif option.failed_condition_id not in defender.state.active_effect_ids:
                    defender.state.active_effect_ids.append(option.failed_condition_id)
                applied.append(option.failed_condition_id)
                if option.failed_push_ft:
                    push_straight_away(
                        defender, attacker, setup, option.failed_push_ft, round_number=round_number,
                    )
        if option.start_of_turn_dice_count:
            slot = int(attacker.state.feature_last_turn_keys.get("paid-post-hit-slot") or option.level)
            count = option.start_of_turn_dice_count + option.start_of_turn_dice_per_slot_above * max(
                0, slot - option.level
            )
            apply_timed_condition(
                defender.state,
                option.id,
                attacker.combatant_id,
                source_effect_id=option.id,
                source_template=attacker.state.template,
                source_is_magical=True,
                applied_round=round_number,
                expires_round=round_number + max(1, option.duration_rounds or 10),
                expires_at_start_of_source_turn=False,
                expiry_timing="source_turn_end",
                affected_states=states,
                use_default_poison_recovery=False,
            )
            from app.domain.combatants import DamageType
            for effect in defender.state.timed_effects:
                if effect.effect_id == option.id and effect.source_id == attacker.combatant_id:
                    effect.start_of_turn_dice_count = count
                    effect.start_of_turn_dice_size = option.start_of_turn_dice_size
                    if option.start_of_turn_damage_type:
                        effect.start_of_turn_damage_type = DamageType(option.start_of_turn_damage_type)
                    effect.start_of_turn_save_ability = option.start_of_turn_save_ability
                    effect.start_of_turn_save_dc = option.start_of_turn_save_dc
                    effect.start_of_turn_save_ends = option.start_of_turn_save_ends
            applied.append(option.id)
        if option.exile_if_hp_at_or_below and 0 < defender.state.current_hp <= option.exile_if_hp_at_or_below:
            apply_timed_condition(
                defender.state,
                EXILED_EFFECT_ID,
                attacker.combatant_id,
                source_effect_id=option.id,
                source_template=attacker.state.template,
                source_is_magical=True,
                suppress_action=True,
                suppress_bonus_action=True,
                suppress_reactions=True,
                suppress_movement=True,
                applied_round=round_number,
                expires_round=round_number + max(1, option.duration_rounds),
                expiry_timing="source_turn_end",
                affected_states=states,
                use_default_poison_recovery=False,
                removed_from_battlefield=True,
            )
            applied.append(EXILED_EFFECT_ID)
        return applied
    except Exception:
        logger.exception("Failed extra-smite riders for %s.", attacker.combatant_id)
        raise
