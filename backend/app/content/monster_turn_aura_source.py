from __future__ import annotations

import re

from app.content.monster_combat_scope import feature_blocks, normalized_source_text
from app.content.monster_trait_source_audit import parse_trait_names
from app.domain.combatants import TurnDamageAuraDefinition
from app.domain.weapons import DamageType

_FIRE_AURA = re.compile(
    r"Fire Aura\. At the end of each of .+? turns, each creature of .+? choice in a "
    r"(?P<radius>\d+)-foot Emanation originating from .+? takes \d+ "
    r"\((?P<count>\d+)d(?P<size>\d+)(?P<bonus>\s*[+-]\s*\d+)?\) "
    r"(?P<type>[A-Za-z]+) damage unless .+? has the Incapacitated condition\.",
    re.I,
)


def parse_turn_damage_auras(row: dict[str, object]) -> list[TurnDamageAuraDefinition]:
    traits = row.get("traits", "")
    names = parse_trait_names(traits, preserve_annotations=True) if str(traits).strip() else []
    blocks = feature_blocks(traits, names) if names else {}
    fire_name = next((name for name in names if name.split(" (")[0] == "Fire Aura"), None)
    if fire_name is None:
        return []
    block = normalized_source_text(blocks[fire_name])
    match = _FIRE_AURA.fullmatch(block)
    if match is None:
        raise ValueError(f"Unsupported Fire Aura wording for {row.get('name')!r}: {block!r}")
    damage_type = DamageType(match.group("type").lower())
    bonus = int((match.group("bonus") or "0").replace(" ", ""))
    return [TurnDamageAuraDefinition(
        id="fire-aura",
        name="Fire Aura",
        radius_ft=int(match.group("radius")),
        dice_count=int(match.group("count")),
        dice_size=int(match.group("size")),
        damage_bonus=bonus,
        damage_type=damage_type,
        target_mode="enemies",
        suppressed_if_incapacitated=True,
    )]
