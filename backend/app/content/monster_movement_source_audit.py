from __future__ import annotations

import logging

from app.content.monster_movement_choice_source import selected_movement_choice
from app.content.monster_movement_form_policy import form_only_movement_is_arena_neutral
from app.content.movement_modes import movement_source_issues, parse_movement_profile
from app.domain.models import CombatantTemplate

logger = logging.getLogger(__name__)
_MODE_FIELDS = {
    "walk": "walk_ft",
    "fly": "fly_ft",
    "climb": "climb_ft",
    "swim": "swim_ft",
    "burrow": "burrow_ft",
}


def movement_mode_issues(
    template: CombatantTemplate,
    row: dict[str, object],
) -> list[str]:
    """Audit runtime movement against unconditional source modes and a declared GM choice."""
    try:
        expected = parse_movement_profile(row["speed"])
        selected_modes, choice_issues = selected_movement_choice(
            row["speed"],
            template.movement_modes,
        )
        issues = [
            f"movement-{mode}-mismatch"
            for mode, field in _MODE_FIELDS.items()
            if mode not in selected_modes
            and getattr(template.movement_modes, field) != getattr(expected, field)
        ]
        if template.movement_modes.hover != expected.hover:
            issues.append("movement-hover-mismatch")

        source_issues = movement_source_issues(row["speed"])
        if form_only_movement_is_arena_neutral(row):
            source_issues = [
                issue for issue in source_issues
                if issue != "movement-form-source-unmodeled"
            ]
        if not choice_issues:
            source_issues = [
                issue
                for issue in source_issues
                if issue != "movement-choice-source-unmodeled"
            ]
        issues.extend(source_issues)
        issues.extend(choice_issues)
        return issues
    except Exception as exc:
        logger.exception("Failed to audit movement modes for %s.", template.id)
        raise RuntimeError("Monster movement modes could not be audited.") from exc
