from __future__ import annotations

import re

_MOVEMENT_MODES = ("walk", "fly", "climb", "swim", "burrow")
_STANDARD_ARENA_MODES = frozenset({"walk", "fly"})


def parse_movement_modes(source_speed: object) -> dict[str, int]:
    """Parse SRD Speed text without collapsing distinct movement modes."""
    text = str(source_speed).strip().lower()
    if not text:
        raise ValueError("SRD Speed text is empty.")
    modes: dict[str, int] = {}
    for index, part in enumerate(piece.strip() for piece in text.split(",")):
        match = re.search(r"(\d+)\s*ft", part)
        if not match:
            raise ValueError(f"Could not parse movement speed component: {part!r}")
        speed = int(match.group(1))
        named = next((mode for mode in _MOVEMENT_MODES[1:] if re.search(rf"\b{mode}\b", part)), None)
        mode = named or ("walk" if index == 0 else None)
        if mode is None:
            raise ValueError(f"Unknown movement mode in SRD Speed component: {part!r}")
        modes[mode] = speed
    if "walk" not in modes:
        raise ValueError(f"SRD Speed text lacks a base walking speed: {source_speed!r}")
    return modes


def standard_arena_closing_speed(source_speed: object) -> int:
    """Fastest printed mode legal in the open, flat standard Iron Pit.

    Walking and horizontal flight are available. Climb, swim, and burrow need
    terrain the standard arena intentionally does not provide.
    """
    modes = parse_movement_modes(source_speed)
    legal = [speed for mode, speed in modes.items() if mode in _STANDARD_ARENA_MODES]
    if not legal:
        raise ValueError(f"No standard-arena movement mode available: {source_speed!r}")
    return max(legal)
