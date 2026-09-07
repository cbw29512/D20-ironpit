from __future__ import annotations

import re

from app.content.monster_combat_scope import feature_blocks
from app.content.monster_trait_source_audit import parse_trait_names

_ABILITY = r"Strength|Dexterity|Constitution|Intelligence|Wisdom|Charisma"
_SIZE = r"Tiny|Small|Medium|Large|Huge|Gargantuan"
_GRAPPLE_SAVE = re.compile(
    rf"^(?P<name>.+?)\. (?P<ability>{_ABILITY}) Saving Throw: DC (?P<dc>\d+), "
    rf"one (?P<size>{_SIZE}) or smaller creature .*?within (?P<range>\d+) feet\. "
    r"Failure: The target has the Grappled condition \(escape DC (?P<escape>\d+)\)\.$",
    re.I,
)


def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def parse_simple_bonus_save_actions(row: dict[str, object]) -> list[dict[str, object]]:
    """Parse mathematically simple Bonus Action saves into the universal save capability."""
    source = str(row.get("bonusActions", ""))
    headings = parse_trait_names(source, preserve_annotations=True) if source.strip() else []
    blocks = feature_blocks(source, headings) if headings else {}
    monster_slug = _slug(str(row["name"])); actions: list[dict[str, object]] = []
    for heading, block in blocks.items():
        if "Saving Throw:" not in block: continue
        match = _GRAPPLE_SAVE.fullmatch(block)
        if match is None: raise ValueError(f"Simple bonus-save parser cannot prove {row['name']} {heading!r}: {block!r}")
        actions.append({
            "id": f"srd-{monster_slug}-{_slug(heading)}", "name": heading, "action_cost": "bonus_action",
            "save_ability": match.group("ability").lower(), "dc": int(match.group("dc")), "range_ft": int(match.group("range")),
            "target_max_size": match.group("size").lower(),
            "grapple": {"kind": "grapple", "escape_dc": int(match.group("escape")), "max_target_size": match.group("size").lower()},
            "animation": "grapple",
        })
    return actions
