from __future__ import annotations

import argparse
import html
import json
import logging
import re
import unicodedata
from pathlib import Path

logger = logging.getLogger(__name__)
DAMAGE_TYPES = {
    "acid", "bludgeoning", "cold", "fire", "force", "lightning", "necrotic",
    "piercing", "poison", "psychic", "radiant", "slashing", "thunder",
}


def _slug(value: str) -> str:
    text = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", text).strip("-")


def _integer(value: object) -> int:
    match = re.search(r"-?\d+", str(value))
    return int(match.group()) if match else 0


def _plain(value: str) -> str:
    text = re.sub(r"<[^>]+>", " ", value or "")
    return re.sub(r"\s+", " ", html.unescape(text).replace("\u00ad", "")).strip()


def _names(value: str | None) -> list[str]:
    if not value:
        return []
    return [_plain(item).rstrip(".") for item in re.findall(r"<strong>(.*?)</strong>", value, re.I | re.S)]


def _speed(value: str | None) -> dict[str, int]:
    result: dict[str, int] = {}
    for mode, amount in re.findall(r"(?:(walk|fly|swim|climb|burrow)\s+)?(\d+)\s*ft\.", (value or "").lower()):
        result[mode or "walk"] = int(amount)
    return result


def _bonuses(value: str | None) -> dict[str, int]:
    if not value:
        return {}
    return {
        name.strip().lower().replace(" ", "_"): int(amount)
        for name, amount in re.findall(r"([A-Za-z ]+?)\s*([+-]\d+)(?:,|$)", value)
    }


def _list(value: str | None) -> list[str]:
    if not value:
        return []
    return [item.strip().lower() for item in re.split(r"[,;]", value) if item.strip()]


def _attack(paragraph: str) -> dict | None:
    text = _plain(paragraph)
    name_match = re.search(r"<strong>(.*?)</strong>", paragraph, re.I | re.S)
    if not name_match:
        return None
    kind = "melee" if re.search(r"Melee(?: or Ranged)? (?:Weapon|Spell) Attack:", text, re.I) else None
    if re.search(r"Ranged (?:Weapon|Spell) Attack:", text, re.I):
        kind = "ranged"
    hit = re.search(r"([+-]\d+) to hit", text, re.I)
    damage = re.search(
        r"Hit:\s*(\d+)\s*\((\d+)d(\d+)(?:\s*([+-])\s*(\d+))?\)\s*([A-Za-z]+) damage",
        text, re.I,
    )
    if not kind or not hit or not damage:
        return None
    average, count, size, sign, bonus, damage_type = damage.groups()
    damage_type = damage_type.lower()
    if damage_type not in DAMAGE_TYPES:
        return None
    reach = re.search(r"reach (\d+) ft", text, re.I)
    ranges = re.search(r"range (\d+)(?:\s*ft\.)?\s*/\s*(\d+) ft", text, re.I)
    if not ranges:
        ranges = re.search(r"range (\d+) ft", text, re.I)
    result = {
        "id": _slug(_plain(name_match.group(1))), "name": _plain(name_match.group(1)).rstrip("."),
        "kind": kind, "attack_bonus": int(hit.group(1)),
        "damage": {
            "average": int(average), "dice_count": int(count), "dice_size": int(size),
            "bonus": int(bonus or 0) * (-1 if sign == "-" else 1), "type": damage_type,
        },
    }
    if reach:
        result["reach_ft"] = int(reach.group(1))
    if ranges:
        result["normal_range_ft"] = int(ranges.group(1))
        if ranges.lastindex and ranges.lastindex >= 2 and ranges.group(2):
            result["long_range_ft"] = int(ranges.group(2))
    return result


def _record(source: dict) -> dict:
    meta = source.get("meta", "")
    size, _, rest = meta.partition(" ")
    creature_type, _, alignment = rest.partition(",")
    hp = source.get("Hit Points", "")
    attacks = [
        attack for paragraph in (re.findall(r"<p>(.*?)</p>", source.get("Actions", ""), re.I | re.S) or [])
        if (attack := _attack(paragraph)) is not None
    ]
    return {
        "id": _slug(source["name"]), "name": source["name"], "ruleset": "2014",
        "size": size.title(), "creature_type": creature_type.strip().split(" ")[0],
        "alignment": alignment.strip() or None, "armor_class": _integer(source.get("Armor Class")),
        "max_hp": _integer(hp), "hit_dice": (re.search(r"\(([^)]+)\)", hp) or [None, None])[1],
        "speed": _speed(source.get("Speed")),
        "abilities": {key.lower(): _integer(source.get(key)) for key in ("STR", "DEX", "CON", "INT", "WIS", "CHA")},
        "saving_throws": _bonuses(source.get("Saving Throws")), "skills": _bonuses(source.get("Skills")),
        "damage_resistances": _list(source.get("Damage Resistances")),
        "damage_immunities": _list(source.get("Damage Immunities")),
        "damage_vulnerabilities": _list(source.get("Damage Vulnerabilities")),
        "condition_immunities": _list(source.get("Condition Immunities")),
        "challenge_rating": (source.get("Challenge") or "").split(" ", 1)[0] or None,
        "attacks": attacks, "action_names": _names(source.get("Actions")),
        "trait_names": _names(source.get("Traits")), "reaction_names": _names(source.get("Reactions")),
        "legendary_action_names": _names(source.get("Legendary Actions")),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Normalize a 2014 monster JSON export for Iron Pit.")
    parser.add_argument("source", type=Path)
    parser.add_argument("--output", type=Path, default=Path("data/monsters/2014/catalog.json"))
    args = parser.parse_args()
    try:
        raw = json.loads(args.source.read_text(encoding="utf-8"))
        catalog = [_record(item) for item in raw]
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(catalog, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"wrote {len(catalog)} monsters to {args.output}")
        return 0
    except Exception as exc:
        logger.exception("2014 monster import failed: %s", exc)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
