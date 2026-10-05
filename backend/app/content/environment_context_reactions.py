from __future__ import annotations

import logging

from app.domain.environment_contexts import EnvironmentContextReaction

logger = logging.getLogger(__name__)


def sunlight_sensitivity_2014() -> EnvironmentContextReaction:
    """2014 printed Sunlight Sensitivity: attack rolls and sight-based Perception."""
    try:
        return EnvironmentContextReaction(
            source_id="sunlight-sensitivity",
            source_name="Sunlight Sensitivity",
            context_id="sunlight",
            disadvantage_on=["attack_rolls", "sight_based_perception_checks"],
        )
    except Exception:
        logger.exception("Failed to build 2014 Sunlight Sensitivity context reaction.")
        raise
