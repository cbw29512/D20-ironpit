"""Source-turn attachment ticks, using existing direct-HP-loss/typed-damage engines."""
from __future__ import annotations

import logging

from app.combat.attachments import detach_for_combatant, record_attachment_hp_loss
from app.combat.damage import roll_damage_component
from app.combat.damage_defenses import apply_damage_defenses
from app.combat.dice import roll_dice
from app.combat.hit_point_loss import lose_hit_points
from app.combat.zero_hp import apply_damage
from app.domain.encounters import EncounterSetup, EncounterCombatant
from app.domain.events import BattleEvent
from app.domain.attachment_receipts import AttachmentChange
from app.domain.models import DamageType

logger = logging.getLogger(__name__)


def cleanup_invalid_attachments(setup: EncounterSetup) -> None:
    """Remove the shared relationship when either combatant is no longer alive."""
    try:
        members = {member.combatant_id: member for member in [*setup.heroes, *setup.monsters]}
        links = tuple(setup.attachments)
        for row in tuple(links):
            owner, target = members.get(row.source_id), members.get(row.target_id)
            if any(member is None or member.state.is_dead or not member.state.is_alive
                   for member in (owner, target)):
                links = detach_for_combatant(links, row.source_id if owner is None
                                             or owner.state.is_dead or not owner.state.is_alive
                                             else row.target_id)
        setup.attachments = list(links)
    except Exception:
        logger.exception("Failed to clean up encounter attachment links.")
        raise


def resolve_attachment_turn_start_events(
    sequence: int, round_number: int, owner: EncounterCombatant,
    setup: EncounterSetup, dice,
) -> tuple[list[BattleEvent], int]:
    """Resolve only source-turn-start links; no new attack and no Grappled effect."""
    try:
        cleanup_invalid_attachments(setup)
        if owner.state.is_dead or not owner.state.is_alive or owner.state.current_hp <= 0:
            return [], sequence
        members = {member.combatant_id: member for member in [*setup.heroes, *setup.monsters]}
        affected = [member.state for member in members.values()]
        events: list[BattleEvent] = []
        for row in tuple(setup.attachments):
            if row.source_id != owner.combatant_id or row.damage_timing != "source_turn_start":
                continue
            target = members.get(row.target_id)
            if target is None or target.state.is_dead or not target.state.is_alive:
                continue
            before = target.state.current_hp
            adjusted = []
            if row.periodic_effect_kind == "direct_hp_loss":
                rolled = roll_dice(dice, row.damage_dice_count, row.damage_dice_size)
                lost = lose_hit_points(
                    target.state, max(0, rolled + row.damage_bonus),
                    dice=dice, affected_states=affected,
                )
                effect_text = f"drains {lost} Hit Points (not damage)"
            elif row.periodic_effect_kind == "typed_damage":
                kind = DamageType(row.damage_type)
                component = roll_damage_component(
                    dice, row.source_name, row.damage_dice_count, row.damage_dice_size,
                    row.damage_bonus, kind, False,
                )
                applied, adjusted = apply_damage_defenses(target.state, [component])
                apply_damage(
                    target.state, applied, damage_types={kind}, dice=dice,
                    affected_states=affected, setup=setup, damage_components=adjusted,
                    source_id=owner.combatant_id,
                )
                lost = max(0, before - target.state.current_hp)
                effect_text = f"deals {applied} {kind.value} damage"
            else:
                raise ValueError("Unsupported periodic attachment effect kind.")
            setup.attachments = list(record_attachment_hp_loss(
                tuple(setup.attachments), row.source_id, row.effect_id, lost,
            ))
            detached = not any(
                item.source_id == row.source_id and item.effect_id == row.effect_id
                for item in setup.attachments
            )
            change = [AttachmentChange(
                operation="detach", source_id=row.source_id, target_id=row.target_id,
                effect_id=row.effect_id, source_name=row.source_name,
            )] if detached else []
            events.append(BattleEvent(
                sequence=sequence, round_number=round_number, event_type="feature",
                actor_id=owner.combatant_id, actor_name=owner.state.template.name,
                target_id=target.combatant_id, target_name=target.state.template.name,
                feature_id=row.source_name, damage_components=adjusted,
                attachment_changes=change,
                hp_before=before, hp_after=target.state.current_hp,
                is_dead=target.state.is_dead, animation="feature",
                description=f"{owner.state.template.name}: {row.source_name} {effect_text} at its turn start.",
            ))
            sequence += 1
            if target.state.is_dead or not target.state.is_alive:
                cleanup_invalid_attachments(setup)
        return events, sequence
    except Exception:
        logger.exception("Attachment start-turn resolution failed for %s.", owner.combatant_id)
        raise
