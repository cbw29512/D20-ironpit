from __future__ import annotations

import html
import re


_ABILITIES = "Strength|Dexterity|Constitution|Intelligence|Wisdom|Charisma"


def _plain(value: str | None) -> str:
    text = re.sub(r"<[^>]+>", " ", value or "")
    return re.sub(r"\s+", " ", html.unescape(text).replace("\u00ad", "")).strip()


def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def _regurgitation(text: str) -> tuple[int, str, int, int] | None:
    match = re.search(
        rf"takes (\d+) damage or more on a single turn from (?:the swallowed creature|a creature inside it).*?"
        rf"DC (\d+) ({_ABILITIES}) saving throw at the end of that turn or regurgitate .*?within (\d+) feet",
        text, re.I,
    )
    if match is None:
        return None
    threshold, dc, ability, release_range = match.groups()
    return int(threshold), ability.lower(), int(dc), int(release_range)


def _shared_swallow_data(text: str) -> dict | None:
    acid = re.search(
        r"takes \d+ \((\d+)d(\d+)(?:\s*([+-])\s*(\d+))?\) acid damage at the start of each of the [A-Za-z' -]+['’]s turns",
        text, re.I,
    )
    capacity = re.search(r"can have only (?:one|1) (?:creature|target) swallowed at a time", text, re.I)
    release = re.search(
        r"If the [A-Za-z' -]+ dies, a swallowed creature is no longer restrained by it and can escape from the corpse (?:by )?using (\d+) feet of movement, exiting prone",
        text, re.I,
    )
    regurgitation = _regurgitation(text)
    required = (
        re.search(r"blinded and restrained", text, re.I),
        re.search(r"total cover against attacks and other effects outside", text, re.I),
    )
    if acid is None or release is None or not all(required):
        return None
    count, size, sign, bonus = acid.groups()
    row = {
        "damage_dice_count": int(count), "damage_dice_size": int(size),
        "damage_bonus": int(bonus or 0) * (-1 if sign == "-" else 1), "damage_type": "acid",
        "max_swallowed": 1 if capacity is not None else None,
        "regurgitation_damage_threshold": None, "regurgitation_save_ability": None,
        "regurgitation_save_dc": None, "regurgitation_range_ft": None,
        "exit_movement_ft": int(release.group(1)), "exit_prone": True,
    }
    if regurgitation is not None:
        threshold, ability, dc, release_range = regurgitation
        row.update(
            regurgitation_damage_threshold=threshold, regurgitation_save_ability=ability,
            regurgitation_save_dc=dc, regurgitation_range_ft=release_range,
        )
    return row


def parse_swallow_action(paragraph: str) -> dict | None:
    """Parse the common grapple-then-attack 2014 Swallow action shape."""
    heading = re.search(r"<strong>(.*?)</strong>", paragraph, re.I | re.S)
    if heading is None or _plain(heading.group(1)).rstrip(".").lower() != "swallow":
        return None
    text = _plain(paragraph)
    opener = re.search(
        r"makes one ([A-Za-z' -]+) attack against a (Tiny|Small|Medium|Large|Huge) or smaller (?:target|creature) it is grappling",
        text, re.I,
    )
    shared = _shared_swallow_data(text)
    if opener is None or shared is None or not re.search(
        r"(?:the target|that creature|the creature).*?is swallowed, and the grapple ends", text, re.I,
    ):
        return None
    attack_name, max_size = opener.groups()
    return {
        "id": "swallow", "name": "Swallow", "attack_id": _slug(attack_name),
        "max_target_size": max_size.lower(), "requires_existing_grapple": True, **shared,
    }


