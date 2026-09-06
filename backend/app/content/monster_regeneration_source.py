from __future__ import annotations

import re

from app.content.monster_combat_scope import feature_blocks
from app.content.monster_trait_source_audit import parse_trait_names
from app.domain.passive_effects import RegenerationDefinition
from app.domain.weapons import DamageType

_AMOUNT = re.compile(r"\bregains\s+(\d+)\s+Hit Points?\s+at the start of each of (?:its|their) turns?", re.I)
_DELAYED_DEATH = re.compile(
    r"\bdies? only if (?:it|they) starts? (?:its|their) turn with 0 Hit Points? and doesn[’']t regenerate\b",
    re.I,
)
_SUPPRESSION = re.compile(
    r"\bIf .+? takes? (.+?) damage, this trait doesn[’']t function on .+? next turn\b",
    re.I,
)


def parse_regeneration(row: dict[str, object]) -> RegenerationDefinition | None:
    traits = row.get("traits", "")
    names = parse_trait_names(traits, preserve_annotations=True) if str(traits).strip() else []
    regeneration_name = next((name for name in names if name.split(" (")[0] == "Regeneration"), None)
    if regeneration_name is None:
        return None
    block = feature_blocks(traits, names)[regeneration_name]
    amount_match = _AMOUNT.search(block)
    if amount_match is None:
        raise ValueError(f"Unsupported Regeneration wording for {row.get('name')!r}: {block!r}")
    suppression_match = _SUPPRESSION.search(block)
    suppressed: list[DamageType] = []
    if suppression_match is not None:
        clause = suppression_match.group(1).lower()
        suppressed = [damage_type for damage_type in DamageType if damage_type.value in clause]
        if not suppressed:
            raise ValueError(f"Regeneration suppression damage types were not parsed for {row.get('name')!r}.")
    return RegenerationDefinition(
        amount=int(amount_match.group(1)),
        suppressed_by_damage_types=suppressed,
        delays_death_at_zero=bool(_DELAYED_DEATH.search(block)),
    )
