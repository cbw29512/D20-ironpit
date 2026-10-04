from __future__ import annotations

import logging

from app.combat.damage_defenses import apply_damage_defenses
from app.combat.encounter_targeting import combatant_distance
from app.combat.zero_hp import apply_damage
from app.domain.encounters import EncounterCombatant
from app.domain.models import CombatantState, DamageRollComponent, DamageType
from app.domain.timed_self_buffs import MeleeHitRetaliation, TimedSelfBuffAction

logger = logging.getLogger(__name__)


def active_melee_hit_retaliation(defender: CombatantState) -> tuple[TimedSelfBuffAction, MeleeHitRetaliation] | None:
    try:
        for action in defender.template.timed_self_buff_actions:
            if action.melee_hit_retaliation is None:
                continue
            if any(effect.source_effect_id == action.id for effect in defender.timed_effects):
                return action, action.melee_hit_retaliation
        return None
    except Exception:
        logger.exception("Failed to read melee-hit retaliation for %s.", defender.template.name)
        raise


def apply_melee_hit_retaliation(
    attacker: EncounterCombatant,
    defender: EncounterCombatant,
    *,
    melee: bool,
    dice,
    affected_states: list[CombatantState] | None = None,
) -> int:
    """Deal printed retaliation damage when a melee attack roll hits inside range."""
    try:
        if not melee or attacker.state.is_dead or not attacker.state.is_alive:
            return 0
        bound = active_melee_hit_retaliation(defender.state)
        if bound is None:
            return 0
        action, rule = bound
        if combatant_distance(attacker, defender) > rule.range_ft:
            return 0
        rolls = [dice.roll(rule.dice_size) for _ in range(rule.dice_count)]
        raw = DamageRollComponent(
            source=action.id,
            notation=f"{rule.dice_count}d{rule.dice_size}",
            rolls=rolls,
            modifier=0,
            damage_type=rule.damage_type,
            total=sum(rolls),
        )
        applied, _ = apply_damage_defenses(attacker.state, [raw])
        if applied:
            apply_damage(
                attacker.state,
                applied,
                damage_types={DamageType(rule.damage_type)},
                dice=dice,
                affected_states=affected_states,
            )
        return applied
    except Exception:
        logger.exception("Failed melee-hit retaliation for %s.", defender.combatant_id)
        raise
