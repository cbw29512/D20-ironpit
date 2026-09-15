from __future__ import annotations

import html
import re
import unicodedata

DAMAGE_TYPES = {
    "acid", "bludgeoning", "cold", "fire", "force", "lightning", "necrotic",
    "piercing", "poison", "psychic", "radiant", "slashing", "thunder",
}


def _plain(value: str | None) -> str:
    text = re.sub(r"<[^>]+>", " ", value or "")
    return re.sub(r"\s+", " ", html.unescape(text).replace("\u00ad", "")).strip()


def _slug(value: str) -> str:
    text = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", text).strip("-")


def _damage_types(value: str) -> list[str]:
    words = re.sub(r"\band\b", ",", value, flags=re.I).split(",")
    parsed = [re.sub(r"\s+damage\b", "", item.strip().lower()) for item in words if item.strip()]
    return parsed if parsed and all(item in DAMAGE_TYPES for item in parsed) else []


def _object_stats(text: str) -> tuple[int, int] | None:
    labeled = re.search(r"AC\s*(\d+)[,;)]*\s*(?:hp|hit points)\s*(\d+)", text, re.I)
    if labeled:
        return int(labeled.group(1)), int(labeled.group(2))
    natural = re.search(r"AC\s*(\d+)[,;)]*\s*(\d+)\s+hit points", text, re.I)
    return (int(natural.group(1)), int(natural.group(2))) if natural else None


def parse_breakable_restraint_attack(paragraph: str, recharges: dict[str, int]) -> dict | None:
    """Parse zero-damage attack rolls that apply an escapable, destructible restraint."""
    try:
        heading_match = re.search(r"<strong>(.*?)</strong>", paragraph, re.I | re.S)
        if heading_match is None:
            return None
        heading = _plain(heading_match.group(1)).rstrip(".")
        name = heading.split("(Recharge", 1)[0].strip()
        action_id = _slug(name)
        if action_id not in recharges:
            return None
        text = _plain(paragraph)
        attack = re.search(r"Ranged (?:Weapon|Spell) Attack:\s*([+-]\d+) to hit", text, re.I)
        ranges = re.search(r"range\s+(\d+)\s*/\s*(\d+)\s*ft", text, re.I)
        restrained = re.search(r"Hit:\s*The (?:target|creature) is restrained by ([A-Za-z -]+?)\.", text, re.I)
        escape = re.search(r"DC\s+(\d+)\s+(Strength|Dexterity|Constitution|Intelligence|Wisdom|Charisma) check", text, re.I)
        object_stats = _object_stats(text)
        vulnerable = re.search(r"vulnerabilit(?:y|ies) to ([A-Za-z, ]+?) damage", text, re.I)
        immune = re.search(r"immunit(?:y|ies) to ([A-Za-z, ]+?) damage(?:\.|;|\))", text, re.I)
        destroyed = re.search(r"(?:ends if .*?destroyed|attacked and destroyed)", text, re.I)
        if not all((attack, ranges, restrained, escape, object_stats, vulnerable, immune, destroyed)):
            return None
        vulnerabilities = _damage_types(vulnerable.group(1)); immunities = _damage_types(immune.group(1))
        if not vulnerabilities or not immunities:
            return None
        size_match = re.search(r"one (Tiny|Small|Medium|Large|Huge) or smaller creature", text, re.I)
        escape_dc, escape_ability = escape.groups(); object_ac, object_hp = object_stats
        restraint = {
            "condition_id": "restrained", "escape_ability": escape_ability.lower(), "escape_dc": int(escape_dc),
            "object_ac": object_ac, "object_hp": object_hp,
            "damage_vulnerabilities": vulnerabilities, "damage_immunities": immunities,
        }
        if size_match:
            restraint["max_target_size"] = size_match.group(1).lower()
        normal, long = map(int, ranges.groups())
        return {
            "id": action_id, "name": name, "kind": "ranged", "attack_bonus": int(attack.group(1)),
            "damage": {"average": 0, "dice_count": 0, "dice_size": 6, "bonus": 0, "type": None},
            "conditional_damage": [], "on_hit_damage": [], "on_hit_save_effect": None, "control_effect": None,
            "resource_id": action_id, "resource_cost": 1, "breakable_restraint": restraint,
            "forbid_target_grappled_by_self": False, "normal_range_ft": normal, "long_range_ft": long,
            "source_complete": True, "unsupported_text": None,
        }
    except Exception as exc:
        raise RuntimeError("2014 breakable restraint attack could not be parsed.") from exc
