from __future__ import annotations

import re

DAMAGE_TYPES = {
    "acid", "bludgeoning", "cold", "fire", "force", "lightning", "necrotic",
    "piercing", "poison", "psychic", "radiant", "slashing", "thunder",
}
_SWARM_HALF_DAMAGE = re.compile(
    r"(?:or\s+)?\d+\s*\((\d+)d(\d+)(?:\s*([+\-−])\s*(\d+))?\)\s*([A-Za-z]+) damage "
    r"if the swarm has half of its hit points or fewer\.?'?",
    re.I,
)


def parse_conditional_replacement_damage(remainder: str) -> tuple[list[dict], str]:
    """Parse generic conditional replacement weapon damage from printed attack text."""
    match = _SWARM_HALF_DAMAGE.search(remainder)
    if not match:
        return [], remainder
    count, size, sign, bonus, damage_type = match.groups()
    dtype = damage_type.lower()
    if dtype not in DAMAGE_TYPES:
        return [], remainder
    modifier = int(bonus or 0) * (-1 if sign in {"-", "−"} else 1)
    conditional = {
        "trigger": "attacker_bloodied",
        "mode": "replace_weapon",
        "dice_count": int(count),
        "dice_size": int(size),
        "damage_bonus": modifier,
        "damage_type": dtype,
    }
    residual = (remainder[:match.start()] + " " + remainder[match.end():]).strip(" .,;")
    return [conditional], residual
