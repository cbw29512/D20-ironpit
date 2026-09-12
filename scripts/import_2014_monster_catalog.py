from __future__ import annotations

import argparse
import html
import json
import logging
import re
import unicodedata
from pathlib import Path

from import_2014_attack_details import parse_on_hit_control, parse_on_hit_save_condition, parse_secondary_damage
from import_2014_charge import parse_charge_profiles
from import_2014_multiattack import parse_multiattack
from import_2014_reactions import parse_parry_ac_bonus

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
_ROLLED_DAMAGE = re.compile(r"Hit:\s*(\d+)\s*\((\d+)d(\d+)(?:\s*([+\-−])\s*(\d+))?\)\s*([A-Za-z]+) damage", re.I)
_FIXED_DAMAGE = re.compile(r"Hit:\s*(\d+)\s+([A-Za-z]+) damage", re.I)
_ALT_DAMAGE = r"(\d+)\s*\((\d+)d(\d+)(?:\s*([+\-−])\s*(\d+))?\)\s*([A-Za-z]+) damage"
_TWO_HANDED = re.compile(r"or\s+" + _ALT_DAMAGE + r"\s+if used with two hands to make a melee attack", re.I)
_MELEE_RANGE = re.compile(r"in melee or\s+" + _ALT_DAMAGE + r"\s+at range", re.I)


def _slug(value: str) -> str:
    text = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", text).strip("-")


def _plain(value: str | None) -> str:
    text = re.sub(r"<[^>]+>", " ", value or ""); text = re.sub(r"\s+", " ", html.unescape(text).replace("\u00ad", "")).strip()
    return re.sub(r"\s+:", ":", text)


def _integer(value: object) -> int:
    match = re.search(r"-?\d+", str(value)); return int(match.group()) if match else 0


def _names(value: str | None) -> list[str]:
    return [_plain(item).rstrip(".") for item in re.findall(r"<strong>(.*?)</strong>", value or "", re.I | re.S)]


def _speed(value: str | None) -> dict[str, int]:
    return {mode or "walk": int(amount) for mode, amount in re.findall(r"(?:(walk|fly|swim|climb|burrow)\s+)?(\d+)\s*ft\.", (value or "").lower())}


def _bonuses(value: str | None) -> dict[str, int]:
    return {name.strip().lower().replace(" ", "_"): int(amount) for name, amount in re.findall(r"([A-Za-z ]+?)\s*([+-]\d+)(?:,|$)", value or "")}


def _simple_values(value: str | None, allowed: set[str]) -> tuple[list[str], list[str]]:
    text = _plain(value).lower(); simple: list[str] = []; unsupported: list[str] = []
    for clause in [item.strip().rstrip(".") for item in text.split(";") if item.strip()]:
        parts = [part.strip() for part in clause.split(",") if part.strip()]
        if parts and all(part in allowed for part in parts): simple.extend(parts)
        elif clause in allowed: simple.append(clause)
        else: unsupported.append(clause)
    return simple, unsupported


def _damage(groups: tuple[str | None, ...]) -> dict | None:
    average, count, size, sign, bonus, damage_type = groups; dtype = (damage_type or "").lower()
    if dtype not in DAMAGE_TYPES: return None
    modifier = int(bonus or 0) * (-1 if sign in {"-", "−"} else 1)
    return {"average": int(average), "dice_count": int(count), "dice_size": int(size), "bonus": modifier, "type": dtype}


def _primary_damage(text: str) -> tuple[re.Match[str], dict] | None:
    rolled = _ROLLED_DAMAGE.search(text)
    if rolled:
        parsed = _damage(rolled.groups())
        return (rolled, parsed) if parsed else None
    fixed = _FIXED_DAMAGE.search(text)
    if fixed:
        amount, damage_type = fixed.groups(); damage_type = damage_type.lower()
        if damage_type not in DAMAGE_TYPES: return None
        return fixed, {"average": int(amount), "dice_count": 0, "dice_size": 6, "bonus": 0, "type": damage_type}
    return None


