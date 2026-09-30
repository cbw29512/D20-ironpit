from __future__ import annotations

import logging

from app.combat.condition_rules import is_incapacitated
from app.combat.replacement_forms import revert_replacement_form
from app.domain.models import CombatantState

logger = logging.getLogger(__name__)


def revert_replacement_form_if_incapacitated(state: CombatantState) -> bool:
    """Revert an active form when its declared lifecycle ends on incapacitation."""
    try:
        active = state.replacement_form
        if active is None or not active.ends_on_incapacitated:
            return False
        if not (state.is_dead or is_incapacitated(state)):
            return False
        revert_replacement_form(state, spend_voluntary_action=False)
        return True
    except ValueError:
        raise
    except Exception as exc:
        logger.exception(
            "Failed incapacitation-triggered replacement-form reversion for %s.",
            state.template.name,
        )
        raise RuntimeError(
            "Replacement-form incapacitation lifecycle could not be resolved."
        ) from exc


def apply_replacement_form_damage(
    state: CombatantState,
    amount: int,
) -> tuple[int, bool]:
    """Apply damage to form-pool HP or pass retained-owner HP damage through."""
    try:
        if amount < 0:
            raise ValueError("Replacement-form damage cannot be negative.")
        active = state.replacement_form
        if active is None or amount == 0:
            return amount, False
        if active.hp_mode == "retain_owner":
            return amount, False
        absorbed = min(active.form_hp, amount)
        active.form_hp -= absorbed
        excess = amount - absorbed
        if active.form_hp > 0:
            return 0, False
        revert_replacement_form(state, spend_voluntary_action=False)
        return excess, True
    except ValueError:
        raise
    except Exception as exc:
        logger.exception(
            "Failed to resolve replacement-form damage for %s.", state.template.name
        )
        raise RuntimeError("Replacement-form damage could not be resolved.") from exc
