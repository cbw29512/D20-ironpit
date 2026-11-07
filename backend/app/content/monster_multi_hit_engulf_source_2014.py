"""Source proof: same-target repeated Slam hits promote a held target to Engulf.

Monster IDs never select runtime behavior. Reject changed printed action text.
"""
from __future__ import annotations
import logging
import re
from app.content.monster_source_2014 import SourceMonster2014
from app.content.monster_source_sections_2014 import source_sections_2014
from app.domain.multi_hit_grapple import MultiHitGrappleEffect
from app.domain.source_turn_relation_damage import SourceTurnRelationDamage
from app.domain.size import CreatureSize

logger = logging.getLogger(__name__)
_MULTI = re.compile(
    r"The (?P<actor>[\w '-]+) makes two (?P<attack>[\w-]+) attacks\. "
    r"If both attacks hit a (?P<size>Medium|Small|Large) or smaller target, "
    r"the target is grappled \(escape DC (?P<dc>\d+)\), "
    r"and the (?P=actor) uses its (?P<name>[\w-]+) on it\.", re.I,
)
_ENGULF = re.compile(
    r"The (?P<actor>[\w '-]+) engulfs a (?P<size>Medium|Small|Large) "
    r"or smaller creature grappled by it\. The engulfed target is "
    r"blinded, restrained, and unable to breathe, and it must succeed "
    r"on a DC (?P<save>\d+) Constitution saving throw at the start "
    r"of each of the (?P=actor)'s turns or take (?P<avg>\d+) "
    r"\((?P<count>\d+)d(?P<die>\d+) \+ (?P<bonus>\d+)\) "
    r"(?P<type>bludgeoning|piercing|acid|fire|cold) damage\. "
    r"If the (?P=actor) moves, the engulfed target moves with it\. "
    r"The (?P=actor) can have only one creature engulfed at a time\.", re.I,
)


def source_two_hit_engulf_2014(
    monster: SourceMonster2014,
) -> tuple[MultiHitGrappleEffect, SourceTurnRelationDamage] | None:
    """Validate exact text, existing attacks and parsed damage parameters."""
    try:
        sections = source_sections_2014(monster.source_actions, include_continuations=True)
        a = _MULTI.fullmatch(sections.get("Multiattack", ""))
        b = _ENGULF.fullmatch(sections.get("Engulf", ""))
        if a is None or b is None:
            return None
        if (a["actor"].casefold() != b["actor"].casefold()
                or a["size"].casefold() != b["size"].casefold()
                or a["name"].casefold() != "engulf"):
            return None
        matching = [attack for attack in monster.attacks
                    if attack.name.casefold() == a["attack"].casefold()
                    and attack.kind == "melee"]
        if len(matching) != 1:
            return None
        attack = matching[0]
        if monster.multiattack_slots != [[attack.id], [attack.id]]:
            return None
        if (len(monster.swallow_actions) != 1
                or not isinstance(monster.swallow_actions[0], dict)):
            return None
        raw = monster.swallow_actions[0]
        count, sides, bonus = int(b["count"]), int(b["die"]), int(b["bonus"])
        if int(b["avg"]) != count * (sides + 1) // 2 + bonus:
            return None
        size, dc = CreatureSize(a["size"].lower()), int(a["dc"])
        if int(b["save"]) < 1 or dc < 1:
            return None
        expected = {
            "attack_id": attack.id, "max_target_size": size.value,
            "damage_dice_count": count, "damage_dice_size": sides,
            "damage_bonus": bonus, "damage_type": b["type"].lower(),
            "max_swallowed": 1, "requires_existing_grapple": True,
        }
        if any(raw.get(key) != value for key, value in expected.items() if key in raw):
            return None
        if raw.get("id") not in (None, "engulf"):
            return None
        return (
            MultiHitGrappleEffect(
                source_name="Engulf", attack_id=f"2014-{monster.id}-{attack.id}",
                hits_required=2, max_target_size=size, escape_dc=dc,
                range_ft=attack.reach_ft, max_active_grapples=1,
            ),
            SourceTurnRelationDamage(
                source_name="Engulf", target_relation="creatures_grappled_by_source",
                dice_count=count, dice_size=sides, damage_bonus=bonus,
                damage_type=b["type"].lower(), save_ability="constitution",
                save_dc=int(b["save"]),
            ),
        )
    except Exception:
        logger.exception("Engulf source verification failed for %s.", monster.id)
        raise