def _attack(paragraph: str) -> dict | None:
    text = _plain(paragraph); name_match = re.search(r"<strong>(.*?)</strong>", paragraph, re.I | re.S); hit = re.search(r"([+-]\d+) to hit", text, re.I); primary = _primary_damage(text)
    if not name_match or not hit or primary is None: return None
    damage_match, damage = primary; dual_mode = bool(re.search(r"Melee or Ranged (?:Weapon|Spell) Attack:", text, re.I))
    if re.search(r"Ranged (?:Weapon|Spell) Attack:", text, re.I) and not dual_mode: kind = "ranged"
    elif re.search(r"Melee(?: or Ranged)? (?:Weapon|Spell) Attack:", text, re.I): kind = "melee"
    else: return None
    name = _plain(name_match.group(1)).rstrip("."); extras, residual = parse_secondary_damage(text[damage_match.end():].strip(" .")); save_effect, residual = parse_on_hit_save_condition(residual); control, forbid_grappled, residual = parse_on_hit_control(residual)
    result = {"id": _slug(name), "name": name, "kind": kind, "attack_bonus": int(hit.group(1)), "damage": damage, "on_hit_damage": extras, "on_hit_save_effect": save_effect, "control_effect": control, "forbid_target_grappled_by_self": forbid_grappled, "source_complete": not dual_mode and not residual, "unsupported_text": residual or ("dual-mode attack requires split" if dual_mode else None)}
    reach = re.search(r"reach (\d+) ft", text, re.I); ranges = re.search(r"range (\d+)(?:\s*ft\.)?\s*/\s*(\d+) ft", text, re.I)
    if reach: result["reach_ft"] = int(reach.group(1))
    if ranges: result["normal_range_ft"], result["long_range_ft"] = map(int, ranges.groups())
    return result


def _clean_residual(value: str) -> str:
    return re.sub(r"^[\s,;]*(?:and\s+)?|[\s,;]+$", "", value, flags=re.I).strip(" .")


def _attacks(paragraph: str) -> list[dict]:
    attack = _attack(paragraph)
    if attack is None: return []
    residual = attack.get("unsupported_text") or ""; base_id = attack["id"]
    two_handed = _TWO_HANDED.search(residual)
    if two_handed:
        alt = _damage(two_handed.groups()); remainder = _clean_residual(_TWO_HANDED.sub("", residual))
        if alt and not remainder:
            base = {**attack, "source_complete": True, "unsupported_text": None}
            rows = [base]
            if "normal_range_ft" in base: rows.append({**base, "id": f"{base_id}-ranged", "kind": "ranged"})
            rows.append({**base, "id": f"{base_id}-two-handed", "kind": "melee", "damage": alt})
            return rows
    melee_range = _MELEE_RANGE.search(residual)
    if melee_range and "normal_range_ft" in attack:
        alt = _damage(melee_range.groups()); remainder = _clean_residual(_MELEE_RANGE.sub("", residual))
        if alt and not remainder:
            base = {**attack, "source_complete": True, "unsupported_text": None}
            return [{**base, "id": f"{base_id}-melee", "kind": "melee"}, {**base, "id": f"{base_id}-ranged", "kind": "ranged", "damage": alt}]
    text = _plain(paragraph)
    if not re.search(r"Melee or Ranged (?:Weapon|Spell) Attack:", text, re.I) or "normal_range_ft" not in attack: return [attack]
    primary = _primary_damage(text)
    if primary is None: return [attack]
    damage_match, _ = primary; extras, residual = parse_secondary_damage(text[damage_match.end():].strip(" .")); save_effect, residual = parse_on_hit_save_condition(residual); control, forbid_grappled, residual = parse_on_hit_control(residual)
    if residual: return [attack]
    shared = {**attack, "on_hit_damage": extras, "on_hit_save_effect": save_effect, "control_effect": control, "forbid_target_grappled_by_self": forbid_grappled, "source_complete": True, "unsupported_text": None}
    return [{**shared, "id": f"{base_id}-melee", "kind": "melee"}, {**shared, "id": f"{base_id}-ranged", "kind": "ranged"}]


