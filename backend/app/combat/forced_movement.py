from __future__ import annotations

from dataclasses import dataclass

from app.domain.control_effects import ForcedMovementEffect
from app.domain.encounters import EncounterCombatant
from app.domain.size import CreatureSize, size_at_most

ARENA_MIN_POSITION_FT = 0
ARENA_MAX_POSITION_FT = 15
CARD_FOOTPRINT_FT = 5


@dataclass(frozen=True)
class ForcedMovementResult:
    before_ft: int
    after_ft: int

    @property
    def moved_ft(self) -> int:
        return abs(self.after_ft - self.before_ft)


def _clamp(position_ft: int) -> int:
    return min(ARENA_MAX_POSITION_FT, max(ARENA_MIN_POSITION_FT, position_ft))


def _push_direction(source: EncounterCombatant, target: EncounterCombatant) -> int:
    if target.position_ft > source.position_ft:
        return 1
    if target.position_ft < source.position_ft:
        return -1
    # Fixed-formation fallback when two 5-ft cards share the same abstract point.
    return -1 if target.side == "heroes" else 1


def maximum_legal_destination(
    source: EncounterCombatant,
    target: EncounterCombatant,
    effect: ForcedMovementEffect,
) -> int:
    """Choose the maximum legal displacement permitted by an offensive `up to` effect."""
    if effect.direction == "push":
        direction = _push_direction(source, target)
        return _clamp(target.position_ft + direction * effect.max_distance_ft)

    distance = abs(source.position_ft - target.position_ft)
    available = max(0, distance - CARD_FOOTPRINT_FT)
    moved = min(effect.max_distance_ft, available)
    if moved == 0:
        return target.position_ft
    direction = 1 if source.position_ft > target.position_ft else -1
    return _clamp(target.position_ft + direction * moved)


def apply_forced_movement(
    source: EncounterCombatant,
    target: EncounterCombatant,
    effect: ForcedMovementEffect | None,
    *,
    max_target_size: CreatureSize | None = None,
) -> ForcedMovementResult | None:
    if effect is None:
        return None
    if max_target_size is not None and not size_at_most(target.state.template.size, max_target_size):
        return None
    before = target.position_ft
    target.position_ft = maximum_legal_destination(source, target, effect)
    return ForcedMovementResult(before_ft=before, after_ft=target.position_ft)
