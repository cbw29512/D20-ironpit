from __future__ import annotations

import re

from app.content.monster_combat_scope import feature_blocks, normalized_source_text
from app.content.monster_trait_source_audit import parse_trait_names
from app.domain.passive_effects import AllyRollAuraDefinition

_AUTHORITY = re.compile(
    r"Aura of Authority\. While in a (?P<radius>\d+)-foot Emanation originating from the .+?, "
    r"the .+? and its allies have Advantage on attack rolls and saving throws, provided the .+? "
    r"doesn[’']t have the Incapacitated condition\.",
    re.I,
)


def parse_ally_roll_auras(row: dict[str, object]) -> list[AllyRollAuraDefinition]:
    traits = row.get("traits", "")
    names = parse_trait_names(traits, preserve_annotations=True) if str(traits).strip() else []
    aura_name = next((name for name in names if name.split(" (")[0] == "Aura of Authority"), None)
    if aura_name is None:
        return []
    block = normalized_source_text(feature_blocks(traits, names)[aura_name])
    match = _AUTHORITY.fullmatch(block)
    if match is None:
        raise ValueError(f"Unsupported Aura of Authority wording for {row.get('name')!r}: {block!r}")
    return [AllyRollAuraDefinition(
        id="aura-of-authority",
        name="Aura of Authority",
        radius_ft=int(match.group("radius")),
        attack_advantage=True,
        saving_throw_advantage=True,
        suppressed_if_incapacitated=True,
    )]
