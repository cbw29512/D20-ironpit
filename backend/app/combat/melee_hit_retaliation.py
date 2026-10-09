from __future__ import annotations

import logging

from app.combat.damage_defenses import apply_damage_defenses
from app.combat.encounter_targeting import combatant_distance
from app.combat.zero_hp import apply_damage
from app.domain.encounters import EncounterCombatant
from app.domain.models import CombatantState, DamageRollComponent, DamageType
from app.domain.timed_self_buffs import MeleeHitRetaliation, TimedSelfBuffAction

logger = logging.getLogger(__name__)


def active_melee_hit_retaliations(
    defender: CombatantState,
) -> list[tuple[TimedSelfBuffAction, MeleeHitRetaliation]]:
    """Return every active source-owned retaliation, in declared effect order."""
    try:
        return [
            (action, action.melee_hit_retaliation)
            for action in defender.template.timed_self_buff_actions
            if action.melee_hit_retaliation is not None
            and (
                action.activation_timing == "passive"
                or any(effect.source_effect_id == action.id for effect in defender.timed_effects)
            )
        ]
    except Exception:
        logger.exception("Failed to read melee-hit retaliation for %s.", defender.template.name)
        raise


def active_melee_hit_retaliation(defender: CombatantState) -> tuple[TimedSelfBuffAction, MeleeHitRetaliation] | None:
    """Legacy single-effect query; the damage path resolves all qualifying effects."""
    sources = active_melee_hit_retaliations(defender)
    return sources[0] if sources else None


def apply_melee_hit_retaliation(
    attacker: EncounterCombatant,
    defender: EncounterCombatant,
    *,
    melee: bool,
    dice,
    affected_states: list[CombatantState] | None = None,
    physical_contact: bool = False,
) -> int:
    """Resolve every source-owned retaliation on a melee hit or proven physical contact."""
    try:
        if (not melee and not physical_contact) or attacker.state.is_dead or not attacker.state.is_alive:
            return 0
        distance = combatant_distance(attacker, defender)
        total = 0
        for action, rule in active_melee_hit_retaliations(defender.state):
            if not melee and not rule.on_contact:
                continue
            if distance > rule.range_ft:
                continue
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
            total += applied
        return total
    except Exception:
        logger.exception("Failed melee-hit retaliation for %s.", defender.combatant_id)
        raise
