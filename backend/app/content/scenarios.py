from __future__ import annotations

import logging

from app.domain.models import (
    ActorVisibilityState,
    CombatantTemplate,
    EncounterSetup,
    PrecombatActorPlan,
)

logger = logging.getLogger(__name__)


def build_rogue_ambush_setup(
    rogue: CombatantTemplate,
    target: CombatantTemplate,
) -> tuple[dict[str, ActorVisibilityState], EncounterSetup]:
    try:
        visibility = {
            rogue.id: ActorVisibilityState(
                heavily_obscured=True,
                enemy_line_of_sight=False,
            )
        }
        setup = EncounterSetup(
            plans_by_actor={
                rogue.id: PrecombatActorPlan(
                    attempt_hide=True,
                    ambush_target_ids={target.id},
                )
            }
        )
        return visibility, setup
    except Exception as exc:
        logger.exception("Failed to build Rogue ambush scenario.")
        raise RuntimeError("Rogue ambush scenario could not be created.") from exc
