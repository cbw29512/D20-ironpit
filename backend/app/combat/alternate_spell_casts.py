from __future__ import annotations

import logging

from app.domain.alternate_spell_casts import AlternateSpellCastGrant
from app.domain.models import CombatantState

logger = logging.getLogger(__name__)


def available_alternate_casts(
    state: CombatantState,
    spell_id: str,
) -> tuple[AlternateSpellCastGrant, ...]:
    try:
        grants = [
            grant
            for grant in state.template.progression_features.alternate_spell_cast_grants
            if grant.spell_id == spell_id
        ]
        available = []
        for grant in grants:
            if grant.resource_id is None:
                available.append(grant)
                continue
            resource = next(
                (item for item in state.resources if item.id == grant.resource_id),
                None,
            )
            if resource is not None and resource.current_uses >= grant.resource_cost:
                available.append(grant)
        return tuple(sorted(available, key=lambda item: (-item.priority, item.cast_level, item.source_id)))
    except Exception:
        logger.exception(
            "Failed to evaluate alternate spell casts for %s and %s.",
            state.template.id,
            spell_id,
        )
        raise


def spend_alternate_cast(
    state: CombatantState,
    grant: AlternateSpellCastGrant,
) -> int | None:
    try:
        if grant.resource_id is None:
            return None
        resource = next(
            (item for item in state.resources if item.id == grant.resource_id),
            None,
        )
        if resource is None or resource.current_uses < grant.resource_cost:
            raise ValueError(f"Insufficient {grant.resource_id} for {grant.source_name}.")
        resource.current_uses -= grant.resource_cost
        return resource.current_uses
    except ValueError:
        raise
    except Exception as exc:
        logger.exception(
            "Failed to spend alternate spell cast %s for %s.",
            grant.source_id,
            state.template.id,
        )
        raise RuntimeError("Alternate spell cast resource could not be spent.") from exc
