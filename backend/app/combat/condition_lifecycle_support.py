from __future__ import annotations

from app.combat.source_effect_immunity import grant_source_effect_immunity
from app.domain.actions import ConditionTiming


def condition_name(effect_id: str) -> str:
    return effect_id.replace("_", " ").title()


def repeat_save_due(effect, round_number: int, timing: ConditionTiming) -> bool:
    if effect.repeat_save_timing != timing:
        return False
    return not (
        effect.effect_id == "poisoned"
        and effect.applied_round is not None
        and round_number <= effect.applied_round
    )


def expiry_due(effect, round_number: int, timing: ConditionTiming) -> bool:
    if effect.expiry_timing != timing:
        return False
    return effect.expires_round is None or round_number >= effect.expires_round


def grant_end_immunity(target, effect) -> None:
    if not effect.source_effect_immunity_on_end or effect.source_effect_id is None:
        return
    grant_source_effect_immunity(
        target.state,
        effect.source_id,
        effect.source_effect_id,
    )
