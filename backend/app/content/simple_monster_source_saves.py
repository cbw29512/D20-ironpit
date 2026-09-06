from __future__ import annotations

import re

from app.content.monster_combat_scope import feature_blocks
from app.content.monster_trait_source_audit import parse_trait_names

_ABILITY = r"Strength|Dexterity|Constitution|Intelligence|Wisdom|Charisma"
_DAMAGE = r"Acid|Bludgeoning|Cold|Fire|Force|Lightning|Necrotic|Piercing|Poison|Psychic|Radiant|Slashing|Thunder"
_SIMPLE_SAVE = re.compile(
    rf"^(?P<name>.+?)\. (?P<ability>{_ABILITY}) Saving Throw: DC (?P<dc>\d+), "
    r"one creature .*?within (?P<range>\d+) feet\. Failure: \d+ "
    rf"\((?P<count>\d+)d(?P<size>\d+)(?P<bonus>\s*[+-]\s*\d+)?\) (?P<type>{_DAMAGE}) damage\."
    r"(?: Success: Half damage\.)?$",
    re.I,
)


def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def parse_simple_save_actions(row: dict[str, object]) -> list[dict[str, object]]:
    """Parse one-target damage saves; fail closed on other save-action shapes."""
    source = str(row.get("actions", ""))
    headings = parse_trait_names(source, preserve_annotations=True) if source.strip() else []
    blocks = feature_blocks(source, headings) if headings else {}
    monster_slug = _slug(str(row["name"]))
    actions: list[dict[str, object]] = []
    for heading, block in blocks.items():
        if "Saving Throw:" not in block or "Attack Roll:" in block:
            continue
        match = _SIMPLE_SAVE.fullmatch(block)
        if match is None:
            raise ValueError(f"Simple save parser cannot prove {row['name']} {heading!r}: {block!r}")
        bonus = int((match.group("bonus") or "0").replace(" ", ""))
        actions.append({
            "id": f"srd-{monster_slug}-{_slug(heading)}", "name": heading,
            "save_ability": match.group("ability").lower(), "dc": int(match.group("dc")),
            "range_ft": int(match.group("range")),
            "damage": {"count": int(match.group("count")), "size": int(match.group("size")), "bonus": bonus},
            "damage_type": match.group("type").lower(),
            "success_damage": "half" if "Success: Half damage." in block else "none",
            "animation": "save-effect",
        })
    return actions
