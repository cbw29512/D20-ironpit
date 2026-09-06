from __future__ import annotations

import re

from app.content.monster_combat_scope import feature_blocks, normalized_source_text
from app.content.monster_trait_source_audit import parse_trait_names
from app.domain.actions import SavingThrowAction

_DEATH_BURST = re.compile(
    r"Death Burst\. The .+? explodes when it dies\. "
    r"(?P<ability>Strength|Dexterity|Constitution|Intelligence|Wisdom|Charisma) Saving Throw: "
    r"DC (?P<dc>\d+), each creature in a (?P<radius>\d+)-foot Emanation originating from the .+?\. "
    r"Failure: \d+ \((?P<count>\d+)d(?P<size>\d+)(?P<bonus>\s*[+-]\s*\d+)?\) "
    r"(?P<type>Acid|Bludgeoning|Cold|Fire|Force|Lightning|Necrotic|Piercing|Poison|Psychic|Radiant|Slashing|Thunder) damage\. "
    r"Success: Half damage\.",
    re.I,
)


def parse_death_trigger_saves(row: dict[str, object]) -> list[SavingThrowAction]:
    traits = row.get("traits", "")
    names = parse_trait_names(traits, preserve_annotations=True) if str(traits).strip() else []
    death_name = next((name for name in names if name.split(" (")[0] == "Death Burst"), None)
    if death_name is None:
        return []
    block = normalized_source_text(feature_blocks(traits, names)[death_name])
    match = _DEATH_BURST.fullmatch(block)
    if match is None:
        raise ValueError(f"Unsupported Death Burst wording for {row.get('name')!r}: {block!r}")
    bonus = int((match.group("bonus") or "0").replace(" ", ""))
    return [SavingThrowAction(
        id="death-burst",
        name="Death Burst",
        save_ability=match.group("ability").lower(),
        dc=int(match.group("dc")),
        range_ft=int(match.group("radius")),
        damage_dice_count=int(match.group("count")),
        damage_dice_size=int(match.group("size")),
        damage_bonus=bonus,
        damage_type=match.group("type").lower(),
        success_damage="half",
        animation="death-burst",
    )]
