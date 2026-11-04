"""Universal action-choice policy for removing a source-target attachment."""
from __future__ import annotations

import logging

from app.combat.action_economy import is_available
from app.combat.attachment_removal import remove_attachment_by_action
from app.combat.encounter_targeting import combatant_distance
from app.domain.attachment_receipts import AttachmentChange
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.events import BattleEvent

logger = logging.getLogger(__name__)


def choose_attachment_removal(
    actor: EncounterCombatant, setup: EncounterSetup,
):
    """Find the highest-threat friendly attached target in removal range."""
    try:
        if not is_available(actor.state, "action"):
            return None
        members = {m.combatant_id: m for m in [*setup.heroes, *setup.monsters]}
        choices = []
        for link in setup.attachments:
            source, target = members.get(link.source_id), members.get(link.target_id)
            if not link.action_removable or source is None or target is None:
                continue
            if source.state.is_dead or not source.state.is_alive:
                continue
            if target.state.is_dead or not target.state.is_alive:
                continue
            if target.side != actor.side or source.side == actor.side:
                continue
            # The victim may always reach an attached source; other helpers need range.
            if (actor.combatant_id != link.target_id
                    and combatant_distance(actor, source) > link.action_removal_range_ft):
                continue
            average_loss = link.damage_dice_count * (link.damage_dice_size + 1) / 2
            choices.append((-(average_loss + link.damage_bonus),
                            link.source_id, link.effect_id, link))
        return sorted(choices)[0][3] if choices else None
    except Exception:
        logger.exception("Attachment removal choice failed for %s.", actor.combatant_id)
        raise


def resolve_attachment_removal_action(
    sequence: int, round_number: int, actor: EncounterCombatant,
    setup: EncounterSetup,
) -> BattleEvent | None:
    """Spend the Action and report a generic detach transition for replay."""
    try:
        link = choose_attachment_removal(actor, setup)
        if link is None:
            return None
        if not remove_attachment_by_action(setup, actor, link.source_id, link.effect_id):
            raise ValueError("Selected attachment removal became illegal.")
        target = next(member for member in [*setup.heroes, *setup.monsters]
                      if member.combatant_id == link.target_id)
        return BattleEvent(
            sequence=sequence, round_number=round_number, event_type="feature",
            actor_id=actor.combatant_id, actor_name=actor.state.template.name,
            target_id=target.combatant_id, target_name=target.state.template.name,
            feature_id=link.source_name, animation="feature",
            attachment_changes=[AttachmentChange(
                operation="detach", source_id=link.source_id, target_id=link.target_id,
                effect_id=link.effect_id, source_name=link.source_name,
            )],
            description=(f"{actor.state.template.name} spends an Action to detach "
                         f"{link.source_name} from {target.state.template.name}."),
        )
    except Exception:
        logger.exception("Failed to resolve attachment removal Action for %s.", actor.combatant_id)
        raise
