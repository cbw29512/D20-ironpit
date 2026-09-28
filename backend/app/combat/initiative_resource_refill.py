from __future__ import annotations

import logging

from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.events import BattleEvent
from app.domain.initiative_resources import InitiativeResourceRefillGrant
from app.domain.runtime import ResourceState

logger = logging.getLogger(__name__)


def _resource_by_id(
    member: EncounterCombatant,
    resource_id: str,
    source_name: str,
) -> ResourceState:
    try:
        resource = next(
            (item for item in member.state.resources if item.id == resource_id),
            None,
        )
        if resource is None:
            raise ValueError(
                f"{source_name} references missing resource {resource_id}."
            )
        return resource
    except ValueError:
        logger.exception(
            "Initiative resource refill references an invalid resource for %s.",
            member.combatant_id,
        )
        raise
    except Exception as exc:
        logger.exception(
            "Initiative resource lookup failed for %s.",
            member.combatant_id,
        )
        raise RuntimeError("Initiative resource could not be resolved.") from exc


def resolve_initiative_resource_refills(
    sequence: int,
    setup: EncounterSetup,
) -> tuple[list[BattleEvent], int]:
    """Apply source-declared finite-resource restoration after initiative is rolled."""
    try:
        events: list[BattleEvent] = []
        for member in [*setup.heroes, *setup.monsters]:
            for grant in member.state.template.initiative_resource_refill_grants:
                resource = _resource_by_id(member, grant.resource_id, grant.source_name)
                usage = (
                    _resource_by_id(member, grant.usage_resource_id, grant.source_name)
                    if grant.usage_resource_id is not None else None
                )
                if resource.current_uses > grant.when_at_or_below:
                    continue
                if usage is not None and usage.current_uses < grant.usage_resource_cost:
                    continue
                before = resource.current_uses
                after = (
                    resource.max_uses
                    if grant.restore_to_max
                    else min(resource.max_uses, before + grant.restore_amount)
                )
                if after <= before:
                    continue
                if usage is not None:
                    usage.current_uses -= grant.usage_resource_cost
                resource.current_uses = after
                regained = after - before
                events.append(BattleEvent(
                    sequence=sequence,
                    round_number=0,
                    event_type="feature",
                    actor_id=member.combatant_id,
                    actor_name=member.state.template.name,
                    feature_id=grant.source_id,
                    resource_remaining=after,
                    animation="initiative",
                    description=(
                        f"{member.state.template.name} regains {regained} "
                        f"{resource.name} from {grant.source_name}."
                    ),
                ))
                sequence += 1
        return events, sequence
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Initiative resource refill resolution failed.")
        raise RuntimeError("Initiative resource refills could not be resolved.") from exc
