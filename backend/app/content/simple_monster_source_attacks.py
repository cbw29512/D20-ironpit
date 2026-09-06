from __future__ import annotations

import logging
import re

from app.content.monster_combat_scope import base_feature_name, feature_blocks, strip_post_combat_outcomes
from app.content.monster_trait_source_audit import parse_trait_names
from app.content.simple_monster_source_riders import parse_hit_riders

logger = logging.getLogger(__name__)
_NUMBER = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6}
_DAMAGE = r"Hit:\s*\d+\s*\(\s*(\d+)d(\d+)(?:\s*([+-])\s*(\d+))?\s*\)\s*([A-Za-z]+)\s+damage"
_ATTACK = re.compile(rf"\b(Melee|Ranged) Attack Roll:\s*([+-]?\d+)(?:\s*\([^)]*\))?,\s*(?:(?:reach\s+(\d+)\s*ft\.?)|(?:range\s+(\d+)\s*/\s*(\d+)\s*ft\.?))\s*{_DAMAGE}", re.I)
_HYBRID = re.compile(rf"\bMelee or Ranged Attack Roll:\s*([+-]?\d+)(?:\s*\([^)]*\))?,\s*reach\s+(\d+)\s*ft\.?\s+or\s+range\s+(\d+)\s*/\s*(\d+)\s*ft\.?\s*{_DAMAGE}", re.I)
_EXTRA_DICE = re.compile(r"\bplus\s+\d+\s*\(\s*(\d+)d(\d+)(?:\s*([+-])\s*(\d+))?\s*\)\s*([A-Za-z]+)\s+damage", re.I)
_EXTRA_FIXED = re.compile(r"\bplus\s+(\d+)\s+([A-Za-z]+)\s+damage\b", re.I)
_GRAPPLE_ADV = re.compile(r"\bwith Advantage if the target is Grappled by the [^)]+", re.I)
_GRAPPLE_REPLACEMENT = re.compile(
    r"\bor\s+\d+\s*\(\s*(\d+)d(\d+)(?:\s*([+-])\s*(\d+))?\s*\)\s*([A-Za-z]+)\s+damage\s+"
    r"if\s+the\s+target\s+is\s+Grappled\s+by\s+the\s+[A-Za-z][A-Za-z'’ -]*", re.I,
)
_REPLACE_ATTACK = re.compile(r"\bcan replace one attack with a (?P<name>[A-Z][A-Za-z’'\- ]+?) attack\.", re.I)
_COUNT = r"one|two|three|four|five|six|\d+"
_SIMPLE_MULTI_CHOICE = re.compile(
    rf"\bmakes\s+({_COUNT})\s+([A-Z][A-Za-z’'\-]*(?:\s+[A-Z][A-Za-z’'\-]*)?(?:\s+or\s+[A-Z][A-Za-z’'\-]*(?:\s+[A-Z][A-Za-z’'\-]*)?)+)\s+attacks?\b",
    re.I,
)


def _slug(value: str) -> str: return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
def _number(value: str) -> int: return _NUMBER.get(value.lower(), int(value) if value.isdigit() else 0)

def _dice(count: str, size: str, sign: str | None, bonus: str | None) -> dict[str, int]:
    return {"count": int(count), "size": int(size), "bonus": int(bonus or 0) * (-1 if sign == "-" else 1)}


def _effects(block: str, base_span: tuple[int, int], heading: str) -> list[dict[str, object]]:
    extras = list(_EXTRA_DICE.finditer(block)); effects: list[dict[str, object]] = []
    for extra in extras:
        count, size, sign, bonus, damage_type = extra.groups()
        effects.append({"kind": "damage", "source": heading, "dice": _dice(count, size, sign, bonus), "damage_type": damage_type.lower()})
    replacement = _GRAPPLE_REPLACEMENT.search(block)
    if replacement:
        count, size, sign, bonus, damage_type = replacement.groups()
        effects.append({
            "kind": "damage", "source": heading, "dice": _dice(count, size, sign, bonus),
            "damage_type": damage_type.lower(), "trigger": "target_grappled_by_self", "mode": "replace_weapon",
        })
    spans = [base_span, *[item.span() for item in extras]]
    for extra in _EXTRA_FIXED.finditer(block):
        if any(start <= extra.start() < end for start, end in spans): continue
        amount, damage_type = extra.groups()
        effects.append({"kind": "damage", "source": heading, "dice": {"count": 0, "size": 6, "bonus": int(amount)}, "damage_type": damage_type.lower()})
    effects.extend(parse_hit_riders(block)); return effects


def _entry(monster_slug: str, heading: str, mode: str, bonus: str, reach: str | None, normal: str | None,
           long: str | None, count: str, size: str, sign: str | None, damage_bonus: str | None,
           damage_type: str, effects: list[dict[str, object]], *, hybrid: bool = False) -> dict[str, object]:
    suffix = f"-{mode}" if hybrid else ""; attack_id = f"srd-{monster_slug}-{_slug(heading)}{suffix}"
    attack: dict[str, object] = {
        "id": attack_id, "name": heading, "weapon_id": f"{attack_id}-weapon", "attack_kind": mode,
        "attack_bonus": int(bonus), "damage": _dice(count, size, sign, damage_bonus),
        "damage_type": damage_type.lower(), "animation": "projectile" if mode == "ranged" else "strike",
        "reach_ft": int(reach or 5), "effects": effects,
    }
    if normal: attack.update({"normal_range_ft": int(normal), "long_range_ft": int(long), "projectile": _slug(heading)})
    return attack


