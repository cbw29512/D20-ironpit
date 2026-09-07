from __future__ import annotations

import re

_ABILITY = r"Strength|Dexterity|Constitution|Intelligence|Wisdom|Charisma"
_DAMAGE = r"Acid|Bludgeoning|Cold|Fire|Force|Lightning|Necrotic|Piercing|Poison|Psychic|Radiant|Slashing|Thunder"
_SIZE = r"Tiny|Small|Medium|Large|Huge|Gargantuan"
_HEAD = re.compile(
    rf"^(?P<name>.+?)\. (?P<ability>{_ABILITY}) Saving Throw: DC (?P<dc>\d+), "
    rf"one (?P<target_size>{_SIZE}) or smaller creature .*?within (?P<range>\d+) feet\. Failure: (?P<failure>.+)$",
    re.I,
)
_DAMAGE_PACKET = re.compile(
    rf"(?P<average>\d+) \((?P<count>\d+)d(?P<size>\d+)(?P<bonus>\s*[+-]\s*\d+)?\) (?P<type>{_DAMAGE}) damage",
    re.I,
)
_GRAPPLE = re.compile(r"Grappled condition \(escape DC (?P<dc>\d+)\)", re.I)


def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def _dice(match: re.Match[str]) -> dict[str, int]:
    return {
        "count": int(match.group("count")), "size": int(match.group("size")),
        "bonus": int((match.group("bonus") or "0").replace(" ", "")),
    }


def parse_constrict_save(row: dict[str, object], heading: str, block: str) -> dict[str, object] | None:
    """Parse save → typed damage packet(s) → Grappled/(optional) Restrained as one universal family."""
    match = _HEAD.fullmatch(block)
    if match is None: return None
    failure = match.group("failure"); grapple = _GRAPPLE.search(failure)
    if grapple is None: return None
    packets = list(_DAMAGE_PACKET.finditer(failure))
    if not packets: return None
    primary = packets[0]; target_size = match.group("target_size").lower()
    result: dict[str, object] = {
        "id": f"srd-{_slug(str(row['name']))}-{_slug(heading)}", "name": heading,
        "save_ability": match.group("ability").lower(), "dc": int(match.group("dc")),
        "range_ft": int(match.group("range")), "target_max_size": target_size,
        "damage": _dice(primary), "damage_type": primary.group("type").lower(),
        "grapple": {
            "kind": "grapple", "escape_dc": int(grapple.group("dc")), "max_target_size": target_size,
            "restrains": "Restrained condition until the grapple ends" in failure,
        },
        "animation": "grapple",
    }
    if len(packets) > 1:
        result["additional_damage"] = [
            {
                "kind": "damage", "source": packet.group("type").title(), "dice": _dice(packet),
                "damage_type": packet.group("type").lower(), "trigger": "on_save", "mode": "add",
            }
            for packet in packets[1:]
        ]
    return result
