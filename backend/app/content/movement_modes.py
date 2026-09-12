from __future__ import annotations

import logging
import re
from functools import lru_cache

from app.content.monster_catalog import load_monster_rows
from app.domain.models import CombatantTemplate
from app.domain.movement import MovementModes

logger = logging.getLogger(__name__)
_MOVEMENT_MODES = ("walk", "fly", "climb", "swim", "burrow")
_STANDARD_ARENA_MODES = frozenset({"walk", "fly"})
_MODE_FIELDS = {
    "walk": "walk_ft",
    "fly": "fly_ft",
    "climb": "climb_ft",
    "swim": "swim_ft",
    "burrow": "burrow_ft",
}
_FORM_ONLY = re.compile(r"\([^)]*\bform\s+only\b[^)]*\)", re.I)
_GM_CHOICE = re.compile(
    r"\b(?:climb|fly|swim|burrow)\s+or\s+(?:climb|fly|swim|burrow)\b.*\(\s*gm[’']s choice\s*\)",
    re.I,
)


def _deferred_component_kind(part: str) -> str | None:
    if _GM_CHOICE.search(part):
        return "choice"
    if _FORM_ONLY.search(part):
        return "form"
    if "(" in part and ")" not in part:
        return "malformed-parenthetical"
    return None


def movement_source_issues(source_speed: object) -> list[str]:
    """Identify printed movement alternatives that the flat runtime profile must not invent."""
    issues: set[str] = set()
    for part in (piece.strip().lower() for piece in str(source_speed).split(",")):
        kind = _deferred_component_kind(part)
        if kind == "choice":
            issues.add("movement-choice-source-unmodeled")
        elif kind == "form":
            issues.add("movement-form-source-unmodeled")
        elif kind == "malformed-parenthetical":
            issues.add("movement-parenthetical-source-malformed")
    return sorted(issues)


def parse_movement_modes(source_speed: object) -> dict[str, int]:
    """Parse unconditional SRD Speed text without activating source alternatives."""
    text = str(source_speed).strip().lower()
    if not text:
        raise ValueError("SRD Speed text is empty.")
    modes: dict[str, int] = {}
    for index, part in enumerate(piece.strip() for piece in text.split(",")):
        if _deferred_component_kind(part) is not None:
            continue
        match = re.search(r"(\d+)\s*ft", part)
        if not match:
            raise ValueError(f"Could not parse movement speed component: {part!r}")
        speed = int(match.group(1))
        named = next((mode for mode in _MOVEMENT_MODES[1:] if re.search(rf"\b{mode}\b", part)), None)
        mode = named or ("walk" if index == 0 else None)
        if mode is None:
            raise ValueError(f"Unknown movement mode in SRD Speed component: {part!r}")
        if mode in modes:
            raise ValueError(f"Duplicate {mode} movement mode in SRD Speed: {source_speed!r}")
        modes[mode] = speed
    if "walk" not in modes:
        raise ValueError(f"SRD Speed text lacks a base walking speed: {source_speed!r}")
    return modes


def parse_movement_profile(source_speed: object) -> MovementModes:
    """Convert unconditional printed SRD Speed text into the runtime movement fingerprint."""
    modes = parse_movement_modes(source_speed)
    hover = bool(re.search(r"\bhover\b", str(source_speed), re.IGNORECASE))
    if hover and "fly" not in modes:
        raise ValueError(f"Hover is printed without a Fly speed: {source_speed!r}")
    return MovementModes(
        walk_ft=modes["walk"],
        fly_ft=modes.get("fly", 0),
        climb_ft=modes.get("climb", 0),
        swim_ft=modes.get("swim", 0),
        burrow_ft=modes.get("burrow", 0),
        hover=hover,
    )


def standard_arena_closing_speed(source_speed: object) -> int:
    """Fastest unconditional printed mode legal in the open, flat standard Iron Pit."""
    modes = parse_movement_modes(source_speed)
    legal = [speed for mode, speed in modes.items() if mode in _STANDARD_ARENA_MODES]
    if not legal:
        raise ValueError(f"No standard-arena movement mode available: {source_speed!r}")
    return max(legal)


def movement_mode_issues(template: CombatantTemplate, row: dict[str, object]) -> list[str]:
    """Return blockers for movement drift and unresolved printed movement alternatives."""
    expected = parse_movement_profile(row["speed"])
    issues = [
        f"movement-{mode}-mismatch"
        for mode, field in _MODE_FIELDS.items()
        if getattr(template.movement_modes, field) != getattr(expected, field)
    ]
    if template.movement_modes.hover != expected.hover:
        issues.append("movement-hover-mismatch")
    issues.extend(movement_source_issues(row["speed"]))
    return issues


@lru_cache(maxsize=1)
def _rows_by_name() -> dict[str, dict[str, object]]:
    return {str(row["name"]): row for row in load_monster_rows()}


def source_movement_modes(name: str) -> MovementModes:
    row = _rows_by_name().get(name)
    if row is None:
        raise ValueError(f"No SRD 5.2.1 source row for monster {name!r}.")
    profile = parse_movement_profile(row["speed"])
    incorporeal = bool(re.search(r"\bIncorporeal Movement\b", str(row.get("traits", "")), re.IGNORECASE))
    return profile.model_copy(update={
        "pass_through_creatures_as_difficult_terrain": incorporeal,
    })


def with_source_movement_modes(template: CombatantTemplate) -> CombatantTemplate:
    if template.kind != "monster":
        return template
    return template.model_copy(update={"movement_modes": source_movement_modes(template.name)})


def complete_monster_movement_modes(templates: list[CombatantTemplate]) -> list[CombatantTemplate]:
    try:
        return [with_source_movement_modes(template) for template in templates]
    except Exception:
        logger.exception("Failed to derive canonical monster movement modes from SRD source.")
        raise
