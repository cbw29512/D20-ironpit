from __future__ import annotations

import html
import re


def _plain(value: str | None) -> str:
    text = re.sub(r"<[^>]+>", " ", value or "")
    return re.sub(r"\s+", " ", html.unescape(text).replace("\u00ad", "")).strip()


def parse_swallow_action(paragraph: str) -> dict | None:
    """Parse the common 2014 attack-to-swallow action shape into shared data."""
    heading = re.search(r"<strong>(.*?)</strong>", paragraph, re.I | re.S)
    if heading is None or _plain(heading.group(1)).rstrip(".").lower() != "swallow":
        return None
    text = _plain(paragraph)
    opener = re.search(
        r"makes one ([A-Za-z' -]+) attack against a (Tiny|Small|Medium|Large|Huge) or smaller target it is grappling",
        text, re.I,
    )
    acid = re.search(
        r"takes \d+ \((\d+)d(\d+)(?:\s*([+-])\s*(\d+))?\) acid damage at the start of each of the [A-Za-z' -]+['’]s turns",
        text, re.I,
    )
    capacity = re.search(r"can have only (?:one|1) (?:creature|target) swallowed at a time", text, re.I)
    release = re.search(
        r"If the [A-Za-z' -]+ dies, a swallowed creature is no longer restrained by it and can escape from the corpse using (\d+) feet of movement, exiting prone",
        text, re.I,
    )
    required = (
        re.search(r"the target is swallowed, and the grapple ends", text, re.I),
        re.search(r"blinded and restrained", text, re.I),
        re.search(r"total cover against attacks and other effects outside", text, re.I),
    )
    if opener is None or acid is None or capacity is None or release is None or not all(required):
        return None
    attack_name, max_size = opener.groups(); count, size, sign, bonus = acid.groups()
    modifier = int(bonus or 0) * (-1 if sign == "-" else 1)
    attack_id = re.sub(r"[^a-z0-9]+", "-", attack_name.lower()).strip("-")
    return {
        "id": "swallow", "name": "Swallow", "attack_id": attack_id,
        "max_target_size": max_size.lower(), "damage_dice_count": int(count),
        "damage_dice_size": int(size), "damage_bonus": modifier, "damage_type": "acid",
        "max_swallowed": 1, "exit_movement_ft": int(release.group(1)), "exit_prone": True,
    }
