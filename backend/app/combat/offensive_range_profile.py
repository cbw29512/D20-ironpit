from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class OffensiveRangeProfile:
    """Immutable movement-facing range contract for one offensive option.

    ``max_range_ft`` answers whether the option can legally reach at all.
    ``preferred_range_ft`` is the distance movement should seek when doing so
    improves execution quality, such as avoiding ranged-weapon disadvantage.
    ``execution_rank`` mirrors ordinary turn-family ordering after resource
    priority has been considered.
    """

    priority: int
    family: str
    max_range_ft: int
    preferred_range_ft: int
    execution_rank: int = 0

    def __post_init__(self) -> None:
        if self.priority < 0 or self.execution_rank < 0:
            raise ValueError("Offensive range priorities cannot be negative.")
        if self.max_range_ft < 0 or self.preferred_range_ft < 0:
            raise ValueError("Offensive ranges cannot be negative.")
        if self.preferred_range_ft > self.max_range_ft:
            raise ValueError("Preferred offensive range cannot exceed maximum range.")
