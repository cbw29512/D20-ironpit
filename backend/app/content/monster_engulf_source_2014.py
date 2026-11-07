"""Strict source proof for a two-hit Multiattack followed by a held-target action.

No monster ID dispatch. Source headings, dice, sizes, target relationship and
the immutable attack sequence must agree before any source can use this family.
"""
from __future__ import annotations

from dataclasses import dataclass
import logging
import re

from app.content.monster_source_sections_2014 import source_sections_2014
from app.domain.size import CreatureSize

logger = logging.getLogger(__name__)

_MULTI = re.compile(
    r"The (?P<actor>[a-z][a-z '-]+) makes two (?P<attack>[a-z '-]+) attacks\. "
    r"If both attacks hit a (?P<size>Medium) or smaller target, the target is "
    r"grappled \(escape DC (?P<dc>\d+)\), and the (?P=actor) uses its Engulf on it\.",
    re.IGNORECASE,
)
_ENGULF = re.compile(
    r"The (?P<actor>[a-z][a-z '-]+) engulfs a (?P<size>Medium) or smaller "
    r"creature grappled by it\. The engulfed target is blinded, restrained, "
    r"and unable to breathe, and it must succeed on a DC (?P<dc>\d+) "
    r"Constitution saving throw at the start of each of the (?P<short>[a-z '-]+)'s "
    r"turns or take (?P<average>\d+) \((?P<count>\d+)d(?P<sides>\d+) \+ "
    r"(?P<bonus>\d+)\) (?P<type>bludgeoning) damage\. If the (?P=short) moves, "
    r"the engulfed target moves with it\. The (?P=short) can have only one "
    r"creature engulfed at a time\.",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class EngulfProfile2014:
    source_name: str
    attack_id: str
    required_hits: int
    max_target_size: CreatureSize
    grapple_escape_dc: int
    grapple_range_ft: int
    damage_dice_count: int
    damage_dice_size: int
    damage_bonus: int
    damage_type: str
    save_ability: str
    save_dc: int
    max_active_targets: int = 1
    ownership_marker_id: str = "engulfed"


def source_engulf_profile_2014(monster) -> EngulfProfile2014 | None:
    """Only parse a complete printed Multiattack/Engulf pair with typed backing."""
    try:
        if len(monster.swallow_actions) != 1:
            return None
        parts = source_sections_2014(
            monster.source_actions, include_continuations=True,
        )
        multi = _MULTI.fullmatch(parts.get("Multiattack", ""))
        engulf = _ENGULF.fullmatch(parts.get("Engulf", ""))
        if not multi or not engulf:
            return None
        actor = multi["actor"].casefold()
        if engulf["actor"].casefold() != actor or engulf["short"].casefold() != actor.split()[-1]:
            return None
        if multi["size"].casefold() != engulf["size"].casefold():
            return None
        if multi["dc"] != engulf["dc"]:
            return None
        matching = [
            attack for attack in monster.attacks
            if attack.name.casefold() == multi["attack"].casefold()
            and attack.kind == "melee" and attack.source_complete
        ]
        if len(matching) != 1:
            return None
        attack = matching[0]
        if monster.multiattack_slots != [[attack.id], [attack.id]]:
            return None
        dice = int(engulf["count"]), int(engulf["sides"]), int(engulf["bonus"])
        if dice != (2, 8, 4) and any(x <= 0 for x in dice):
            return None
        if int(engulf["average"]) != dice[0] * (dice[1] + 1) // 2 + dice[2]:
            return None
        raw = monster.swallow_actions[0]
        if not isinstance(raw, dict):
            return None
        # Any structured field present must agree with the printed card.
        expected = {
            "id": "engulf", "max_target_size": "medium",
            "damage_dice_count": dice[0], "damage_dice_size": dice[1],
            "damage_bonus": dice[2], "damage_type": "bludgeoning",
            "max_swallowed": 1,
        }
        if any(raw[k] != v for k, v in expected.items() if k in raw):
            return None
        if "Engulf" not in monster.action_names:
            return None
        return EngulfProfile2014(
            source_name="Engulf", attack_id=attack.id, required_hits=2,
            max_target_size=CreatureSize.MEDIUM,
            grapple_escape_dc=int(multi["dc"]), grapple_range_ft=attack.reach_ft,
            damage_dice_count=dice[0], damage_dice_size=dice[1],
            damage_bonus=dice[2], damage_type="bludgeoning",
            save_ability="constitution", save_dc=int(engulf["dc"]),
        )
    except Exception:
        logger.exception("Failed full-body Engulf source proof.")
        raise
