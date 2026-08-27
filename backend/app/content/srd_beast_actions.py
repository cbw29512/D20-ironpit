from __future__ import annotations

import logging

from app.domain.models import (
    Ability,
    ConditionExpiry,
    ConditionType,
    SaveAction,
    SaveFailureEffect,
)

logger = logging.getLogger(__name__)


def build_lion_roar_action() -> SaveAction:
    try:
        return SaveAction(
            id="lion-roar",
            name="Roar",
            save_ability=Ability.WISDOM,
            dc=11,
            range_ft=15,
            failure_effects=[SaveFailureEffect(
                condition=ConditionType.FRIGHTENED,
                expires_on=ConditionExpiry.SOURCE_TURN_START,
            )],
            animation="roar",
        )
    except Exception as exc:
        logger.exception("Failed to build Lion Roar action.")
        raise RuntimeError("Lion Roar action could not be created.") from exc
