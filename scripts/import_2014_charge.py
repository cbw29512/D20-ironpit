from __future__ import annotations

import html
import re


def _plain(value: str | None) -> str:
    text = re.sub(r"<[^>]+>", " ", value or "")
    return re.sub(r"\s+", " ", html.unescape(text)).strip()


def _key(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", value.lower()).rstrip("s")


def parse_charge_profiles(source_traits: str | None, attacks: list[dict]) -> dict[str, dict]:
    text = _plain(source_traits)
    if not re.search(r"\bCharge\b", text, re.I):
        return {}
    pattern = re.compile(
        r"moves at least (\d+) feet straight toward a target and then hits it with (?:a|an) "
        r"([A-Za-z' -]+?) attack on the same turn, the target takes an extra "
        r"\d+ \((\d+)d(\d+)(?:\s*([+\-−])\s*(\d+))?\)(?: ([A-Za-z]+))? damage",
        re.I,
    )
    match = pattern.search(text)
    if match is None:
        return {}
    move, attack_name, count, size, sign, bonus, damage_type = match.groups()
    attack = next((item for item in attacks if _key(item["name"]) == _key(attack_name)), None)
    if attack is None:
        return {}
    dtype = (damage_type or attack["damage"]["type"]).lower()
    modifier = int(bonus or 0) * (-1 if sign in {"-", "−"} else 1)
    profile: dict = {
        "minimum_move_ft": int(move),
        "bonus_damage": {
            "dice_count": int(count), "dice_size": int(size),
            "damage_type": dtype, "damage_bonus": modifier,
        },
    }
    save = re.search(r"DC (\d+) Strength saving throw or be knocked prone", text, re.I)
    if save:
        profile.update({"prone_save_ability": "strength", "prone_save_dc": int(save.group(1))})
    return {attack["id"]: profile}
