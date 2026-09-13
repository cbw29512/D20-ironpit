from __future__ import annotations

import html
import re


_SIZE = r"(Tiny|Small|Medium|Large|Huge)"
_ABILITY = r"(Strength|Dexterity|Constitution|Intelligence|Wisdom|Charisma)"


def _plain(value: str | None) -> str:
    text = re.sub(r"<[^>]+>", " ", value or "")
    return re.sub(r"\s+", " ", html.unescape(text).replace("\u00ad", "")).strip()


def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def _common(text: str) -> dict | None:
    acid = re.search(
        r"takes \d+ \((\d+)d(\d+)(?:\s*([+-])\s*(\d+))?\) acid damage at the start of each of the .*? turns",
        text, re.I,
    )
    release = re.search(
        r"dies, .*?swallowed creature.*?escape from the corpse (?:using|by using) (\d+) feet of movement, exiting prone",
        text, re.I,
    )
    if acid is None or release is None:
        return None
    if not re.search(r"blinded and restrained", text, re.I):
        return None
    if not re.search(r"total cover against attacks and other effects outside", text, re.I):
        return None
    count, size, sign, bonus = acid.groups()
    modifier = int(bonus or 0) * (-1 if sign == "-" else 1)
    row = {
        "damage_dice_count": int(count), "damage_dice_size": int(size),
        "damage_bonus": modifier, "damage_type": "acid",
        "exit_movement_ft": int(release.group(1)), "exit_prone": True,
    }
    threshold = re.search(
        r"takes (\d+) damage or more (?:on|in) (?:a|one) (?:single )?turn from a creature inside.*?DC (\d+) Constitution saving throw.*?regurgitate.*?within (\d+) feet",
        text, re.I,
    )
    if threshold:
        row.update(
            regurgitate_damage_threshold=int(threshold.group(1)),
            regurgitate_save_dc=int(threshold.group(2)),
            regurgitate_exit_radius_ft=int(threshold.group(3)),
        )
    if re.search(r"(?:becomes|is knocked) prone.*?regurgitat", text, re.I):
        row["regurgitate_on_prone"] = True
    return row


def _standalone(text: str) -> tuple[str, str, str, int | None] | None:
    opener = re.search(
        rf"makes one ([A-Za-z' -]+) attack against a {_SIZE} or smaller target it is grappling",
        text, re.I,
    )
    if opener is None or not re.search(r"the target is swallowed, and the grapple ends", text, re.I):
        return None
    capacity = 1 if re.search(r"can have only (?:one|1) (?:creature|target) swallowed at a time", text, re.I) else None
    return _slug(opener.group(1)), opener.group(2).lower(), "grappled_action", capacity


def _failed_save(text: str, heading: str) -> tuple[str, str, str, int | None, str, int] | None:
    match = re.search(
        rf"target is a {_SIZE} or smaller creature.*?DC (\d+) {_ABILITY} saving throw or be swallowed",
        text, re.I,
    )
    if match is None:
        return None
    size, dc, ability = match.groups()
    return _slug(heading), size.lower(), "hit_failed_save", None, ability.lower(), int(dc)


def _grappled_hit(text: str, heading: str) -> tuple[str, str, str, int | None] | None:
    match = re.search(
        rf"target is a {_SIZE} or smaller creature grappled by .*?that creature is swallowed, and the grapple ends",
        text, re.I,
    )
    if match is None:
        return None
    return _slug(heading), match.group(1).lower(), "hit_grappled", None


def parse_swallow_action(paragraph: str) -> dict | None:
    """Normalize the 2014 standalone and on-hit Swallow shapes into shared data."""
    heading_match = re.search(r"<strong>(.*?)</strong>", paragraph, re.I | re.S)
    if heading_match is None:
        return None
    heading = _plain(heading_match.group(1)).rstrip(".")
    text = _plain(paragraph)
    common = _common(text)
    if common is None:
        return None
    parsed = _standalone(text) if heading.lower() == "swallow" else None
    save = _failed_save(text, heading) if parsed is None else None
    grappled = _grappled_hit(text, heading) if parsed is None and save is None else None
    if parsed is None and save is None and grappled is None:
        return None
    result = save or grappled or parsed
    attack_id, max_size, trigger, max_swallowed = result[:4]
    row = {
        "id": "swallow", "name": "Swallow", "attack_id": attack_id,
        "max_target_size": max_size, "trigger": trigger, "max_swallowed": max_swallowed,
        **common,
    }
    if save is not None:
        row["save_ability"] = save[4]; row["save_dc"] = save[5]
    return row
