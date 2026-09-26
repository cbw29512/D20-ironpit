from __future__ import annotations

import logging
from dataclasses import dataclass

from app.combat.action_economy import spend
from app.combat.resources import spend_resource
from app.domain.combatants import CombatantTemplate
from app.domain.models import CombatantState
from app.domain.replacement_forms import ReplacementFormState

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class ReplacementFormResult:
    source_id: str
    form_name: str
    resource_remaining: int | None
    reverted: bool = False


def enter_replacement_form(
    state: CombatantState,
    *,
    source_id: str,
    source_name: str,
    form_template: CombatantTemplate,
    action_cost: str,
    resource_id: str | None = None,
    resource_cost: int = 1,
    voluntary_revert_action: str = "bonus_action",
) -> ReplacementFormResult:
    try:
        if state.replacement_form is not None:
            raise ValueError(f"{state.template.name} is already in a replacement form.")
        if form_template.kind != "monster":
            raise ValueError("Replacement form templates must use monster-form combat data.")
        spend(state, action_cost)
        remaining = spend_resource(state, resource_id, resource_cost)
        state.replacement_form = ReplacementFormState(
            source_id=source_id,
            source_name=source_name,
            original_template=state.template,
            form_template=form_template,
            original_hp=state.current_hp,
            form_hp=form_template.max_hp,
            form_max_hp=form_template.max_hp,
            resource_id=resource_id,
            resource_cost=resource_cost,
            voluntary_revert_action=voluntary_revert_action,
        )
        return ReplacementFormResult(
            source_id=source_id,
            form_name=form_template.name,
            resource_remaining=remaining,
        )
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Failed to enter replacement form %s for %s.", form_template.name, state.template.name)
        raise RuntimeError("Replacement form could not be entered.") from exc


def revert_replacement_form(
    state: CombatantState,
    *,
    spend_voluntary_action: bool,
) -> ReplacementFormResult:
    try:
        active = state.replacement_form
        if active is None:
            raise ValueError(f"{state.template.name} is not in a replacement form.")
        if spend_voluntary_action:
            spend(state, active.voluntary_revert_action)
        result = ReplacementFormResult(
            source_id=active.source_id,
            form_name=active.form_template.name,
            resource_remaining=None,
            reverted=True,
        )
        state.replacement_form = None
        return result
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Failed to revert replacement form for %s.", state.template.name)
        raise RuntimeError("Replacement form could not be reverted.") from exc


def apply_replacement_form_damage(
    state: CombatantState,
    amount: int,
) -> tuple[int, bool]:
    """Apply damage to active form HP and return (excess_damage, reverted)."""
    try:
        if amount < 0:
            raise ValueError("Replacement-form damage cannot be negative.")
        active = state.replacement_form
        if active is None or amount == 0:
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
        logger.exception("Failed to resolve replacement-form damage for %s.", state.template.name)
        raise RuntimeError("Replacement-form damage could not be resolved.") from exc
