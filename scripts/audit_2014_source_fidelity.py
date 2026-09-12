from __future__ import annotations

import hashlib
import html
import json
import re
import urllib.request
from pathlib import Path

MANIFEST = Path("data/monsters/2014/source_manifest.json")
CATALOG = Path("data/monsters/2014/catalog.json")
ABILITIES = ("STR", "DEX", "CON", "INT", "WIS", "CHA")


def plain(value: str | None) -> str:
    text = re.sub(r"<[^>]+>", " ", value or "")
    return re.sub(r"\s+", " ", html.unescape(text).replace("\u00ad", "")).strip()


def integer(value: object) -> int:
    match = re.search(r"-?\d+", str(value))
    return int(match.group()) if match else 0


def names(value: str | None) -> list[str]:
    return [plain(item).rstrip(".") for item in re.findall(r"<strong>(.*?)</strong>", value or "", re.I | re.S)]


def speed(value: str | None) -> dict[str, int]:
    return {mode or "walk": int(amount) for mode, amount in re.findall(r"(?:(walk|fly|swim|climb|burrow)\s+)?(\d+)\s*ft\.", (value or "").lower())}


def bonuses(value: str | None) -> dict[str, int]:
    return {name.strip().lower().replace(" ", "_"): int(amount) for name, amount in re.findall(r"([A-Za-z ]+?)\s*([+-]\d+)(?:,|$)", value or "")}


def expected_average(count: int, size: int, bonus: int) -> int:
    return int(count * (size + 1) / 2 + bonus)


def check_damage(monster: dict) -> list[str]:
    errors: list[str] = []
    for attack in monster.get("attacks", []):
        parts = [attack["damage"], *attack.get("on_hit_damage", [])]
        for part in parts:
            count = part["dice_count"]
            if not count:
                continue
            expected = expected_average(count, part["dice_size"], part.get("bonus", 0))
            if part["average"] != expected:
                errors.append(
                    f"{monster['name']} {attack['name']} {part['type']} average {part['average']} != dice average {expected}"
                )
    return errors


def main() -> int:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    with urllib.request.urlopen(manifest["source_raw_url"], timeout=30) as response:
        payload = response.read()
    digest = hashlib.sha256(payload).hexdigest()
    if digest != manifest["sha256"]:
        raise RuntimeError(f"Pinned 2014 source SHA mismatch: {digest}")

    source = json.loads(payload.decode("utf-8"))
    catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
    if len(source) != manifest["monster_count"] or len(catalog) != manifest["monster_count"]:
        raise RuntimeError("2014 source/catalog count mismatch.")

    by_name = {row["name"]: row for row in catalog}
    if len(by_name) != len(catalog):
        raise RuntimeError("Duplicate monster names in normalized 2014 catalog.")
    ids = [row["id"] for row in catalog]
    if len(ids) != len(set(ids)):
        raise RuntimeError("Duplicate monster ids in normalized 2014 catalog.")

    errors: list[str] = []
    for raw in source:
        row = by_name.get(raw["name"])
        if row is None:
            errors.append(f"Missing normalized monster: {raw['name']}")
            continue
        meta = raw.get("meta", "")
        size_name, _, rest = meta.partition(" ")
        type_text, _, alignment = rest.partition(",")
        checks = {
            "size": size_name.title(),
            "alignment": alignment.strip() or None,
            "armor_class": integer(raw.get("Armor Class")),
            "max_hp": integer(raw.get("Hit Points")),
            "speed": speed(raw.get("Speed")),
            "saving_throws": bonuses(raw.get("Saving Throws")),
            "skills": bonuses(raw.get("Skills")),
            "action_names": names(raw.get("Actions")),
            "trait_names": names(raw.get("Traits")),
            "reaction_names": names(raw.get("Reactions")),
            "legendary_action_names": names(raw.get("Legendary Actions")),
        }
        for field, expected in checks.items():
            if row.get(field) != expected:
                errors.append(f"{raw['name']} {field}: {row.get(field)!r} != {expected!r}")
        expected_abilities = {ability.lower(): integer(raw.get(ability)) for ability in ABILITIES}
        if row.get("abilities") != expected_abilities:
            errors.append(f"{raw['name']} ability scores differ from source")
        for target, source_key in (
            ("armor_class_text", "Armor Class"), ("hit_points_text", "Hit Points"),
            ("speed_text", "Speed"), ("senses", "Senses"), ("languages", "Languages"),
            ("source_traits", "Traits"), ("source_actions", "Actions"),
            ("source_reactions", "Reactions"), ("source_legendary_actions", "Legendary Actions"),
        ):
            if (row.get(target) or "") != (raw.get(source_key) or ""):
                errors.append(f"{raw['name']} lost raw source field {source_key}")
        printed_type = type_text.strip()
        stored_type = (row.get("creature_type_text") or row.get("creature_type") or "").strip()
        if printed_type.lower() not in stored_type.lower() and stored_type.lower() not in printed_type.lower():
            errors.append(f"{raw['name']} creature type lost: {printed_type!r} -> {stored_type!r}")
        errors.extend(check_damage(row))

    if errors:
        preview = "\n".join(f"- {item}" for item in errors[:40])
        raise RuntimeError(f"2014 source fidelity audit found {len(errors)} issue(s):\n{preview}")
    print(f"2014 source fidelity audit passed: {len(catalog)}/{manifest['monster_count']} records")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
