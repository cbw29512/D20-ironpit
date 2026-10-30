from __future__ import annotations

import logging

from app.combat.bloodied import is_bloodied
from app.combat.dice import DiceProvider
from app.combat.encounter_targeting import combatant_distance
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.events import BattleEvent
from app.domain.event_support import DiceRoll

logger = logging.getLogger(__name__)


def resolve_start_turn_berserk(
    sequence: int,
    round_number: int,
    member: EncounterCombatant,
    dice: DiceProvider,
) -> tuple[BattleEvent | None, int]:
    """Resolve a Bloodied Berserk start-turn roll and fight-local activation."""
    try:
        rule = member.state.template.bloodied_berserk_rule
        if rule is None:
            return None, sequence
        if not is_bloodied(member.state):
            member.state.active_berserk_rule_id = None
            return None, sequence

        roll = dice.roll(rule.die_size)
        activated_now = (
            roll >= rule.trigger_minimum
            and member.state.active_berserk_rule_id != rule.id
        )
        if roll >= rule.trigger_minimum:
            member.state.active_berserk_rule_id = rule.id

        event = BattleEvent(
            sequence=sequence,
            round_number=round_number,
            event_type="feature",
            actor_id=member.combatant_id,
            actor_name=member.state.template.name,
            resource_roll=DiceRoll(
                notation=f"1d{rule.die_size}",
                rolls=[roll],
                selected_roll=roll,
                total=roll,
            ),
            feature_id=rule.id,
            animation="berserk",
            description=(
                f"{member.state.template.name} rolls {roll} for {rule.name}"
                + (" and goes berserk." if activated_now else ".")
            ),
        )
        return event, sequence + 1
    except Exception as exc:
        logger.exception("Bloodied Berserk start-turn resolution failed for %s.", member.combatant_id)
        raise RuntimeError("Bloodied Berserk start-turn resolution failed.") from exc


def berserk_target_order(
    attacker: EncounterCombatant,
    setup: EncounterSetup,
) -> list[EncounterCombatant] | None:
    """Return nearest visible living creatures when an active Berserk rule overrides normal sides."""
    try:
        rule = attacker.state.template.bloodied_berserk_rule
        if (
            rule is None
            or attacker.state.active_berserk_rule_id != rule.id
            or not is_bloodied(attacker.state)
        ):
            return None
        members = [
            member
            for member in [*setup.heroes, *setup.monsters]
            if member.combatant_id != attacker.combatant_id
            and member.state.is_alive
            and not member.state.is_dead
            and (
                member.state.swallowed is None
                or not member.state.swallowed.total_cover_from_outside
            )
        ]
        return sorted(
            members,
            key=lambda target: (
                combatant_distance(attacker, target),
                target.combatant_id,
            ),
        )
    except Exception as exc:
        logger.exception("Bloodied Berserk targeting failed for %s.", attacker.combatant_id)
        raise RuntimeError("Bloodied Berserk targeting failed.") from exc
