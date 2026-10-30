from __future__ import annotations

import logging
import re
from app.content.monster_bonus_support_binding import runtime_bonus_support
from app.content.monster_bonus_action_source_names import parse_bonus_action_names, source_bonus_action_names
from app.content.monster_timed_self_buff_binding import runtime_timed_self_buff
from app.domain.models import CombatantTemplate

logger = logging.getLogger(__name__)
# These actions only Hide/Disengage or alter pre-contact movement under the
# documented flat, no-Hide, no-kiting, initiative-opener arena abstraction.
_ARENA_NEUTRAL_BONUS_ACTIONS = frozenset({
    "Aquatic Charge",
    "Bubble Dash",
    "Charge",
    "Cunning Action",
    "Ethereal Jaunt",
    "Ignited Illumination",
    "Leap",
    "Nimble Escape",
    "Shadow Stealth",
    "Shape-Shift",
    "Swoop",
    "Teleport",
})


def arena_neutral_bonus_action(name: str) -> bool:
    try:
        return _base_name(name) in _ARENA_NEUTRAL_BONUS_ACTIONS
    except Exception as exc:
        logger.exception("Failed to classify arena-neutral Bonus Action %r.", name)
        raise RuntimeError("Bonus Action arena-neutral policy could not be evaluated.") from exc


def _base_name(name: str) -> str:
    return re.sub(r"\s*\([^)]*\)$", "", name).strip()


def _slug(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", _base_name(name).lower()).strip("-")


def _runtime_bonus_save(template: CombatantTemplate, name: str) -> bool:
    try:
        base = _base_name(name)
        return any(
            action.name == base and action.action_cost == "bonus_action"
            for action in template.saving_throw_actions
        )
    except Exception as exc:
        logger.exception("Failed to inspect Bonus Action save binding for %s.", template.id)
        raise RuntimeError("Bonus Action save binding could not be evaluated.") from exc


def _runtime_triggered_bonus_attack(template: CombatantTemplate, name: str) -> bool:
    try:
        base = _base_name(name)
        return any(feature.name == base for feature in template.triggered_bonus_attacks)
    except Exception as exc:
        logger.exception("Failed to inspect triggered Bonus Action binding for %s.", template.id)
        raise RuntimeError("Triggered Bonus Action binding could not be evaluated.") from exc


def _runtime_bonus_swallow(template: CombatantTemplate, name: str) -> bool:
    try:
        base = _base_name(name)
        return any(
            action.name == base and action.action_cost == "bonus_action"
            for action in template.swallow_actions
        )
    except Exception as exc:
        logger.exception("Failed to inspect Bonus Action Swallow binding for %s.", template.id)
        raise RuntimeError("Bonus Action Swallow binding could not be evaluated.") from exc


def _source_no_hide_movement_bonus(name: str, source_bonus_actions: object) -> bool:
    """Arena-neutral when the printed result is only no-OA movement plus optional Hide."""
    try:
        base = re.escape(_base_name(name))
        text = str(source_bonus_actions or "")
        pattern = re.compile(
            rf"{base}(?:\s*\([^)]*\))?\.\s+The [^.]+ moves up to its Speed "
            r"without provoking Opportunity Attacks\.\s+At the end of this movement, "
            r"the [^.]+ can take the Hide action\.",
            re.IGNORECASE,
        )
        return pattern.search(text) is not None
    except Exception as exc:
        logger.exception("Failed to classify no-Hide movement Bonus Action %r.", name)
        raise RuntimeError("No-Hide movement Bonus Action policy could not be evaluated.") from exc


def _source_planar_neutral_bonus(name: str, source_bonus_actions: object) -> bool:
    try:
        text = str(source_bonus_actions or "")
        plane = "Ethereal " + "Plane"
        return _base_name(name) in text and plane in text and "Material Plane" in text
    except Exception as exc:
        logger.exception("Failed to classify source-planar Bonus Action %r.", name)
        raise RuntimeError("Planar Bonus Action policy could not be evaluated.") from exc


def bonus_action_issues(template: CombatantTemplate, row: dict[str, object]) -> list[str]:
    """Fail closed when a printed outcome-changing bonus action lacks runtime semantics."""
    try:
        expected = parse_bonus_action_names(row.get("bonusActions", ""))
        issues: list[str] = []
        if template.source_bonus_action_names != expected:
            issues.append("source-bonus-action-fingerprint-mismatch")
        for name in expected:
            if (
                arena_neutral_bonus_action(name)
                or _runtime_bonus_save(template, name)
                or _runtime_bonus_swallow(template, name)
                or runtime_bonus_support(template, _base_name(name))
                or runtime_timed_self_buff(template, _base_name(name), "bonus_action")
                or _runtime_triggered_bonus_attack(template, name)
                or _source_no_hide_movement_bonus(name, row.get("bonusActions", ""))
            ):
                continue
            issues.append(f"uncertified-bonus-action:{_slug(name)}")
        return issues
    except Exception as exc:
        logger.exception("Failed to audit Bonus Actions for %s.", template.id)
        raise RuntimeError("Monster Bonus Action audit could not be evaluated.") from exc
def complete_monster_bonus_action_fingerprints(templates: list[CombatantTemplate]) -> list[CombatantTemplate]:
    try:
        return [
            template.model_copy(update={"source_bonus_action_names": source_bonus_action_names(template.name)})
            if template.kind == "monster" else template
            for template in templates
        ]
    except Exception:
        logger.exception("Failed to derive canonical monster bonus-action fingerprints from SRD source.")
        raise