from __future__ import annotations

import argparse
import html
import json
import logging
import re
import unicodedata
from pathlib import Path

from import_2014_attack_details import (
    parse_on_hit_control,
    parse_on_hit_save_condition,
    parse_secondary_damage,
    strip_noncombat_attack_residual,
)
from import_2014_charge import parse_charge_profiles
from import_2014_conditional_damage import parse_conditional_replacement_damage
from import_2014_identity import parse_identity
from import_2014_multiattack import parse_multiattack
from import_2014_reactions import parse_parry_ac_bonus
from import_2014_recharge import parse_action_recharges, parse_rest_recharge_actions
from import_2014_weapon_enhancements import parse_named_weapon_enhancement

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
_SIGN = r"[+\-‐‑‒–—−]"
_ROLLED_DAMAGE = re.compile(rf"Hit:\s*(\d+)\s*\((\d+)d(\d+)(?:\s*({_SIGN})\s*(\d+))?\)\s*([A-Za-z]+) damage", re.I)
_FIXED_DAMAGE = re.compile(r"Hit:\s*(\d+)\s+([A-Za-z]+) damage", re.I)
_ALT_DAMAGE = rf"(\d+)\s*\((\d+)d(\d+)(?:\s*({_SIGN})\s*(\d+))?\)\s*([A-Za-z]+) damage"
_TWO_HANDED = re.compile(r"or\s+" + _ALT_DAMAGE + r"\s+(?:if|when) (?:used|wielded) with two hands(?: to make a melee attack)?", re.I)
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


def _action_paragraphs(value: str | None) -> list[str]:
    """Keep unnamed continuation paragraphs with the preceding named action."""
    grouped: list[str] = []
    for paragraph in re.findall(r"<p>(.*?)</p>", value or "", re.I | re.S):
        if re.search(r"<strong>.*?</strong>", paragraph, re.I | re.S):
            grouped.append(paragraph)
        elif grouped:
            grouped[-1] = f"{grouped[-1]} {paragraph}"
    return grouped


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
    negative_signs = {"-", "‐", "‑", "‒", "–", "—", "−"}
    modifier = int(bonus or 0) * (-1 if sign in negative_signs else 1)
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
    name = _plain(name_match.group(1)).rstrip(".")
    extras, residual = parse_secondary_damage(text[damage_match.end():].strip(" ."))
    conditional, residual = parse_conditional_replacement_damage(residual)
    save_effect, residual = parse_on_hit_save_condition(residual)
    control, forbid_grappled, residual = parse_on_hit_control(residual)
    residual = strip_noncombat_attack_residual(residual)
    result = {"id": _slug(name), "name": name, "kind": kind, "attack_bonus": int(hit.group(1)), "damage": damage, "conditional_damage": conditional, "on_hit_damage": extras, "on_hit_save_effect": save_effect, "control_effect": control, "forbid_target_grappled_by_self": forbid_grappled, "source_complete": not dual_mode and not residual, "unsupported_text": residual or ("dual-mode attack requires split" if dual_mode else None)}
    reach = re.search(r"reach (\d+) ft", text, re.I); ranges = re.search(r"range (\d+)(?:\s*ft\.)?\s*/\s*(\d+) ft", text, re.I)
    if reach: result["reach_ft"] = int(reach.group(1))
    if ranges: result["normal_range_ft"], result["long_range_ft"] = map(int, ranges.groups())
    return result


def _clean_residual(value: str) -> str:
    return re.sub(r"^[\s,;]*(?:and\s+)?|[\s,;]+$", "", value, flags=re.I).strip(" .")


def _attacks(paragraph: str) -> list[dict]:
    attack = _attack(paragraph)
    if attack is None: return []
    residual = attack.get("unsupported_text") or ""; base_id = attack["id"]; text = _plain(paragraph)
    enhancement, work_residual = parse_named_weapon_enhancement(text, residual)
    enhancement_damage = _damage(enhancement["damage_groups"]) if enhancement is not None else None
    if enhancement is None or enhancement_damage is None:
        enhancement = None; enhancement_damage = None; work_residual = residual
    variant_rows: list[dict] = []
    two_handed = _TWO_HANDED.search(work_residual)
    if two_handed:
        alt = _damage(two_handed.groups())
        if alt is not None:
            variant_rows.append({**attack, "id": f"{base_id}-two-handed", "kind": "melee", "damage": alt})
            work_residual = _TWO_HANDED.sub("", work_residual, count=1)
    if enhancement is not None and enhancement_damage is not None:
        variant_rows.append({
            **attack,
            "id": f"{base_id}-{enhancement['id_suffix']}",
            "attack_bonus": enhancement["attack_bonus"],
            "damage": enhancement_damage,
        })
    if variant_rows and not _clean_residual(work_residual):
        base = {**attack, "source_complete": True, "unsupported_text": None}
        rows = [base]
        if "normal_range_ft" in base: rows.append({**base, "id": f"{base_id}-ranged", "kind": "ranged"})
        rows.extend({**row, "source_complete": True, "unsupported_text": None} for row in variant_rows)
        return rows
    melee_range = _MELEE_RANGE.search(residual)
    if melee_range and "normal_range_ft" in attack:
        alt = _damage(melee_range.groups()); remainder = _clean_residual(_MELEE_RANGE.sub("", residual))
        if alt and not remainder:
            base = {**attack, "source_complete": True, "unsupported_text": None}
            return [{**base, "id": f"{base_id}-melee", "kind": "melee"}, {**base, "id": f"{base_id}-ranged", "kind": "ranged", "damage": alt}]
    if not re.search(r"Melee or Ranged (?:Weapon|Spell) Attack:", text, re.I) or "normal_range_ft" not in attack: return [attack]
    primary = _primary_damage(text)
    if primary is None: return [attack]
    damage_match, _ = primary
    extras, residual = parse_secondary_damage(text[damage_match.end():].strip(" ."))
    conditional, residual = parse_conditional_replacement_damage(residual)
    save_effect, residual = parse_on_hit_save_condition(residual)
    control, forbid_grappled, residual = parse_on_hit_control(residual)
    residual = strip_noncombat_attack_residual(residual)
    if residual: return [attack]
    shared = {**attack, "conditional_damage": conditional, "on_hit_damage": extras, "on_hit_save_effect": save_effect, "control_effect": control, "forbid_target_grappled_by_self": forbid_grappled, "source_complete": True, "unsupported_text": None}
    return [{**shared, "id": f"{base_id}-melee", "kind": "melee"}, {**shared, "id": f"{base_id}-ranged", "kind": "ranged"}]


