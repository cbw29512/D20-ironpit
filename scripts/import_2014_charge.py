from __future__ import annotations

import html
import re


def _plain(value: str | None) -> str:
    text = re.sub(r"<[^>]+>", " ", value or "")
    return re.sub(r"\s+", " ", html.unescape(text)).strip()


def _key(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", value.lower()).rstrip("s")


def _attack(attacks: list[dict], name: str) -> dict | None:
    return next((item for item in attacks if _key(item["name"]) == _key(name)), None)


def _standard_charge(text: str, attacks: list[dict]) -> dict[str, dict]:
    pattern = re.compile(
        r"moves at least (\d+) feet straight toward a target and then hits it with (?:a|an) "
        r"([A-Za-z' -]+?) attack on the same turn, the target takes an extra "
        r"\d+ \((\d+)d(\d+)(?:\s*([+\-−])\s*(\d+))?\)(?: ([A-Za-z]+))? damage",
        re.I,
    )
    match = pattern.search(text)
    if match is None: return {}
    move, attack_name, count, size, sign, bonus, damage_type = match.groups(); attack = _attack(attacks, attack_name)
    if attack is None: return {}
    dtype = (damage_type or attack["damage"]["type"]).lower(); modifier = int(bonus or 0) * (-1 if sign in {"-", "−"} else 1)
    profile: dict = {"minimum_move_ft": int(move), "bonus_damage": {"dice_count": int(count), "dice_size": int(size), "damage_type": dtype, "damage_bonus": modifier}}
    save = re.search(r"DC (\d+) Strength saving throw or be knocked prone", text, re.I)
    if save: profile.update({"prone_save_ability": "strength", "prone_save_dc": int(save.group(1))})
    return {attack["id"]: profile}


def _pounce_or_trample(text: str, attacks: list[dict]) -> dict[str, dict]:
    pattern = re.compile(
        r"moves at least (\d+) feet straight toward (?:a creature|a target|a creature or object) and then hits it with (?:a|an) "
        r"([A-Za-z' -]+?) attack on the same turn, (?:that target|the target) must succeed on a DC (\d+) Strength saving throw or be knocked prone",
        re.I,
    )
    match = pattern.search(text)
    if match is None: return {}
    move, attack_name, dc = match.groups(); attack = _attack(attacks, attack_name)
    if attack is None: return {}
    profile: dict = {"minimum_move_ft": int(move), "prone_save_ability": "strength", "prone_save_dc": int(dc)}
    follow = re.search(r"If (?:the|that) target is prone, [^.]+ can make one ([A-Za-z' -]+?) attack against it as a bonus action", text, re.I)
    if follow:
        follow_attack = _attack(attacks, follow.group(1))
        if follow_attack is not None: profile["follow_up_attack_id"] = follow_attack["id"]
    return {attack["id"]: profile}


def parse_charge_profiles(source_traits: str | None, attacks: list[dict]) -> dict[str, dict]:
    text = _plain(source_traits)
    if re.search(r"\b(?:Pounce|Trampling Charge)\b", text, re.I):
        profile = _pounce_or_trample(text, attacks)
        if profile: return profile
    if re.search(r"\bCharge\b", text, re.I):
        return _standard_charge(text, attacks)
    return {}
