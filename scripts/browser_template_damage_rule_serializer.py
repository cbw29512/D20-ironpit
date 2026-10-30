from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


def damage_taken_disadvantage_rows(template: Any) -> list[dict[str, Any]]:
    try:
        return [
            {
                "id": rule.id,
                "name": rule.name,
                "damageType": rule.damage_type.value,
                "attackRollDisadvantage": rule.attack_roll_disadvantage,
                "abilityCheckDisadvantage": rule.ability_check_disadvantage,
            }
            for rule in template.damage_taken_disadvantage_rules
        ]
    except Exception:
        logger.exception(
            "Failed damage-taken disadvantage serialization for %s.",
            getattr(template, "id", "<unknown>"),
        )
        raise