def parse_simple_attacks(row: dict[str, object]) -> tuple[list[dict[str, object]], dict[str, object] | None]:
    try:
        source = strip_post_combat_outcomes(row.get("actions", "")); headings = parse_trait_names(source, preserve_annotations=True)
        blocks = feature_blocks(source, headings); monster_slug = _slug(str(row["name"])); attacks = []
        by_name: dict[str, list[str]] = {}
        for heading, block in blocks.items():
            if "Attack Roll:" not in block: continue
            hybrid = _HYBRID.search(block)
            if hybrid:
                bonus, reach, normal, long, count, size, sign, damage_bonus, damage_type = hybrid.groups()
                effects = _effects(block, hybrid.span(), heading); built = [
                    _entry(monster_slug, heading, "melee", bonus, reach, None, None, count, size, sign, damage_bonus, damage_type, effects, hybrid=True),
                    _entry(monster_slug, heading, "ranged", bonus, None, normal, long, count, size, sign, damage_bonus, damage_type, effects, hybrid=True),
                ]
            else:
                match = _ATTACK.search(block)
                if match is None: raise ValueError(f"Simple attack parser cannot prove {row['name']} {heading!r}: {block!r}")
                kind, bonus, reach, normal, long, count, size, sign, damage_bonus, damage_type = match.groups()
                built = [_entry(monster_slug, heading, kind.lower(), bonus, reach, normal, long, count, size, sign, damage_bonus, damage_type, _effects(block, match.span(), heading))]
            if _GRAPPLE_ADV.search(block):
                for attack in built: attack["advantage_if_target_grappled_by_self"] = True
            attacks.extend(built); base = base_feature_name(heading)
            if base in by_name: raise ValueError(f"Duplicate base attack heading {base!r} for {row['name']!r}.")
            by_name[base] = [item["id"] for item in built]
        if not attacks: raise ValueError(f"No ordinary attacks parsed for {row['name']!r}.")
        return attacks, _parse_multiattack(row, blocks.get("Multiattack"), by_name)
    except (KeyError, TypeError, ValueError):
        logger.exception("Failed to parse simple source attacks for %r", row.get("name")); raise


def _replacement_ids(source: str, by_name: dict[str, list[str]]) -> list[str]:
    match = _REPLACE_ATTACK.search(source)
    if match is None: return []
    wanted = match.group("name").strip().casefold()
    matches = [ids for name, ids in by_name.items() if name.casefold() == wanted]
    if len(matches) != 1: raise ValueError(f"Replacement attack {match.group('name')!r} did not resolve uniquely.")
    return matches[0]


def _parse_multiattack(row: dict[str, object], source: str | None, by_name: dict[str, list[str]]) -> dict[str, object] | None:
    if source is None: return None
    declared = re.search(rf"\bmakes\s+({_COUNT})\s+attacks?\b", source, re.I)
    choice = re.search(r"\busing\s+(.+?)\s+in\s+any\s+combination\b", source, re.I); slots = []
    simple_choice = _SIMPLE_MULTI_CHOICE.search(source)
    if choice or simple_choice:
        count = declared.group(1) if choice and declared else simple_choice.group(1) if simple_choice else None
        names_source = choice.group(1) if choice else simple_choice.group(2)
        if count is None: raise ValueError(f"Unrecognized Multiattack count for {row['name']!r}: {source!r}")
        names = [item.strip() for item in re.split(r"\s+or\s+|,", names_source) if item.strip()]
        if any(name not in by_name for name in names): raise ValueError(f"Multiattack references an unknown attack for {row['name']!r}.")
        ids = [attack_id for name in names for attack_id in by_name[name]]; slots = [{"attack_ids": ids} for _ in range(_number(count))]
    else:
        parts = re.findall(rf"\b({_COUNT})\s+([A-Z][A-Za-z’'\-]*(?:\s+[A-Z][A-Za-z’'\-]*)?)(?=\s+(?:attacks?\b|and\b|,|$))", source)
        for count, name in parts:
            if name in by_name: slots.extend({"attack_ids": by_name[name]} for _ in range(_number(count)))
        total = _number(declared.group(1)) if declared else sum(_number(count) for count, name in parts if name in by_name)
        if not total or len(slots) != total: raise ValueError(f"Unrecognized fixed Multiattack sequence for {row['name']!r}: {source!r}")
    replacement_ids = _replacement_ids(source, by_name)
    if replacement_ids:
        if not slots: raise ValueError(f"Replacement attack requires a Multiattack slot for {row['name']!r}.")
        slots[0]["attack_ids"] = list(dict.fromkeys([*slots[0]["attack_ids"], *replacement_ids]))
    return {"id": f"srd-{_slug(str(row['name']))}-multiattack", "name": "Multiattack", "is_attack_action": False, "slots": slots}
