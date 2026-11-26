"""Action and movement-based removal of any source-target attachment link."""
from __future__ import annotations

import logging

from app.combat.action_economy import claim_voluntary_activity, is_available, spend
from app.combat.ability_checks import ability_check_roll_mode, resolve_ability_check_outcome
from app.combat.ability_check_escape import ability_check_bonus
from app.combat.exhaustion import ability_check_disadvantage_sources, d20_modifier
from app.combat.rolls import roll_d20
from app.combat.attachments import detach_link, sync_attachment_controls
from app.combat.encounter_targeting import combatant_distance
from app.domain.attachment_receipts import AttachmentChange
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.events import BattleEvent

logger = logging.getLogger(__name__)


def attempt_attachment_removal_by_action(
    setup: EncounterSetup, actor: EncounterCombatant,
    source_id: str, effect_id: str, dice=None, round_number: int = 1,
):
    """Spend the Action and resolve an optional source-printed ability check."""
    row = next((link for link in setup.attachments
                if (link.source_id, link.effect_id) == (source_id, effect_id)), None)
    if row is None or not row.action_removable or not is_available(actor.state, "action"):
        return False, False, None
    source = next((member for member in [*setup.heroes, *setup.monsters]
                   if member.combatant_id == source_id), None)
    if source is None:
        raise ValueError("Cannot remove link for an absent source.")
    if (actor.combatant_id != row.target_id
            and combatant_distance(actor, source) > row.action_removal_range_ft):
        return False, False, None
    check = None
    success = True
    if row.action_removal_check_ability is not None:
        if dice is None or row.action_removal_check_dc is None:
            raise ValueError("Checked attachment removal requires dice and a printed DC.")
        ability = row.action_removal_check_ability
        disadvantage = ability_check_disadvantage_sources(actor.state, ability)
        mode = ability_check_roll_mode(
            actor.state, ability=ability, disadvantage_sources=disadvantage,
            member=actor, setup=setup,
        )
        check = roll_d20(
            dice, ability_check_bonus(actor.state, ability) + d20_modifier(actor.state), mode,
        )
        check, success = resolve_ability_check_outcome(
            actor.state, ability, check, row.action_removal_check_dc,
            dice=dice, round_number=round_number, encounter_roller=actor, setup=setup,
        )
    spend(actor.state, "action")
    if success:
        setup.attachments = list(detach_link(tuple(setup.attachments), source_id, effect_id))
        sync_attachment_controls(setup)
    return True, success, check


def remove_attachment_by_action(
    setup: EncounterSetup, actor: EncounterCombatant,
    source_id: str, effect_id: str,
) -> bool:
    """A creature near the source may spend one ordinary Action to remove its link."""
    try:
        attempted, success, _ = attempt_attachment_removal_by_action(
            setup, actor, source_id, effect_id,
        )
        return attempted and success
    except Exception:
        logger.exception("Action detachment failed for %s / %s.", source_id, effect_id)
        raise


def detach_attachment_with_movement(
    setup: EncounterSetup, actor: EncounterCombatant, effect_id: str,
) -> bool:
    """Source can spend its printed movement cost; does not grant free movement."""
    try:
        row = next((link for link in setup.attachments
                    if (link.source_id, link.effect_id) == (actor.combatant_id, effect_id)), None)
        if row is None:
            return False
        cost = row.source_detach_movement_ft
        if cost <= 0 or actor.state.is_dead or not actor.state.is_alive:
            return False
        if actor.state.movement_remaining_ft < cost:
            return False
        from app.combat.action_economy import voluntary_activity_available
        if not voluntary_activity_available(actor.state, "movement"):
            return False
        claim_voluntary_activity(actor.state, "movement")
        actor.state.movement_remaining_ft -= cost
        setup.attachments = list(detach_link(tuple(setup.attachments), actor.combatant_id, effect_id))
        sync_attachment_controls(setup)
        logger.info("%s spends %s ft movement to detach %s.",
                    actor.combatant_id, cost, row.source_name)
        return True
    except Exception:
        logger.exception("Source movement detachment failed for %s.", actor.combatant_id)
        raise


def resolve_blocked_source_movement_detachment(
    sequence: int,
    round_number: int,
    actor: EncounterCombatant,
    setup: EncounterSetup,
) -> BattleEvent | None:
    """Use a legal printed movement detach before an attack-locked source gives up its turn."""
    try:
        candidates = sorted(
            (
                row
                for row in setup.attachments
                if row.source_id == actor.combatant_id
                and row.blocks_source_attacks
                and row.source_detach_movement_ft > 0
            ),
            key=lambda row: (row.source_detach_movement_ft, row.effect_id, row.target_id),
        )
        for row in candidates:
            movement_before = actor.state.movement_remaining_ft
            if not detach_attachment_with_movement(setup, actor, row.effect_id):
                continue
            spent = movement_before - actor.state.movement_remaining_ft
            return BattleEvent(
                sequence=sequence,
                round_number=round_number,
                event_type="feature",
                actor_id=actor.combatant_id,
                actor_name=actor.state.template.name,
                target_id=row.target_id,
                feature_id=row.source_name,
                movement_ft=spent,
                animation="movement",
                attachment_changes=[AttachmentChange(
                    operation="detach",
                    source_id=row.source_id,
                    target_id=row.target_id,
                    effect_id=row.effect_id,
                    source_name=row.source_name,
                )],
                description=(
                    f"{actor.state.template.name} spends {spent} feet of movement "
                    f"to detach {row.source_name}."
                ),
            )
        return None
    except Exception:
        logger.exception("Blocked-source movement detachment failed for %s.", actor.combatant_id)
        raise
