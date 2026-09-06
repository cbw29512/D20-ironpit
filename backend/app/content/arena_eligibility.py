from __future__ import annotations

from app.domain.models import CombatantTemplate
from app.domain.movement import MovementModes


def deferred_environment_reason(source: object | MovementModes) -> str | None:
    """Movement modes never block Iron Pit eligibility.

    The Pit owns positioning. A genuine environment-dependent combat effect must
    be audited from the effect or trait that changes combat math, not inferred
    from walk/fly/swim Speed values.
    """
    return None


def standard_arena_eligible(template: CombatantTemplate) -> bool:
    """All combatants are positionable by the Pit regardless of movement modes."""
    return True


def filter_standard_arena_eligible(templates: list[CombatantTemplate]) -> list[CombatantTemplate]:
    return [template for template in templates if standard_arena_eligible(template)]
