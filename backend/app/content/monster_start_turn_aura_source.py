from __future__ import annotations

import re

from app.content.monster_combat_scope import feature_blocks, normalized_source_text
from app.content.monster_trait_source_audit import parse_trait_names
from app.domain.passive_effects import StartTurnSaveAuraDefinition

_STENCH = re.compile(
    r"Stench\. (?P<ability>Strength|Dexterity|Constitution|Intelligence|Wisdom|Charisma) Saving Throw: "
    r"DC (?P<dc>\d+), any creature that starts its turn in a (?P<radius>\d+)-foot Emanation "
    r"originating from the [^.]+\. Failure: The target has the (?P<condition>[A-Za-z]+) condition "
    r"until the start of its next turn\.",
    re.I,
)


def parse_start_turn_save_auras(row: dict[str, object]) -> list[StartTurnSaveAuraDefinition]:
    traits = row.get("traits", "")
    names = parse_trait_names(traits, preserve_annotations=True) if str(traits).strip() else []
    blocks = feature_blocks(traits, names) if names else {}
    name = next((item for item in names if item.split(" (")[0] == "Stench"), None)
    if name is None:
        return []
    block = normalized_source_text(blocks[name])
    match = _STENCH.fullmatch(block)
    if match is None:
        raise ValueError(f"Unsupported Stench wording for {row.get('name')!r}: {block!r}")
    return [StartTurnSaveAuraDefinition(
        id="stench", name="Stench", radius_ft=int(match.group("radius")),
        save_ability=match.group("ability").lower(), dc=int(match.group("dc")),
        failure_condition=match.group("condition").lower(),
        condition_expiry_timing="target_turn_start", target_mode="all-other-creatures",
    )]
