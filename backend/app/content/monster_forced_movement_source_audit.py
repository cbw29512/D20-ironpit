from __future__ import annotations

from collections import Counter
from typing import Any

from app.content.monster_forced_movement_rider import forced_movement_specs


def _fingerprint(movement: Any, max_size: Any) -> tuple[str, int, str, str | None]:
    size = getattr(max_size, "value", max_size)
    return (
        movement.direction,
        movement.max_distance_ft,
        movement.distance_mode,
        str(size) if size is not None else None,
    )


def _runtime_specs(template: Any) -> Counter[tuple[str, int, str, str | None]]:
    specs: list[tuple[str, int, str, str | None]] = []
    for attack in [template.weapon_attack, *template.alternate_weapon_attacks]:
        control = attack.control_effect
        if control is not None and control.forced_movement is not None:
            specs.append(_fingerprint(control.forced_movement, control.max_target_size))
    for action in template.saving_throw_actions:
        control = action.failure_control
        if control is not None and control.forced_movement is not None:
            specs.append(_fingerprint(control.forced_movement, control.max_target_size))
    return Counter(specs)


def forced_movement_issues(template: Any, actions: str) -> list[str]:
    """Require runtime push/pull fingerprints to match every compiled canonical source clause."""
    try:
        source = Counter(_fingerprint(movement, size) for movement, size in forced_movement_specs(actions))
        runtime = _runtime_specs(template)
        return [] if source == runtime else ["forced-movement-source-mismatch"]
    except (TypeError, ValueError) as exc:
        raise ValueError(f"forced movement source audit failed for {template.id}") from exc
