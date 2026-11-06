"""Source-prove end-turn recurring weapon-hit effects across 2014 cards."""
from __future__ import annotations

import logging
import re

from app.content.monster_source_2014 import SourceAttack2014, SourceMonster2014
from app.content.monster_source_sections_2014 import source_sections_2014
from app.domain.recurring_damage import OnHitRecurringDamage

logger = logging.getLogger(__name__)
_BASE = re.compile(
    r"^Melee Weapon Attack: \+(?P<bonus>\d+) to hit, reach (?P<reach>\d+) ft\., "
    r"one target\. Hit: (?P<average>\d+) "
    r"\((?P<count>\d+)d(?P<sides>\d+)(?: \+ (?P<flat>\d+))?\) "
    r"(?P<type>\w+) damage\.$", flags=re.IGNORECASE,
)

# This is source grammar, not a name/monster-specific combat resolver.
_IGNITION = re.compile(
    r"if the target is a creature(?: or a flammable object)?, it ignites\. "
    r"until a creature takes an action to douse the fire, the target takes "
    r"(?P<average>\d+) \((?P<count>\d+)d(?P<sides>\d+)\) (?P<type>\w+) "
    r"damage at the end of each of its turns\.",
    flags=re.IGNORECASE,
)


def source_end_turn_recurring_damage_2014(
    monster: SourceMonster2014, attack: SourceAttack2014,
) -> OnHitRecurringDamage | None:
    """Return only fully source-proven hit/tick dice; douse range stays blocked."""
    try:
        section = source_sections_2014(
            monster.source_actions, include_continuations=True,
        ).get(attack.name, "").strip()
        match = _IGNITION.search(section)
        if match is None or match.end() != len(section):
            return None
        # The ordinary attack parser owns its hit/damage fields; the recurring
        # clause must actually be attached to the same printed hit paragraph.
        if "Hit:" not in section[:match.start()]:
            return None
        count, sides, average = (
            int(match["count"]), int(match["sides"]), int(match["average"])
        )
        if not (1 <= count <= 40 and 2 <= sides <= 100):
            return None
        if average != count * (sides + 1) // 2:
            return None
        return OnHitRecurringDamage(
            effect_id="burning", dice_count=count, dice_size=sides,
            damage_type=match["type"].lower(),
            removal_action_ids=["douse-fire"],
        )
    except Exception:
        logger.exception("2014 recurring hit-effect source proof failed for %s.", monster.id)
        raise

def source_completed_recurring_attack_2014(
    monster: SourceMonster2014, attack: SourceAttack2014,
) -> SourceAttack2014:
    """Admit a previously partial hit only when normal damage AND douse are proven."""
    try:
        if attack.source_complete or attack.kind != "melee":
            return attack
        if (attack.on_hit_damage or attack.on_hit_save_effect
                or attack.control_effect or attack.ongoing_damage_effect
                or attack.conditional_damage):
            return attack
        if source_end_turn_recurring_damage_2014(monster, attack) is None:
            return attack
        section = source_sections_2014(
            monster.source_actions, include_continuations=True,
        ).get(attack.name, "")
        marker = " If the target is a creature"
        if section.count(marker) != 1:
            return attack
        prefix, _ = section.split(marker, 1)
        hit = _BASE.fullmatch(prefix)
        if hit is None:
            return attack
        damage = attack.damage
        if (
            int(hit["bonus"]) != attack.attack_bonus
            or int(hit["reach"]) != attack.reach_ft
            or (int(hit["average"]), int(hit["count"]), int(hit["sides"]),
                int(hit["flat"] or 0), hit["type"].lower())
            != (damage.average, damage.dice_count, damage.dice_size,
                damage.bonus, damage.type)
        ):
            return attack
        return attack.model_copy(update={"source_complete": True})
    except Exception:
        logger.exception("Strict recurring-hit attack proof failed for %s.", monster.id)
        raise
