from __future__ import annotations

import html
import re
import unicodedata


def _plain(value: str | None) -> str:
    text = re.sub(r"<[^>]+>", " ", value or "")
    return re.sub(r"\s+", " ", html.unescape(text).replace("\u00ad", "")).strip()


def _slug(value: str) -> str:
    text = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", text).strip("-")


def parse_limited_healing_action(paragraph: str) -> tuple[dict, int] | None:
    """Parse printed X/Day healing actions into the shared HealingAction schema."""
    heading_match = re.search(r"<strong>(.*?)</strong>", paragraph, re.I | re.S)
    if heading_match is None:
        return None
    heading = _plain(heading_match.group(1)).rstrip(".")
    usage = re.search(r"\((\d+)/Day\)$", heading, re.I)
    if usage is None:
        return None
    name = re.sub(r"\s*\(\d+/Day\)$", "", heading, flags=re.I).strip()
    text = _plain(paragraph)
    healing = re.search(
        r"regains\s+\d+\s*\((\d+)d(\d+)\s*([+-]\s*\d+)?\)\s*hit points",
        text, re.I,
    )
    if healing is None:
        return None
    dice_count, dice_size, bonus = healing.groups()
    removable: list[str] = []
    lowered = text.lower()
    if "poison" in lowered: removable.append("poisoned")
    if "blindness" in lowered: removable.append("blinded")
    if "deafness" in lowered: removable.append("deafened")
    target_mode = "other" if re.search(r"touch(?:es)? another creature", text, re.I) else "self_or_ally"
    action_id = _slug(name)
    return ({
        "id": action_id, "name": name, "action_cost": "action", "range_ft": 5,
        "target_mode": target_mode, "dice_count": int(dice_count), "dice_size": int(dice_size),
        "healing_bonus": int((bonus or "0").replace(" ", "")),
        "removable_conditions": removable, "resource_id": action_id, "resource_cost": 1,
        "animation": "healing",
    }, int(usage.group(1)))
