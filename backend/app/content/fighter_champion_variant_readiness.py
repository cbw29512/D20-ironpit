from __future__ import annotations

from collections.abc import Mapping

from app.content.build_audit import audit_character_build
from app.content.combat_build_choice_overlays import get_combat_build_choice_overlay
from app.content.combatant_capability_requirements import audit_combatant_capability_support
from app.content.fighter_champion_variant_profiles import build_fighter_champion_variant_profile
from app.content.fighter_champion_variant_runtime import compile_fighter_champion_variant


def audit_fighter_champion_variant_readiness(
    build_id: str,
    level: int,
    capability_statuses: Mapping[str, str],
) -> list[str]:
    """Audit a Fighter/Champion snapshot from its sheet, compiled runtime, and shared capability statuses."""
    profile = build_fighter_champion_variant_profile(build_id, level)
    template = compile_fighter_champion_variant(build_id, level)
    overlay = get_combat_build_choice_overlay("fighter", build_id)
    return [
        *audit_character_build(profile, template),
        *audit_combatant_capability_support(
            profile,
            template,
            capability_statuses,
            arena_ignored=frozenset(overlay.arena_ignored),
        ),
    ]


def fighter_champion_variant_family_ready(
    build_id: str,
    capability_statuses: Mapping[str, str],
) -> bool:
    """A named Champion build is active only when every generated level 3-20 snapshot is runnable."""
    return all(
        not audit_fighter_champion_variant_readiness(build_id, level, capability_statuses)
        for level in range(3, 21)
    )
