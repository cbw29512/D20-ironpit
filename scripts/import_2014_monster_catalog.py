from __future__ import annotations

import argparse
import html
import json
import logging
import re
import unicodedata
from pathlib import Path

from import_2014_multiattack import parse_multiattack

logger = logging.getLogger(__name__)
DAMAGE_TYPES = {
    "acid", "bludgeoning", "cold", "fire", "force", "lightning", "necrotic",
    "piercing", "poison", "psychic", "radiant", "slashing", "thunder",
}
CONDITIONS = {
    "blinded", "charmed", "deafened", "exhaustion", "frightened", "grappled",
    "incapacitated", "invisible", "paralyzed", "petrified", "poisoned", "prone",
    "restrained", "stunned", "unconscious",
}


def _slug(value: str) -> str:
    text = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", text).strip("-")


def _plain(value: str | None) -> str:
    text = re.sub(r"<[^>]+>", " ", value or "")
    return re.sub(r"\s+", " ", html.unescape(text).replace("\u00ad", "")).strip()


def _integer(value: object) -> int:
    match = re.search(r"-?\d+", str(value))
    return int(match.group()) if match else 0


def _names(value: str | None) -> list[str]:
    return [_plain(item).rstrip(".") for item in re.findall(r"<strong>(.*?)</strong>", value or "", re.I | re.S)]


def _speed(value: str | None) -> dict[str, int]:
    return {
        mode or "walk": int(amount)
        for mode, amount in re.findall(r"(?:(walk|fly|swim|climb|burrow)\s+)?(\d+)\s*ft\.", (value or "").lower())
    }


def _bonuses(value: str | None) -> dict[str, int]:
    return {
        name.strip().lower().replace(" ", "_"): int(amount)
        for name, amount in re.findall(r"([A-Za-z ]+?)\s*([+-]\d+)(?:,|$)", value or "")
    }


def _simple_values(value: str | None, allowed: set[str]) -> tuple[list[str], list[str]]:
    text = _plain(value).lower()
    simple: list[str] = []
    unsupported: list[str] = []
    for clause in [item.strip().rstrip(".") for item in text.split(";") if item.strip()]:
        parts = [part.strip() for part in clause.split(",") if part.strip()]
        if parts and all(part in allowed for part in parts):
            simple.extend(parts)
        elif clause in allowed:
            simple.append(clause)
        else:
            unsupported.append(clause)
    return simple, unsupported


def _attack(paragraph: str) -> dict | None:
    text = _plain(paragraph)
    name_match = re.search(r"<strong>(.*?)</strong>", paragraph, re.I | re.S)
    hit = re.search(r"([+-]\d+) to hit", text, re.I)
    damage = re.search(r"Hit:\s*(\d+)\s*\((\d+)d(\d+)(?:\s*([+-])\s*(\d+))?\)\s*([A-Za-z]+) damage", text, re.I)
    if not name_match or not hit or not damage:
        return None
    if re.search(r"Ranged (?:Weapon|Spell) Attack:", text, re.I):
        kind = "ranged"
    elif re.search(r"Melee(?: or Ranged)? (?:Weapon|Spell) Attack:", text, re.I):
        kind = "melee"
    else:
        return None
    average, count, size, sign, bonus, damage_type = damage.groups()
    damage_type = damage_type.lower()
    if damage_type not in DAMAGE_TYPES:
        return None
    name = _plain(name_match.group(1)).rstrip(".")
    result = {
        "id": _slug(name), "name": name, "kind": kind, "attack_bonus": int(hit.group(1)),
        "damage": {"average": int(average), "dice_count": int(count), "dice_size": int(size),
                   "bonus": int(bonus or 0) * (-1 if sign == "-" else 1), "type": damage_type},
    }
    reach = re.search(r"reach (\d+) ft", text, re.I)
    ranges = re.search(r"range (\d+)(?:\s*ft\.)?\s*/\s*(\d+) ft", text, re.I)
    if reach:
        result["reach_ft"] = int(reach.group(1))
    if ranges:
        result["normal_range_ft"], result["long_range_ft"] = map(int, ranges.groups())
    return result


def _record(source: dict) -> dict:
    meta = source.get("meta", "")
    size, _, rest = meta.partition(" ")
    creature_type, _, alignment = rest.partition(",")
    hp = source.get("Hit Points", "")
    hit_dice = re.search(r"\(([^)]+)\)", hp)
    action_text = source.get("Actions", "")
    action_paragraphs = re.findall(r"<p>(.*?)</p>", action_text, re.I | re.S)
    attacks = [attack for paragraph in action_paragraphs if (attack := _attack(paragraph)) is not None]
    multiattack = parse_multiattack(action_text, attacks)
    resist, bad_resist = _simple_values(source.get("Damage Resistances"), DAMAGE_TYPES)
    immune, bad_immune = _simple_values(source.get("Damage Immunities"), DAMAGE_TYPES)
    vulnerable, bad_vulnerable = _simple_values(source.get("Damage Vulnerabilities"), DAMAGE_TYPES)
    condition_immune, bad_condition = _simple_values(source.get("Condition Immunities"), CONDITIONS)
    return {
        "id": _slug(source["name"]), "name": source["name"], "ruleset": "2014", "size": size.title(),
        "creature_type": creature_type.strip().split(" ")[0], "alignment": alignment.strip() or None,
        "armor_class": _integer(source.get("Armor Class")), "armor_class_text": source.get("Armor Class"),
        "max_hp": _integer(hp), "hit_points_text": hp, "hit_dice": hit_dice.group(1) if hit_dice else None,
        "speed": _speed(source.get("Speed")), "speed_text": source.get("Speed"),
        "abilities": {key.lower(): _integer(source.get(key)) for key in ("STR", "DEX", "CON", "INT", "WIS", "CHA")},
        "saving_throws": _bonuses(source.get("Saving Throws")), "skills": _bonuses(source.get("Skills")),
        "senses": source.get("Senses"), "languages": source.get("Languages"),
        "damage_resistances": resist, "damage_immunities": immune, "damage_vulnerabilities": vulnerable,
        "condition_immunities": condition_immune,
        "unsupported_defense_text": bad_resist + bad_immune + bad_vulnerable + bad_condition,
        "challenge_rating": (source.get("Challenge") or "").split(" ", 1)[0] or None,
        "attacks": attacks, "multiattack_slots": multiattack["slots"] if multiattack else [],
        "action_names": _names(action_text), "trait_names": _names(source.get("Traits")),
        "reaction_names": _names(source.get("Reactions")), "legendary_action_names": _names(source.get("Legendary Actions")),
        "source_traits": source.get("Traits"), "source_actions": action_text,
        "source_reactions": source.get("Reactions"), "source_legendary_actions": source.get("Legendary Actions"),
        "image_url": source.get("img_url"),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Normalize a 2014 monster JSON export for Iron Pit.")
    parser.add_argument("source", type=Path)
    parser.add_argument("--output", type=Path, default=Path("data/monsters/2014/catalog.json"))
    args = parser.parse_args()
    try:
        catalog = [_record(item) for item in json.loads(args.source.read_text(encoding="utf-8"))]
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(catalog, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"wrote {len(catalog)} monsters to {args.output}")
        return 0
    except Exception as exc:
        logger.exception("2014 monster import failed: %s", exc)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
