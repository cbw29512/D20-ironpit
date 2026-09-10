from __future__ import annotations

from typing import Literal

AbilityName = Literal["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]
ConditionTiming = Literal["source_turn_start", "source_turn_end", "target_turn_start", "target_turn_end"]
ConditionName = Literal[
    "blinded", "charmed", "deafened", "exhaustion", "frightened", "grappled",
    "incapacitated", "invisible", "paralyzed", "petrified", "poisoned", "prone",
    "restrained", "stunned", "unconscious",
]
