from __future__ import annotations
import logging
from dataclasses import dataclass
from app.combat.staged_save_debuff import resolve_staged_save
from app.domain.visual_turn_start import VisualTurnStartRule

log = logging.getLogger(__name__)

@dataclass(frozen=True)
class VisualTurnStartFacts:
    distance_ft: int
    source_active: bool
    target_active: bool
    source_sees_target: bool
    target_sees_source: bool
    target_immune: bool
    target_surprised: bool

def decide_visual_turn_start(rule: VisualTurnStartRule, facts: VisualTurnStartFacts) -> str:
    try:
        if type(facts.distance_ft) is not int or facts.distance_ft < 0:
            raise ValueError("Invalid visual distance")
        if any(type(getattr(facts, key)) is not bool for key in ("source_active", "target_active", "source_sees_target", "target_sees_source", "target_immune", "target_surprised")):
            raise ValueError("Visual eligibility flags must be booleans")
        if facts.distance_ft > rule.range_ft or not all((facts.source_active, facts.target_active, facts.source_sees_target, facts.target_sees_source)) or facts.target_immune:
            return "ineligible"
        return "averted" if not facts.target_surprised else "save_required"
    except Exception:
        log.exception("Visual eligibility failed")
        raise

def resolve_visual_save_stage(rule: VisualTurnStartRule, save_total: int, previous_stage: str | None = None) -> str:
    try:
        if type(save_total) is not int or previous_stage not in (None, rule.initial_debuff):
            raise ValueError("Invalid save progression")
        outcome = resolve_staged_save(
            save_total=save_total, dc=rule.save_dc,
            initial_effect=rule.initial_debuff, terminal_effect=rule.terminal_debuff,
            previous_effect=previous_stage,
            immediate_failure_margin=rule.immediate_petrification_margin,
        )
        return outcome if outcome is not None else "clear"
    except Exception:
        log.exception("Visual progression failed")
        raise
