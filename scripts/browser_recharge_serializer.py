from __future__ import annotations

import logging
from typing import Any

from app.domain.models import CombatantTemplate

logger = logging.getLogger(__name__)


def recharge_rows(template: CombatantTemplate) -> list[dict[str, Any]]:
    """Serialize immutable Recharge rules for the browser combat template.

    The browser runtime owns only temporary resource state. These rows describe
    when an expended template resource may recharge; they never mutate the
    source CombatantTemplate.
    """
    try:
        resource_ids = {resource.id for resource in template.resources}
        rows: list[dict[str, Any]] = []
        for rule in template.recharge_rules:
            if rule.resource_id not in resource_ids:
                raise ValueError(
                    f"Recharge rule {rule.resource_id!r} on {template.id!r} "
                    "does not reference a declared resource."
                )
            rows.append(
                {
                    "resourceId": rule.resource_id,
                    "minimumRoll": rule.minimum_roll,
                    "dieSize": rule.die_size,
                }
            )
        return rows
    except Exception:
        logger.exception("Failed to serialize Recharge rules for %s.", template.id)
        raise