def _record(source: dict) -> dict:
    meta = source.get("meta", ""); size, _, rest = meta.partition(" "); creature_type, _, alignment = rest.partition(","); hp = source.get("Hit Points", ""); hit_dice = re.search(r"\(([^)]+)\)", hp); action_text = source.get("Actions", ""); reactions_text = source.get("Reactions", "")
    attacks = [attack for paragraph in re.findall(r"<p>(.*?)</p>", action_text, re.I | re.S) for attack in _attacks(paragraph)]
    for attack_id, profile in parse_charge_profiles(source.get("Traits"), attacks).items(): next(item for item in attacks if item["id"] == attack_id)["charge_profile"] = profile
    multiattack = parse_multiattack(action_text, attacks); resist, bad_resist = _simple_values(source.get("Damage Resistances"), DAMAGE_TYPES); immune, bad_immune = _simple_values(source.get("Damage Immunities"), DAMAGE_TYPES); vulnerable, bad_vulnerable = _simple_values(source.get("Damage Vulnerabilities"), DAMAGE_TYPES); condition_immune, bad_condition = _simple_values(source.get("Condition Immunities"), CONDITIONS)
    return {"id": _slug(source["name"]), "name": source["name"], "ruleset": "2014", "size": size.title(), "creature_type": creature_type.strip().split(" ")[0], "alignment": alignment.strip() or None, "armor_class": _integer(source.get("Armor Class")), "armor_class_text": source.get("Armor Class"), "max_hp": _integer(hp), "hit_points_text": hp, "hit_dice": hit_dice.group(1) if hit_dice else None, "speed": _speed(source.get("Speed")), "speed_text": source.get("Speed"), "abilities": {key.lower(): _integer(source.get(key)) for key in ("STR", "DEX", "CON", "INT", "WIS", "CHA")}, "saving_throws": _bonuses(source.get("Saving Throws")), "skills": _bonuses(source.get("Skills")), "senses": source.get("Senses"), "languages": source.get("Languages"), "damage_resistances": resist, "damage_immunities": immune, "damage_vulnerabilities": vulnerable, "condition_immunities": condition_immune, "unsupported_defense_text": bad_resist + bad_immune + bad_vulnerable + bad_condition, "challenge_rating": (source.get("Challenge") or "").split(" ", 1)[0] or None, "attacks": attacks, "multiattack_slots": multiattack["slots"] if multiattack else [], "action_names": _names(action_text), "trait_names": _names(source.get("Traits")), "reaction_names": _names(reactions_text), "parry_ac_bonus": parse_parry_ac_bonus(reactions_text), "legendary_action_names": _names(source.get("Legendary Actions")), "source_traits": source.get("Traits"), "source_actions": action_text, "source_reactions": reactions_text, "source_legendary_actions": source.get("Legendary Actions"), "image_url": source.get("img_url")}


def main() -> int:
    parser = argparse.ArgumentParser(description="Normalize a 2014 monster JSON export for Iron Pit."); parser.add_argument("source", type=Path); parser.add_argument("--output", type=Path, default=Path("data/monsters/2014/catalog.json")); args = parser.parse_args()
    try:
        catalog = [_record(item) for item in json.loads(args.source.read_text(encoding="utf-8"))]; args.output.parent.mkdir(parents=True, exist_ok=True); args.output.write_text(json.dumps(catalog, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"); print(f"wrote {len(catalog)} monsters to {args.output}"); return 0
    except Exception as exc: logger.exception("2014 monster import failed: %s", exc); return 1


if __name__ == "__main__": raise SystemExit(main())