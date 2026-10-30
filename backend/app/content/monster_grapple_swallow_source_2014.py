"""2014 source-verified grapple-then-Swallow actions, without name dispatch."""
from __future__ import annotations

from dataclasses import dataclass
import logging
import re

from app.content.monster_source_2014 import SourceMonster2014
from app.content.monster_source_sections_2014 import source_sections_2014
from app.domain.size import CreatureSize

logger = logging.getLogger(__name__)

_SIMPLE = re.compile(
    r"The (?P<actor>[\w -]+) makes one (?P<attack>[\w -]+) attack against "
    r"a (?P<size>Small|Medium|Large) or smaller target it is grappling\. "
    r"If the attack hits, the target is swallowed, and the grapple ends\. "
    r"The swallowed target is blinded and restrained, it has total cover "
    r"against attacks and other effects outside the (?P=actor), and it takes "
    r"(?P<average>\d+) \((?P<count>\d+)d(?P<sides>\d+)\) "
    r"(?P<type>\w+) damage at the start of each of the (?P=actor)'s turns\. "
    r"The (?P=actor) can have only one target swallowed at a time\. "
    r"If the (?P=actor) dies, a swallowed creature is no longer restrained "
    r"by it and can escape from the corpse using (?P<exit>\d+) feet of "
    r"movement, exiting prone\.",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class GrappleSwallowSource2014:
    source_name: str
    attack_id: str
    max_target_size: CreatureSize
    damage_dice_count: int
    damage_dice_size: int
    damage_type: str
    max_swallowed: int
    exit_movement_ft: int
    regurgitation_damage_threshold: int | None = None
    regurgitation_save_ability: str | None = None
    regurgitation_save_dc: int | None = None
    regurgitation_range_ft: int | None = None
    regurgitation_all_swallowed: bool = False


def _semantic_text(monster: SourceMonster2014) -> str:
    try:
        sections = source_sections_2014(monster.source_actions, include_continuations=True)
        selected = [
            text for heading, text in sections.items()
            if re.search(r"\b(?:swallow(?:s|ed)?|regurgitate)\b", f"{heading} {text}", re.I)
        ]
        return " ".join(" ".join(text.split()) for text in selected)
    except Exception:
        logger.exception("Failed to collect Swallow source text for %s.", monster.id)
        raise


def _attack(monster: SourceMonster2014, attack_name: str):
    try:
        return next(
            (
                item for item in monster.attacks
                if item.name.casefold() == attack_name.casefold() and item.source_complete
            ),
            None,
        )
    except Exception:
        logger.exception("Failed to select Swallow attack for %s.", monster.id)
        raise


def _simple_profile(monster: SourceMonster2014) -> GrappleSwallowSource2014 | None:
    try:
        if len(monster.swallow_actions) != 1:
            return None
        text = source_sections_2014(
            monster.source_actions, include_continuations=True,
        ).get("Swallow", "")
        match = _SIMPLE.fullmatch(text)
        if match is None:
            return None
        groups = match.groupdict()
        actor = monster.name.split()[-1].lower()
        attack = _attack(monster, groups["attack"])
        if groups["actor"].lower() != actor or attack is None:
            return None
        data = monster.swallow_actions[0]
        size = CreatureSize(groups["size"].lower())
        count, sides = int(groups["count"]), int(groups["sides"])
        if int(groups["average"]) != count * (sides + 1) // 2:
            return None
        if not isinstance(data, dict) or not (
            data.get("id") == "swallow"
            and data.get("attack_id") == attack.id
            and data.get("max_target_size") == size.value
            and data.get("requires_existing_grapple") is True
            and data.get("damage_dice_count") == count
            and data.get("damage_dice_size") == sides
            and data.get("damage_bonus") == 0
            and data.get("damage_type") == groups["type"].lower()
            and data.get("max_swallowed") == 1
            and data.get("regurgitation_damage_threshold") is None
            and data.get("exit_movement_ft") == int(groups["exit"])
            and data.get("exit_prone") is True
        ):
            return None
        return GrappleSwallowSource2014(
            "Swallow", attack.id, size, count, sides, groups["type"].lower(),
            1, int(groups["exit"]),
        )
    except Exception:
        logger.exception("Failed simple Swallow source proof for %s.", monster.id)
        raise


def _threshold_profile(monster: SourceMonster2014) -> GrappleSwallowSource2014 | None:
    try:
        text = _semantic_text(monster)
        if not text:
            return None
        actor = monster.name.split()[-1].lower()
        actor_re = re.escape(actor)
        size_match = re.search(r"a (Small|Medium|Large) or smaller", text, re.I)
        periodic = re.search(
            rf"takes (?P<avg>\d+) \((?P<count>\d+)d(?P<sides>\d+)\) "
            rf"(?P<type>\w+) damage at the start of each of the {actor_re}'s turns",
            text, re.I,
        )
        threshold = re.search(
            rf"If the {actor_re} takes (?P<threshold>\d+) damage or more on a single turn "
            rf"from (?:the swallowed creature|a creature inside it), the {actor_re} must succeed "
            rf"on a DC (?P<dc>\d+) Constitution saving throw at the end of that turn or "
            rf"regurgitate (?P<scope>the creature|all swallowed creatures), which "
            rf"(?:falls|fall) prone in a space within (?P<range>\d+) feet of the {actor_re}\.",
            text, re.I,
        )
        death = re.search(
            rf"If the {actor_re} dies, a swallowed creature is no longer restrained by it and "
            rf"can escape from the corpse (?:by )?using (?P<exit>\d+) feet of movement, exiting prone\.",
            text, re.I,
        )
        if not (size_match and periodic and threshold and death):
            return None
        size = CreatureSize(size_match.group(1).lower())
        count, sides = int(periodic["count"]), int(periodic["sides"])
        if int(periodic["avg"]) != count * (sides + 1) // 2:
            return None

        data = monster.swallow_actions[0] if len(monster.swallow_actions) == 1 else None
        attack_id = str(data.get("attack_id")) if isinstance(data, dict) and data.get("attack_id") else "bite"
        attack = next((item for item in monster.attacks if item.id == attack_id and item.source_complete), None)
        if attack is None:
            attack = _attack(monster, "bite")
        if attack is None:
            return None

        max_swallowed = 1
        if isinstance(data, dict):
            max_swallowed = int(data.get("max_swallowed", 1) or 1)
            expected = {
                "attack_id": attack.id,
                "max_target_size": size.value,
                "requires_existing_grapple": True,
                "damage_dice_count": count,
                "damage_dice_size": sides,
                "damage_bonus": 0,
                "damage_type": periodic["type"].lower(),
                "regurgitation_damage_threshold": int(threshold["threshold"]),
                "regurgitation_save_ability": "constitution",
                "regurgitation_save_dc": int(threshold["dc"]),
                "regurgitation_range_ft": int(threshold["range"]),
                "exit_movement_ft": int(death["exit"]),
                "exit_prone": True,
            }
            if any(data.get(key) != value for key, value in expected.items()):
                return None
        elif "can have only one creature swallowed at a time" not in text.casefold():
            return None

        return GrappleSwallowSource2014(
            source_name="Swallow",
            attack_id=attack.id,
            max_target_size=size,
            damage_dice_count=count,
            damage_dice_size=sides,
            damage_type=periodic["type"].lower(),
            max_swallowed=max_swallowed,
            exit_movement_ft=int(death["exit"]),
            regurgitation_damage_threshold=int(threshold["threshold"]),
            regurgitation_save_ability="constitution",
            regurgitation_save_dc=int(threshold["dc"]),
            regurgitation_range_ft=int(threshold["range"]),
            regurgitation_all_swallowed=threshold["scope"].casefold().startswith("all "),
        )
    except Exception:
        logger.exception("Failed threshold-regurgitation Swallow source proof for %s.", monster.id)
        raise


def source_grapple_swallow_2014(
    monster: SourceMonster2014,
) -> GrappleSwallowSource2014 | None:
    """Compile only fully proven simple or threshold-regurgitation Swallow text."""
    try:
        return _simple_profile(monster) or _threshold_profile(monster)
    except Exception:
        logger.exception("Failed to compile 2014 Swallow source for %s.", monster.id)
        raise