def parse_grappled_target_swallow_attack(paragraph: str) -> dict | None:
    """Parse an attack that swallows on hit only when the target is already grappled by the attacker."""
    heading = re.search(r"<strong>(.*?)</strong>", paragraph, re.I | re.S)
    if heading is None:
        return None
    name = _plain(heading.group(1)).rstrip(".")
    if name.lower() == "swallow":
        return None
    text = _plain(paragraph)
    rider = re.search(
        r"If the target is a (Tiny|Small|Medium|Large|Huge) or smaller creature grappled by the [A-Za-z' -]+, "
        r"(?:that creature|the target|it) is swallowed, and the grapple ends",
        text, re.I,
    )
    shared = _shared_swallow_data(text)
    if rider is None or shared is None:
        return None
    return {
        "id": "swallow", "name": "Swallow", "attack_id": _slug(name),
        "max_target_size": rider.group(1).lower(), "requires_existing_grapple": True,
        "_inline_attack": True, **shared,
    }


def parse_on_hit_swallow_attack(paragraph: str) -> dict | None:
    """Parse an ordinary attack whose hit rider swallows on a failed saving throw."""
    heading = re.search(r"<strong>(.*?)</strong>", paragraph, re.I | re.S)
    if heading is None:
        return None
    text = _plain(paragraph)
    rider = re.search(
        rf"If the target is a (Tiny|Small|Medium|Large|Huge) or smaller creature, it must succeed on a DC (\d+) ({_ABILITIES}) saving throw or be swallowed",
        text, re.I,
    )
    shared = _shared_swallow_data(text)
    if rider is None or shared is None:
        return None
    max_size, dc, ability = rider.groups()
    return {
        "id": "swallow", "name": "Swallow", "attack_id": _slug(_plain(heading.group(1)).rstrip(".")),
        "max_target_size": max_size.lower(), "requires_existing_grapple": False,
        "on_hit_save_ability": ability.lower(), "on_hit_save_dc": int(dc), **shared,
    }


def parse_grapple_containment_action(paragraph: str) -> dict | None:
    """Parse direct grapple-based containment with source-turn save-gated damage."""
    heading = re.search(r"<strong>(.*?)</strong>", paragraph, re.I | re.S)
    if heading is None:
        return None
    name = _plain(heading.group(1)).rstrip(".")
    text = _plain(paragraph)
    opener = re.search(
        r"(?:engulfs|envelops) a (Tiny|Small|Medium|Large|Huge|Gargantuan) or smaller creature grappled by it",
        text, re.I,
    )
    save = re.search(rf"DC (\d+) ({_ABILITIES}) saving throw", text, re.I)
    damage = re.search(
        r"(?:failed save[^.]*?|\bor\s+)takes? \d+ \((\d+)d(\d+)(?:\s*([+-])\s*(\d+))?\) ([A-Za-z]+) damage",
        text, re.I,
    )
    source_turn = re.search(r"start of each of (?:the |its )?[A-Za-z' -]+['’]s turns", text, re.I)
    required = (
        re.search(r"blinded", text, re.I), re.search(r"restrained", text, re.I),
        re.search(r"unable to breathe", text, re.I), re.search(r"moves? with (?:it|the [A-Za-z' -]+)", text, re.I),
    )
    if opener is None or save is None or damage is None or source_turn is None or not all(required):
        return None
    count, size, sign, bonus, damage_type = damage.groups()
    capacity = re.search(r"can have only (?:one|1) (?:creature|target) (?:engulfed|enveloped) at a time", text, re.I)
    return {
        "id": _slug(name), "name": name, "attack_id": None,
        "max_target_size": opener.group(1).lower(), "requires_existing_grapple": True,
        "damage_dice_count": int(count), "damage_dice_size": int(size),
        "damage_bonus": int(bonus or 0) * (-1 if sign == "-" else 1), "damage_type": damage_type.lower(),
        "max_swallowed": 1 if capacity is not None else None,
        "start_turn_save_dc": int(save.group(1)), "start_turn_save_ability": save.group(2).lower(),
        "source_death_release": "immediate", "exit_movement_ft": 0, "exit_prone": False,
    }