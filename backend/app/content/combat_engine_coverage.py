from __future__ import annotations

import logging
from collections.abc import Iterable, Mapping

from app.content.combat_build_choice_overlays import CombatBuildChoiceOverlay, FIGHTER_COMBAT_BUILD_CHOICES
from app.content.combat_build_variants import get_combat_build_variant

logger = logging.getLogger(__name__)

SUPPORTED = "supported"
BLOCKED = "blocked"
ARENA_OUT_OF_SCOPE = "arena_out_of_scope"
DECLARED_REQUIREMENT_STATUSES = frozenset({SUPPORTED, BLOCKED})


def audit_build_capability_contract(
    overlays: Iterable[CombatBuildChoiceOverlay],
    capability_statuses: Mapping[str, str],
    build_statuses: Mapping[tuple[str, str], str],
) -> list[str]:
    """Return fail-closed capability-contract issues for declared build overlays."""
    issues: list[str] = []
    try:
        for overlay in overlays:
            build_key = (overlay.class_id, overlay.build_id)
            build_label = f"{overlay.class_id}/{overlay.build_id}"
            build_status = build_statuses.get(build_key)
            if build_status not in {"active", "planned"}:
                issues.append(f"{build_label}: missing or invalid build status {build_status!r}.")
                continue

            required = set(overlay.required_capabilities)
            ignored = set(overlay.arena_ignored)
            overlap = sorted(required & ignored)
            if overlap:
                issues.append(f"{build_label}: capabilities cannot be both required and arena-ignored: {overlap}.")

            for capability_id in sorted(required):
                status = capability_statuses.get(capability_id)
                if status not in DECLARED_REQUIREMENT_STATUSES:
                    issues.append(
                        f"{build_label}: required capability {capability_id!r} must be supported or blocked; got {status!r}."
                    )
                    continue
                if build_status == "active" and status != SUPPORTED:
                    issues.append(
                        f"{build_label}: active build requires {capability_id!r}, but matrix status is {status!r}."
                    )

            for capability_id in sorted(ignored):
                status = capability_statuses.get(capability_id)
                if status != ARENA_OUT_OF_SCOPE:
                    issues.append(
                        f"{build_label}: arena-ignored capability {capability_id!r} must be arena_out_of_scope; got {status!r}."
                    )
    except (AttributeError, TypeError) as exc:
        logger.exception("Combat build capability contract audit failed structurally.")
        raise RuntimeError("Combat build capability contract could not be audited.") from exc
    return issues


def audit_current_build_capabilities(capability_statuses: Mapping[str, str]) -> list[str]:
    """Audit every build overlay currently declared by the production content layer."""
    try:
        overlays = tuple(FIGHTER_COMBAT_BUILD_CHOICES.values())
        build_statuses = {
            (overlay.class_id, overlay.build_id): get_combat_build_variant(overlay.class_id, overlay.build_id).status
            for overlay in overlays
        }
        return audit_build_capability_contract(overlays, capability_statuses, build_statuses)
    except (RuntimeError, ValueError) as exc:
        logger.exception("Current combat build capability audit could not be assembled.")
        raise RuntimeError("Current combat build capability audit failed.") from exc