def _record(source: dict) -> dict:
    meta = source.get("meta", ""); size, _, _ = meta.partition(" "); creature_type, creature_type_text, creature_subtypes, alignment = parse_identity(meta); hp = source.get("Hit Points", ""); hit_dice = re.search(r"\(([^)]+)\)", hp); action_text = source.get("Actions", ""); reactions_text = source.get("Reactions", ""); challenge_text = source.get("Challenge")
    attacks = [attack for paragraph in _action_paragraphs(action_text) for attack in _attacks(paragraph)]
    for attack_id, profile in parse_charge_profiles(source.get("Traits"), attacks).items(): next(item for item in attacks if item["id"] == attack_id)["charge_profile"] = profile
    multiattack = parse_multiattack(action_text, attacks); resist, bad_resist = _simple_values(source.get("Damage Resistances"), DAMAGE_TYPES); immune, bad_immune = _simple_values(source.get("Damage Immunities"), DAMAGE_TYPES); vulnerable, bad_vulnerable = _simple_values(source.get("Damage Vulnerabilities"), DAMAGE_TYPES); condition_immune, bad_condition = _simple_values(source.get("Condition Immunities"), CONDITIONS)
    return {
        "id": _slug(source["name"]), "name": source["name"], "ruleset": "2014", "size": size.title(),
        "creature_type": creature_type, "creature_type_text": creature_type_text, "creature_subtypes": creature_subtypes,
        "alignment": alignment, "armor_class": _integer(source.get("Armor Class")), "armor_class_text": source.get("Armor Class"),
        "max_hp": _integer(hp), "hit_points_text": hp, "hit_dice": hit_dice.group(1) if hit_dice else None,
        "speed": _speed(source.get("Speed")), "speed_text": source.get("Speed"),
        "abilities": {key.lower(): _integer(source.get(key)) for key in ("STR", "DEX", "CON", "INT", "WIS", "CHA")},
        "saving_throws": _bonuses(source.get("Saving Throws")), "saving_throws_text": source.get("Saving Throws"),
        "skills": _bonuses(source.get("Skills")), "skills_text": source.get("Skills"), "senses": source.get("Senses"), "languages": source.get("Languages"),
        "damage_resistances": resist, "damage_resistances_text": source.get("Damage Resistances"),
        "damage_immunities": immune, "damage_immunities_text": source.get("Damage Immunities"),
        "damage_vulnerabilities": vulnerable, "damage_vulnerabilities_text": source.get("Damage Vulnerabilities"),
        "condition_immunities": condition_immune, "condition_immunities_text": source.get("Condition Immunities"),
        "unsupported_defense_text": bad_resist + bad_immune + bad_vulnerable + bad_condition,
        "challenge_rating": (challenge_text or "").split(" ", 1)[0] or None, "challenge_text": challenge_text,
        "attacks": attacks, "multiattack_slots": multiattack["slots"] if multiattack else [],
        "action_recharges": parse_action_recharges(action_text), "rest_recharge_action_ids": parse_rest_recharge_actions(action_text),
        "action_names": _names(action_text), "trait_names": _names(source.get("Traits")), "reaction_names": _names(reactions_text),
        "parry_ac_bonus": parse_parry_ac_bonus(reactions_text), "legendary_action_names": _names(source.get("Legendary Actions")),
        "source_traits": source.get("Traits"), "source_actions": action_text, "source_reactions": reactions_text,
        "source_legendary_actions": source.get("Legendary Actions"), "image_url": source.get("img_url"),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Normalize a 2014 monster JSON export for Iron Pit."); parser.add_argument("source", type=Path); parser.add_argument("--output", type=Path, default=Path("data/monsters/2014/catalog.json")); args = parser.parse_args()
    try:
        catalog = [_record(item) for item in json.loads(args.source.read_text(encoding="utf-8"))]; args.output.parent.mkdir(parents=True, exist_ok=True); args.output.write_text(json.dumps(catalog, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"); print(f"wrote {len(catalog)} monsters to {args.output}"); return 0
    except Exception as exc: logger.exception("2014 monster import failed: %s", exc); return 1


if __name__ == "__main__": raise SystemExit(main())