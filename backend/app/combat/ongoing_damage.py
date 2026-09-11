from __future__ import annotations

import logging

from app.combat.damage import aggregate_damage_components, roll_damage_component
from app.combat.damage_defenses import apply_damage_defenses
from app.combat.dice import DiceProvider
from app.combat.zero_hp import apply_damage
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import BattleEvent, DamageType

logger = logging.getLogger(__name__)


def encounter_members(setup: EncounterSetup) -> list[EncounterCombatant]:
    return [*setup.heroes, *setup.monsters]


def resolve_ongoing_damage(
    sequence: int, round_number: int, source: EncounterCombatant, target: EncounterCombatant,
    setup: EncounterSetup, dice: DiceProvider, *, feature_id: str, feature_name: str,
    dice_count: int, dice_size: int, damage_bonus: int, damage_type: DamageType,
    animation: str,
) -> BattleEvent:
    """Resolve non-attack typed damage through the shared defense and zero-HP pipelines."""
    try:
        component = roll_damage_component(
            dice, feature_name, dice_count, dice_size, damage_bonus, damage_type, False,
        )
        total, components = apply_damage_defenses(target.state, [component])
        hp_before = target.state.current_hp
        apply_damage(
            target.state, total, damage_types={damage_type} if total > 0 else set(), dice=dice,
            affected_states=[member.state for member in encounter_members(setup)],
        )
        damage_roll = aggregate_damage_components(components)
        damage_roll.total = total
        return BattleEvent(
            sequence=sequence, round_number=round_number, event_type="feature",
            actor_id=source.combatant_id, actor_name=source.state.template.name,
            target_id=target.combatant_id, target_name=target.state.template.name,
            feature_id=feature_id, damage_roll=damage_roll, damage_components=components,
            hp_before=hp_before, hp_after=target.state.current_hp, animation=animation,
            description=(f"{source.state.template.name}'s {feature_name} deals {total} "
                         f"{damage_type.value} damage to {target.state.template.name}."),
        )
    except Exception as exc:
        logger.exception("Failed ongoing damage %s -> %s.", source.combatant_id, target.combatant_id)
        raise RuntimeError("Ongoing damage could not be resolved.") from exc
