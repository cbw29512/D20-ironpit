from __future__ import annotations

import logging

from app.combat.damage_defenses import apply_damage_defenses
from app.combat.friendly_recovery_aura_windows import (
    resolve_source_turn_recovery_heals,
    resolve_zero_hp_ally_recovery,
)
from app.combat.post_hit_save_condition_lifecycle import start_of_turn_save_condition_damage
from app.combat.start_of_turn_timed_burn import start_of_turn_timed_burns
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
        resolve_zero_hp_ally_recovery(member, setup)
        resolve_source_turn_recovery_heals(member, setup, dice)
        affected = [item.state for item in [*setup.heroes, *setup.monsters]]
        packets = [
            *start_of_turn_save_condition_damage(member, setup, dice),
            *start_of_turn_timed_burns(member, setup, dice),
        ]
        for name, total, damage_type in packets:
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
                animation="feature",
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
