from __future__ import annotations

import logging

from app.combat.damage_defenses import apply_damage_defenses
from app.combat.post_hit_save_condition_lifecycle import start_of_turn_save_condition_damage
from app.combat.zero_hp import apply_damage
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.events import BattleEvent
from app.domain.models import DamageRollComponent, DamageType

logger = logging.getLogger(__name__)


def resolve_start_of_turn_save_condition_damage_events(
    sequence: int,
    round_number: int,
    member: EncounterCombatant,
    setup: EncounterSetup,
    dice,
) -> tuple[list[BattleEvent], int]:
    """Apply printed start-of-turn save-condition damage and emit one event per packet."""
    try:
        events: list[BattleEvent] = []
        affected = [item.state for item in [*setup.heroes, *setup.monsters]]
        for name, total, damage_type in start_of_turn_save_condition_damage(member, setup, dice):
            component = DamageRollComponent(
                source=name,
                notation=str(total),
                rolls=[],
                modifier=0,
                damage_type=DamageType(damage_type),
                total=total,
            )
            applied, adjusted = apply_damage_defenses(member.state, [component])
            hp_before = member.state.current_hp
            apply_damage(
                member.state, applied, critical=False,
                damage_types={component.damage_type}, dice=dice,
                affected_states=affected, setup=setup,
            )
            events.append(BattleEvent(
                sequence=sequence,
                round_number=round_number,
                event_type="feature",
                actor_id=member.combatant_id,
                actor_name=member.state.template.name,
                target_id=member.combatant_id,
                target_name=member.state.template.name,
                feature_id=name,
                hp_before=hp_before,
                hp_after=member.state.current_hp,
                description=(
                    f"{name} deals {applied} {damage_type} damage to "
                    f"{member.state.template.name} at the start of the turn."
                ),
            ))
            sequence += 1
            _ = adjusted
        return events, sequence
    except Exception:
        logger.exception("Start-of-turn save-condition damage events failed for %s.", member.combatant_id)
        raise
