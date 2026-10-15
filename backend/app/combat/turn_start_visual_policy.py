from __future__ import annotations
import logging
from dataclasses import dataclass

log = logging.getLogger(__name__)

@dataclass(frozen=True)
class VisualTurnStartRule:
    source_id: str
    source_name: str
    range_ft: int
    save_dc: int
    save_ability: str = "constitution"
    immediate_petrification_margin: int | None = None

    def __post_init__(self):
        try:
            if not self.source_id or not self.source_name or self.range_ft <= 0 or not 1 <= self.save_dc <= 40:
                raise ValueError("Invalid visual source parameters")
            if self.save_ability not in ("strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"):
                raise ValueError("Invalid visual saving throw")
            if self.immediate_petrification_margin is not None and self.immediate_petrification_margin <= 0:
                raise ValueError("Invalid immediate failure margin")
        except ValueError:
            log.exception("Invalid visual source configuration")
            raise

@dataclass(frozen=True)
class VisualTurnStartFacts:
    distance_ft: int
    source_active: bool
    target_active: bool
    source_sees_target: bool
    target_sees_source: bool
    target_immune: bool
    target_surprised: bool
    may_avert_eyes: bool

def decide_visual_turn_start(rule: VisualTurnStartRule, facts: VisualTurnStartFacts) -> str:
    try:
        if facts.distance_ft < 0:
            raise ValueError("Invalid visual distance")
        if facts.distance_ft > rule.range_ft or not all((facts.source_active, facts.target_active, facts.source_sees_target, facts.target_sees_source)) or facts.target_immune:
            return "ineligible"
        return "averted" if facts.may_avert_eyes and not facts.target_surprised else "save_required"
    except Exception:
        log.exception("Visual eligibility failed")
        raise

def resolve_visual_save_stage(rule: VisualTurnStartRule, save_total: int, previous_stage: str | None = None) -> str:
    try:
        if not isinstance(save_total, int) or previous_stage not in (None, "restrained"):
            raise ValueError("Invalid save progression")
        if save_total >= rule.save_dc:
            return "clear"
        if previous_stage == "restrained":
            return "petrified"
        margin = rule.immediate_petrification_margin
        return "petrified" if margin is not None and rule.save_dc - save_total >= margin else "restrained"
    except Exception:
        log.exception("Visual progression failed")
        raise
