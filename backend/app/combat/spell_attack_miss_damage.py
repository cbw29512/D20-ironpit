from __future__ import annotations

import logging

from app.combat.damage_defenses import apply_damage_defenses
from app.combat.modifier_stack import add_modifier
from app.combat.spell_attack_helpers import roll_spell_attack_damage
from app.combat.spell_attack_hit_riders import apply_spell_attack_hit_riders
from app.combat.spell_modifiers import build_spell_modifier
from app.combat.timed_conditions import apply_timed_condition
from app.combat.zero_hp import apply_damage
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.spells import SpellAttackAction

logger = logging.getLogger(__name__)


def apply_spell_attack_damage_outcome(
    caster: EncounterCombatant,
    target: EncounterCombatant,
    spell: SpellAttackAction,
    setup: EncounterSetup,
    *,
    hit: bool,
    critical: bool,
    round_number: int,
    turn_key: str,
    dice,
    slot_level: int | None = None,
):
    """Apply hit damage and riders, or printed miss-half cantrip damage with no extra effect."""
    try:
        miss_half = (not hit) and spell.miss_damage == "half"
        if not hit and not miss_half:
            return None, [], []
        damage_roll, rolled = roll_spell_attack_damage(
            spell,
            critical if hit else False,
            dice,
            attacker=caster.state if hit else None,
            target_event_id=target.combatant_id if hit else None,
            slot_level=slot_level,
        )
        if miss_half:
            rolled = [item.model_copy(update={"total": item.total // 2}) for item in rolled]
        applied_total, damage_components = apply_damage_defenses(target.state, rolled)
        damage_roll.total = applied_total
        affected_states = [entry.state for entry in [*setup.heroes, *setup.monsters]]
        apply_damage(
            target.state,
            applied_total,
            critical=critical,
            damage_types={part.damage_type for part in damage_components if part.applied_total},
            dice=dice,
            affected_states=affected_states,
        )
        applied_conditions: list[str] = []
        if hit and target.state.is_alive and not target.state.is_dead:
            for index, effect in enumerate(spell.on_hit_modifier_effects):
                add_modifier(target.state, build_spell_modifier(
                    caster.combatant_id, target.combatant_id, spell.id, effect, index,
                    spell.name, round_number=round_number,
                ))
            for effect in spell.on_hit_timed_effects:
                applied = apply_timed_condition(
                    target.state, effect.effect_id, caster.combatant_id,
                    source_effect_id=spell.id, source_template=caster.state.template,
                    source_is_magical=effect.source_is_magical,
                    suppress_action=effect.suppress_action,
                    suppress_bonus_action=effect.suppress_bonus_action,
                    suppress_reactions=effect.suppress_reactions,
                    suppress_movement=effect.suppress_movement,
                    next_attack_disadvantage=effect.next_attack_disadvantage,
                    applied_round=round_number,
                    expires_round=round_number + effect.duration_rounds,
                    expiry_timing=effect.expiry_timing,
                    affected_states=affected_states,
                    use_default_poison_recovery=False,
                )
                if applied is not None:
                    applied_conditions.append(applied)
            apply_spell_attack_hit_riders(
                caster, target, spell, setup, hit=True,
                round_number=round_number, turn_key=turn_key, dice=dice,
            )
        return damage_roll, damage_components, applied_conditions
    except Exception:
        logger.exception("Failed to apply spell-attack damage for %s.", spell.id)
        raise
