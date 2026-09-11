from __future__ import annotations

import re

from app.domain.combatants import RechargeRule, ResourceDefinition


def source_limited_resource(resource_id: str, name: str, limit: str | None) -> ResourceDefinition | None:
    """Compile Recharge or N/Day markers into the shared resource model."""
    if not limit:
        return None
    recharge = re.fullmatch(r"Recharge\s+(\d)(?:\s*[-–]\s*(\d))?", limit, re.I)
    if recharge:
        return ResourceDefinition(
            id=resource_id,
            name=name,
            max_uses=1,
            recharge=RechargeRule(minimum_roll=int(recharge.group(1))),
        )
    per_day = re.fullmatch(r"(\d+)\s*/\s*Day", limit, re.I)
    if per_day:
        return ResourceDefinition(id=resource_id, name=name, max_uses=int(per_day.group(1)))
    return None
