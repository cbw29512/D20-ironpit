from __future__ import annotations

import re

from app.content.monster_combat_scope import feature_blocks
from app.content.monster_trait_source_audit import parse_trait_names

_ABILITY = r"Strength|Dexterity|Constitution|Intelligence|Wisdom|Charisma"
_SIZE = r"Tiny|Small|Medium|Large|Huge|Gargantuan"
_CONDITION = r"Blinded|Charmed|Deafened|Frightened|Incapacitated|Paralyzed|Petrified|Poisoned|Prone|Restrained|Stunned|Unconscious"
_DAMAGE = r"Acid|Bludgeoning|Cold|Fire|Force|Lightning|Necrotic|Piercing|Poison|Psychic|Radiant|Slashing|Thunder"
_GRAPPLE_SAVE = re.compile(
    rf"^(?P<name>.+?)\. (?P<ability>{_ABILITY}) Saving Throw: DC (?P<dc>\d+), "
    rf"one (?P<size>{_SIZE}) or smaller creature .*?within (?P<range>\d+) feet\. "
    r"Failure: The target has the Grappled condition \(escape DC (?P<escape>\d+)\)\.$",
    re.I,
)
_TRAMPLE_SAVE = re.compile(
    rf"^(?P<name>.+?)\. (?P<ability>{_ABILITY}) Saving Throw: DC (?P<dc>\d+), one creature within (?P<range>\d+) feet that has the (?P<condition>{_CONDITION}) condition\. "
    rf"Failure: \d+ \((?P<count>\d+)d(?P<die>\d+)(?P<bonus>\s*[+-]\s*\d+)?\) (?P<type>{_DAMAGE}) damage\. Success: Half damage\.$", re.I,
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
        if match:
            actions.append({
                "id": f"srd-{monster_slug}-{_slug(heading)}", "name": heading, "action_cost": "bonus_action",
                "save_ability": match.group("ability").lower(), "dc": int(match.group("dc")), "range_ft": int(match.group("range")),
                "target_max_size": match.group("size").lower(),
                "grapple": {"kind": "grapple", "escape_dc": int(match.group("escape")), "max_target_size": match.group("size").lower()},
                "animation": "grapple",
            }); continue
        match = _TRAMPLE_SAVE.fullmatch(block)
        if match:
            bonus = int((match.group("bonus") or "0").replace(" ", ""))
            actions.append({
                "id": f"srd-{monster_slug}-{_slug(heading)}", "name": heading, "action_cost": "bonus_action",
                "save_ability": match.group("ability").lower(), "dc": int(match.group("dc")), "range_ft": int(match.group("range")),
                "required_target_conditions": [match.group("condition").lower()],
                "damage": {"count": int(match.group("count")), "size": int(match.group("die")), "bonus": bonus},
                "damage_type": match.group("type").lower(), "success_damage": "half", "animation": "save-effect",
            }); continue
        raise ValueError(f"Simple bonus-save parser cannot prove {row['name']} {heading!r}: {block!r}")
    return actions
