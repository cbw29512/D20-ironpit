from __future__ import annotations

import re

_SIZE = r"Tiny|Small|Medium|Large|Huge|Gargantuan"
_ABILITY = r"Strength|Dexterity|Constitution|Intelligence|Wisdom|Charisma"
_DAMAGE = r"Acid|Bludgeoning|Cold|Fire|Force|Lightning|Necrotic|Piercing|Poison|Psychic|Radiant|Slashing|Thunder"
_CONDITION = r"Blinded|Charmed|Deafened|Exhaustion|Frightened|Incapacitated|Paralyzed|Petrified|Poisoned|Prone|Restrained|Stunned|Unconscious"
_POINT_RADIUS_SAVE = re.compile(
    rf"^(?P<name>.+?)\. .+?a point .+?within (?P<range>\d+) feet\. "
    rf"(?P<ability>{_ABILITY}) Saving Throw: DC (?P<dc>\d+), each creature in a "
    r"(?P<radius>\d+)-foot-radius Sphere centered on that point\. Failure: \d+ "
    rf"\((?P<count>\d+)d(?P<size>\d+)(?P<bonus>\s*[+-]\s*\d+)?\) (?P<type>{_DAMAGE}) damage\."
    rf"(?: If the target is a (?P<max_size>{_SIZE}) or smaller creature, it has the (?P<condition>{_CONDITION}) condition\.)?"
    r"(?: Success: Half damage(?: only)?\.)?$",
    re.I,
)


def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def parse_point_radius_save(
    row: dict[str, object], heading: str, block: str,
) -> dict[str, object] | None:
    """Parse a point-centered Sphere save while keeping point range distinct from radius."""
    match = _POINT_RADIUS_SAVE.fullmatch(block)
    if match is None:
        return None
    bonus = int((match.group("bonus") or "0").replace(" ", ""))
    result: dict[str, object] = {
        "id": f"srd-{_slug(str(row['name']))}-{_slug(heading)}",
        "name": heading,
        "save_ability": match.group("ability").lower(),
        "dc": int(match.group("dc")),
        "range_ft": int(match.group("range")),
        "area": {"shape": "radius", "size_ft": int(match.group("radius"))},
        "damage": {
            "count": int(match.group("count")),
            "size": int(match.group("size")),
            "bonus": bonus,
        },
        "damage_type": match.group("type").lower(),
        "success_damage": "half" if "Success: Half damage" in match.group(0) else "none",
        "animation": "save-effect",
    }
    condition = match.group("condition")
    if condition:
        result["failure_conditions"] = [{
            "kind": "condition",
            "condition": condition.lower(),
            "max_target_size": match.group("max_size").lower(),
        }]
    return result
