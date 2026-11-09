"""Source-owned start-of-turn damage to a creature grappled by the source.

Schema: an immutable SourceTurnRelationDamage selects target relationship,
printed feature label, dice, flat bonus and type; fight state owns Grapples.
Only a complete source paragraph can provide these fields.
"""
from __future__ import annotations

import logging
import re

from app.content.monster_arena_action_policy_2014 import action_label_2014
from app.content.monster_shared_space_recharge_2014 import (
    source_shared_space_recharge_headers_2014,
)
from app.content.monster_source_2014 import SourceMonster2014
from app.content.monster_source_sections_2014 import source_sections_2014
from app.domain.source_turn_relation_damage import SourceTurnRelationDamage
from app.domain.weapons_base import DamageType

logger = logging.getLogger(__name__)

# This is source grammar, not an ability-name/runtime switch. Require the
# *entire* save, Grapple, breathing, capacity, tick and rescue source.
_PARTS = [
    r"On a failure, a target takes (?P<initial_avg>\d+) \((?P<initial_count>\d+)d(?P<initial_size>\d+) \+ (?P<initial_bonus>\d+)\) (?P<initial_type>\w+) damage\.",
    r"If it is Large or smaller, it is also grappled \(escape DC (?P<escape_dc>\d+)\)\.",
    r"Until this grapple ends, the target is restrained and unable to breathe unless it can breathe water\.",
    r"If the saving throw is successful, the target is pushed out of the (?P<owner>[\w ]+)'s space\.",
    r"The (?P=owner) can grapple one Large creature or up to two Medium or smaller creatures at one time\.",
    r"At the start of each of the (?P=owner)'s turns, each target grappled by it takes (?P<tick_avg>\d+) \((?P<tick_count>\d+)d(?P<tick_size>\d+) \+ (?P<tick_bonus>\d+)\) (?P<tick_type>\w+) damage\.",
    r"A creature within (?P<helper_range>\d+) feet of the (?P=owner) can pull a creature or object out of it by taking an action to make a DC (?P<helper_dc>\d+) Strength and succeeding\.",
]
_WHOLE = re.compile(r"\s+".join(_PARTS), re.IGNORECASE)


def _source_average(count: int, sides: int, bonus: int) -> int:
    """SRD integer average is floor(count * mean(die) + bonus)."""
    return (count * (sides + 1)) // 2 + bonus


def source_held_turn_damage_2014(
    monster: SourceMonster2014,
) -> list[SourceTurnRelationDamage]:
    """Bind only a fully proven source turn-damage rider; do not admit the Action."""
    try:
        sections = source_sections_2014(
            monster.source_actions, include_continuations=True,
        )
        result: list[SourceTurnRelationDamage] = []
        for header in source_shared_space_recharge_headers_2014(monster):
            action_heading = [
                heading for heading in monster.action_names
                if action_label_2014(heading) == header.source_name.casefold()
                and heading in sections
            ]
            if len(action_heading) != 1:
                continue
            # Until source-labeled Grapple links exist, other grapple-causing
            # actions would risk a false tick. Reject those cards, fail closed.
            if any(
                "grapple" in body.casefold()
                for heading, body in sections.items()
                if heading != action_heading[0]
            ) or any(attack.control_effect is not None for attack in monster.attacks):
                continue
            match = _WHOLE.fullmatch(header.unbound_outcomes.replace("’", "'"))
            if match is None:
                continue
            n = {
                key: int(value) for key, value in match.groupdict().items()
                if key not in {"owner", "initial_type", "tick_type"}
            }
            if (
                not (1 <= n["initial_count"] <= 40 and 1 <= n["tick_count"] <= 40)
                or not (2 <= n["initial_size"] <= 100 and 2 <= n["tick_size"] <= 100)
                or n["initial_avg"] != _source_average(
                    n["initial_count"], n["initial_size"], n["initial_bonus"]
                )
                or n["tick_avg"] != _source_average(
                    n["tick_count"], n["tick_size"], n["tick_bonus"]
                )
                or n["escape_dc"] != n["helper_dc"]
                or n["helper_range"] <= 0
            ):
                continue
            result.append(SourceTurnRelationDamage(
                source_name=header.source_name,
                target_relation="creatures_grappled_by_source",
                dice_count=n["tick_count"], dice_size=n["tick_size"],
                damage_bonus=n["tick_bonus"],
                damage_type=DamageType(match["tick_type"].casefold()),
            ))
        return result
    except Exception:
        logger.exception("Failed held-target source-turn damage proof for %s.", monster.id)
        raise
