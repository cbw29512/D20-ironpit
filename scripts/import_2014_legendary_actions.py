from __future__ import annotations

import html
import re
import unicodedata

_USES = re.compile(r"can take (\d+) legendary actions", re.I)
_HEADING = re.compile(r"<strong>(.*?)</strong>", re.I | re.S)
_WING = re.compile(
    r"Each creature within (\d+) feet .*?DC (\d+) Dexterity saving throw or take "
    r"\d+ \((\d+)d(\d+)(?:\s*\+\s*(\d+))?\) bludgeoning damage and be knocked prone",
    re.I,
)


def _plain(value: str) -> str:
    text = re.sub(r"<[^>]+>", " ", value)
    return re.sub(r"\s+", " ", html.unescape(text)).strip()


def _slug(value: str) -> str:
    text = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", text).strip("-")


def _name_cost(heading: str) -> tuple[str, int]:
    clean = _plain(heading).rstrip(".")
    cost = re.search(r"\(Costs? (\d+) Actions?\)", clean, re.I)
    name = re.sub(r"\s*\(Costs? \d+ Actions?\)\s*", "", clean, flags=re.I).strip()
    return name, int(cost.group(1)) if cost else 1


def _attack_id(name: str, text: str, attacks: list[dict]) -> str | None:
    match = re.search(r"makes an? ([A-Za-z' -]+) attack", text, re.I)
    if not match:
        return None
    wanted = _slug(match.group(1))
    by_id = {attack["id"]: attack for attack in attacks}
    if wanted in by_id:
        return wanted
    candidates = [attack["id"] for attack in attacks if _slug(attack["name"]) == wanted]
    return candidates[0] if len(candidates) == 1 else None


def _wing(name: str, cost: int, text: str) -> dict | None:
    if name.lower() != "wing attack":
        return None
    match = _WING.search(text)
    if not match:
        return None
    radius, dc, count, size, bonus = match.groups()
    save = {
        "id": "legendary-wing-attack", "name": "Wing Attack",
        "save_ability": "dexterity", "dc": int(dc), "range_ft": int(radius),
        "area": {"shape": "emanation", "origin": "self", "radius_ft": int(radius)},
        "damage_dice_count": int(count), "damage_dice_size": int(size),
        "damage_bonus": int(bonus or 0), "damage_type": "bludgeoning", "success_damage": "none",
        "failure_control_effect": {"condition_id": "prone"}, "animation": "wing-attack",
    }
    return {"id": "wing-attack", "name": name, "cost": cost, "kind": "save", "save_action": save}


def parse_legendary_actions(source_html: str | None, attacks: list[dict]) -> tuple[int, list[dict], list[str]]:
    raw = source_html or ""
    if not raw.strip():
        return 0, [], []
    use_match = _USES.search(_plain(raw))
    if use_match is None:
        return 0, [], ["legendary-action-uses"]
    options: list[dict] = []
    unsupported: list[str] = []
    paragraphs = re.findall(r"<p>(.*?)</p>", raw, re.I | re.S)
    for paragraph in paragraphs:
        heading = _HEADING.search(paragraph)
        if heading is None:
            continue
        name, cost = _name_cost(heading.group(1)); text = _plain(paragraph)
        if name.lower() == "detect" and re.search(r"Wisdom \(Perception\) check", text, re.I):
            options.append({"id": "detect", "name": name, "cost": cost, "kind": "ability_check", "check_ability": "wisdom", "check_skill": "perception"})
            continue
        attack_id = _attack_id(name, text, attacks)
        if attack_id is not None:
            options.append({"id": _slug(name), "name": name, "cost": cost, "kind": "attack", "attack_id": attack_id})
            continue
        wing = _wing(name, cost, text)
        if wing is not None:
            options.append(wing); continue
        unsupported.append(name)
    return int(use_match.group(1)), options, unsupported
