"""Source-scoped visual aversion in mutable fight state."""
from __future__ import annotations
import logging
from dataclasses import dataclass
from typing import Iterable

log = logging.getLogger(__name__)

@dataclass(frozen=True)
class VisualAversionWindow:
    observer_id: str
    source_combatant_id: str
    expires_on_observer_turn_start: int

def _validate(observer_id: str, source_id: str, turns_started: int) -> None:
    try:
        if not isinstance(observer_id, str) or not observer_id.strip():
            raise ValueError("Invalid visual observer ID")
        if not isinstance(source_id, str) or not source_id.strip():
            raise ValueError("Invalid visual source ID")
        if type(turns_started) is not int or turns_started < 0:
            raise ValueError("Invalid observer turn counter")
    except (TypeError, ValueError):
        log.exception("Invalid source-scoped visual aversion")
        raise

def _windows(windows: Iterable[VisualAversionWindow]) -> tuple[VisualAversionWindow, ...]:
    try:
        result = tuple(windows)
        for item in result:
            if not isinstance(item, VisualAversionWindow):
                raise ValueError("Invalid visual aversion state")
            _validate(item.observer_id, item.source_combatant_id, item.expires_on_observer_turn_start)
        return result
    except Exception:
        log.exception("Invalid visual aversion state")
        raise

def record_visual_aversion(windows: Iterable[VisualAversionWindow], observer_id: str,
                          source_combatant_id: str, observer_turns_started: int) -> tuple[VisualAversionWindow, ...]:
    try:
        _validate(observer_id, source_combatant_id, observer_turns_started)
        retained = tuple(w for w in _windows(windows)
                         if not (w.observer_id == observer_id and w.source_combatant_id == source_combatant_id)
                         and not (w.observer_id == observer_id
                                  and w.expires_on_observer_turn_start <= observer_turns_started))
        return retained + (VisualAversionWindow(observer_id, source_combatant_id, observer_turns_started + 1),)
    except Exception:
        log.exception("Failed to record visual aversion")
        raise

def visual_aversion_active(windows: Iterable[VisualAversionWindow], observer_id: str,
                          source_combatant_id: str, observer_turns_started: int) -> bool:
    try:
        _validate(observer_id, source_combatant_id, observer_turns_started)
        return any(w.observer_id == observer_id and w.source_combatant_id == source_combatant_id
                   and observer_turns_started < w.expires_on_observer_turn_start for w in _windows(windows))
    except Exception:
        log.exception("Failed to inspect visual aversion")
        raise

def visual_source_perception(windows: Iterable[VisualAversionWindow], observer_id: str,
                             source_combatant_id: str, observer_turns_started: int,
                             *, visual_sight: bool, nonvisual_perception: bool) -> tuple[bool, bool]:
    try:
        if type(visual_sight) is not bool or type(nonvisual_perception) is not bool:
            raise ValueError("Perception facts must be booleans")
        visual = visual_sight and not visual_aversion_active(
            windows, observer_id, source_combatant_id, observer_turns_started)
        return visual, visual or nonvisual_perception
    except Exception:
        log.exception("Failed source-scoped visual perception")
        raise
