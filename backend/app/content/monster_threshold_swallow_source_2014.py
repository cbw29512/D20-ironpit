"""Source proof for 2014 damage-threshold Swallow regurgitation."""
from __future__ import annotations

from dataclasses import dataclass
import logging
import re

from app.content.monster_source_2014 import SourceMonster2014
from app.content.monster_source_sections_2014 import source_sections_2014
from app.domain.size import CreatureSize

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class ThresholdSwallowProof2014:
    attack_id: str
    max_target_size: CreatureSize
    damage_dice_count: int
    damage_dice_size: int
    damage_type: str
    max_swallowed: int
    exit_movement_ft: int
    damage_threshold: int
    save_dc: int
    range_ft: int
    all_swallowed: bool


def _semantic_text(monster: SourceMonster2014) -> str:
    try:
        sections = source_sections_2014(monster.source_actions, include_continuations=True)
        selected = [
            text for heading, text in sections.items()
            if re.search(r"\b(?:swallow(?:s|ed)?|regurgitate)\b", f"{heading} {text}", re.I)
        ]
        return " ".join(" ".join(text.split()) for text in selected)
    except Exception:
        logger.exception("Failed to collect threshold Swallow text for %s.", monster.id)
        raise


def threshold_swallow_source_2014(
    monster: SourceMonster2014,
) -> ThresholdSwallowProof2014 | None:
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
        attack = next(
            (item for item in monster.attacks if item.id == attack_id and item.source_complete),
            None,
        )
        if attack is None:
            return None
        max_swallowed = int(data.get("max_swallowed", 1) or 1) if isinstance(data, dict) else 1

        if isinstance(data, dict):
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

        return ThresholdSwallowProof2014(
            attack.id, size, count, sides, periodic["type"].lower(),
            max_swallowed, int(death["exit"]), int(threshold["threshold"]),
            int(threshold["dc"]), int(threshold["range"]),
            threshold["scope"].casefold().startswith("all "),
        )
    except Exception:
        logger.exception("Failed threshold Swallow source proof for %s.", monster.id)
        raise
