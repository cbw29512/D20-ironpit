"""Shared source-owned target eligibility for attacks and saving-throw actions."""
from __future__ import annotations

import logging

from app.combat.condition_immunity import condition_is_immune
from app.combat.condition_rules import has_condition, is_incapacitated
from app.domain.models import CombatantState
from app.domain.targeting import TargetQualification

logger = logging.getLogger(__name__)


def target_qualifies(
    source_id: str | None,
    target_state: CombatantState,
    qualification: TargetQualification | None,
    *,
    setup=None,
) -> bool:
    """Return whether at least one declared target predicate is currently true."""
    try:
        if qualification is None:
            return True
        allowed = set(qualification.any_of)
        if "source_grappled" in allowed and source_id and any(
            grapple.source_id == source_id for grapple in target_state.grapple_sources
        ):
            return True
        if "incapacitated" in allowed and is_incapacitated(target_state):
            return True
        if "restrained" in allowed and has_condition(target_state, "restrained", setup=setup):
            return True
        if "willing" in allowed and source_id and source_id in target_state.willing_attack_source_ids:
            return True
        if "source_charmed" in allowed and source_id and has_condition(
            target_state, "charmed", setup=setup,
        ):
            for effect in target_state.timed_effects:
                if (
                    effect.effect_id == "charmed"
                    and effect.source_id == source_id
                    and not condition_is_immune(
                        target_state,
                        "charmed",
                        source_is_magical=effect.source_is_magical,
                        setup=setup,
                    )
                ):
                    return True
        return False
    except Exception as exc:
        logger.exception("Failed target qualification for source %s.", source_id)
        raise RuntimeError("Target qualification could not be evaluated.") from exc
