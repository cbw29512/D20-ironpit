from __future__ import annotations

import logging

from app.domain.movement import MovementModes
from app.domain.runtime import CombatantState

logger = logging.getLogger(__name__)
_MODE_FIELDS = {
    "walk": "walk_ft",
    "fly": "fly_ft",
    "climb": "climb_ft",
    "swim": "swim_ft",
    "burrow": "burrow_ft",
}


def default_horizontal_movement_mode(
    modes: MovementModes | None,
    exempt_modes: list[str] | tuple[str, ...] | None = None,
) -> str:
    """Keep fly as fly when a bound fly OA exemption makes that the production mode."""
    try:
        if (
            modes is not None
            and int(modes.fly_ft or 0) > 0
            and "fly" in (exempt_modes or ())
        ):
            return "fly"
        return "walk"
    except Exception:
        logger.exception("Failed to choose the default horizontal movement mode.")
        raise RuntimeError("Default horizontal movement mode could not be resolved.") from None


def ensure_active_movement_mode(state: CombatantState) -> str:
    try:
        if not state.active_movement_mode:
            state.active_movement_mode = default_horizontal_movement_mode(
                state.template.movement_modes,
                state.template.opportunity_attack_exempt_movement_modes,
            )
        return state.active_movement_mode
    except Exception:
        logger.exception("Failed to establish the active movement mode for %s.", state.template.name)
        raise RuntimeError("Active movement mode could not be established.") from None


def printed_speed_for_state(state: CombatantState) -> int:
    try:
        mode = ensure_active_movement_mode(state)
        if mode == "walk":
            return int(state.template.speed_ft)
        field = _MODE_FIELDS.get(mode)
        if field is None:
            raise ValueError(f"Unknown movement mode {mode!r}.")
        speed = int(getattr(state.template.movement_modes, field, 0) or 0)
        return speed if speed > 0 else int(state.template.speed_ft)
    except Exception:
        logger.exception("Failed to resolve printed speed for %s.", state.template.name)
        raise RuntimeError("Printed movement-mode speed could not be resolved.") from None


def mover_is_opportunity_attack_exempt(state: CombatantState) -> bool:
    try:
        mode = ensure_active_movement_mode(state)
        return mode in (state.template.opportunity_attack_exempt_movement_modes or [])
    except Exception:
        logger.exception("Failed to resolve movement-mode OA exemption for %s.", state.template.name)
        raise RuntimeError("Movement-mode opportunity-attack exemption could not be resolved.") from None
