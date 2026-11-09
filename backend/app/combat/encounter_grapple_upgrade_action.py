"""Action-economy promotion of a previously held target to a linked grapple effect."""
from __future__ import annotations

import logging
from app.combat.action_economy import is_available, spend
from app.combat.grapple import apply_grapple
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import BattleEvent
from app.domain.size import size_at_most

logger = logging.getLogger(__name__)


def resolve_grapple_upgrade_action(
    sequence: int, round_number: int, owner: EncounterCombatant, setup: EncounterSetup,
) -> tuple[list[BattleEvent], int] | None:
    """Use the printed separate Action only against an already owned grapple."""
    try:
        if (not is_available(owner.state, "action")
                or owner.state.template.swallow_actions):
            return None
        members = [*setup.heroes, *setup.monsters]
        for rule in owner.state.template.multi_hit_grapple_effects:
            if not rule.standalone_action:
                continue
            active = sum(
                any(g.source_id == owner.combatant_id
                    and g.linked_effect_id == rule.effect_id
                    for g in member.state.grapple_sources)
                for member in members
            )
            if active >= rule.max_active_grapples:
                continue
            for target in members:
                if target.side == owner.side or not target.state.is_alive:
                    continue
                if target.state.is_dead or target.state.current_hp <= 0:
                    continue
                if not size_at_most(target.state.template.size, rule.max_target_size):
                    continue
                held = next((g for g in target.state.grapple_sources
                             if g.source_id == owner.combatant_id
                             and g.linked_effect_id != rule.effect_id), None)
                if held is None or abs(owner.position_ft - target.position_ft) > rule.range_ft:
                    continue
                conditions = apply_grapple(
                    target.state, owner.combatant_id, held.escape_dc, held.range_ft,
                    restrains=rule.restrains, blinds=rule.blinds,
                    prevents_breathing=rule.prevents_breathing,
                    linked_effect_id=rule.effect_id,
                )
                if not conditions:
                    continue
                spend(owner.state, "action")
                if rule.blinds and "blinded" in target.state.active_effect_ids:
                    conditions.append("blinded")
                event = BattleEvent(
                    sequence=sequence, round_number=round_number, event_type="feature",
                    actor_id=owner.combatant_id, actor_name=owner.state.template.name,
                    target_id=target.combatant_id, target_name=target.state.template.name,
                    feature_id=rule.source_name,
                    applied_condition_ids=list(dict.fromkeys(conditions)),
                    animation="feature",
                    description=(
                        f"{owner.state.template.name} uses {rule.source_name} on held "
                        f"{target.state.template.name}; "
                        f"Grappled (escape DC {held.escape_dc})"
                        + (", Blinded" if rule.blinds else "")
                        + (", Restrained" if rule.restrains else "")
                        + (", unable to breathe" if rule.prevents_breathing else "")
                        + "."
                    ),
                )
                return [event], sequence + 1
        return None
    except Exception:
        logger.exception("Linked grapple upgrade Action failed for %s.", owner.combatant_id)
        raise
