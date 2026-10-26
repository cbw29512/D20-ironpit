"""2014 source-owned proof of fight-only weapon corrosion, separate from admission.

The arena adaptation affects weapons in the fight; the immutable source card
keeps its printed permanent rule and any independent action/armor riders.
"""
from __future__ import annotations

from dataclasses import dataclass
import re

from app.content.monster_source_2014 import SourceMonster2014
from app.content.monster_source_sections_2014 import source_sections_2014

_CORRODE_WEAPON_CLAUSE = re.compile(
    r"Any nonmagical weapon made of metal that hits the (?P<target>[\w -]+) corrodes\. "
    r"After dealing damage, the weapon takes a permanent and cumulative −1 "
    r"penalty to damage rolls\. If its penalty drops to −5, the weapon is "
    r"destroyed\. Nonmagical ammunition made of metal that hits the "
    r"(?P=target) is destroyed after dealing damage\. "
    r"The (?P=target) can eat through 2-inch-thick, nonmagical metal in 1 round\.",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class SourceWeaponCorrosion2014:
    source_name: str = "Corrode Metal"
    damage_penalty_per_hit: int = 1
    unusable_at_penalty: int = 5
    requires_nonmagical_metal_weapon: bool = True


def source_weapon_corrosion_2014(
    monster: SourceMonster2014,
) -> SourceWeaponCorrosion2014 | None:
    """Return only a fully verified 2014 equipment-corrosion source profile."""
    if "Corrode Metal" not in monster.trait_names:
        return None
    text = source_sections_2014(
        monster.source_traits, include_continuations=True,
    ).get("Corrode Metal")
    if text is None or _CORRODE_WEAPON_CLAUSE.fullmatch(text) is None:
        return None
    return SourceWeaponCorrosion2014()
