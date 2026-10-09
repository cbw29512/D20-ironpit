"""2014 printed Angelic Weapons -> universal typed on-hit rider, no runtime name branches."""
from __future__ import annotations

import re

from app.content.monster_included_weapon_traits_2014 import included_weapon_trait_names_2014
from app.content.monster_source_2014 import SourceMonster2014
from app.content.monster_source_sections_2014 import source_sections_2014
from app.domain.weapons import OnHitDamage, DamageType


def source_angelic_weapon_hit_rider_2014(monster: SourceMonster2014) -> OnHitDamage:
    """Return source-proven on-hit damage, or fail closed if no valid trait."""
    if "Angelic Weapons" not in included_weapon_trait_names_2014(monster):
        raise ValueError("2014 Angelic Weapons source trait is not independently validated.")
    text = source_sections_2014(monster.source_traits).get("Angelic Weapons", "")
    found = re.fullmatch(
        r".*?\bextra\s+(\d+)d(\d+)\s+radiant\s+damage\s+\(included\s+in\s+the\s+attack\)\.",
        text.strip(), re.I,
    )
    if found is None:
        raise ValueError("Unrecognized 2014 Angelic Weapons hit damage source.")
    count, size = map(int, found.groups())
    return OnHitDamage(
        source=f"2014:{monster.id}:Angelic Weapons",
        dice_count=count, dice_size=size, damage_type=DamageType.RADIANT,
    )
