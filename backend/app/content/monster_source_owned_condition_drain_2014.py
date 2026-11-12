"""Source-exact 2014 save damage against a condition owned by the acting source.

This is an immutable-card adapter, not a monster/ability-name combat resolver.
Both printed eligibility branches are represented by shared target qualification:
source-owned Charmed or explicit willingness.
"""
from __future__ import annotations

import logging
import re

from app.content.monster_source_2014 import SourceMonster2014
from app.content.monster_source_sections_2014 import source_sections_2014
from app.domain.capability_effects import DiceSpec
from app.domain.capability_save_definitions import SaveCapabilityDefinition
from app.domain.targeting import TargetQualification
from app.domain.weapons import DamageType

logger = logging.getLogger(__name__)

_CHARMED_DRAIN = re.compile(
    r"The (?P<owner>\w+) kisses a creature charmed by it or a willing creature\. "
    r"The target must make a DC (?P<dc>\d+) (?P<save>Constitution) saving throw "
    r"against this magic, taking (?P<average>\d+) \((?P<count>\d+)d"
    r"(?P<size>\d+) \+ (?P<bonus>\d+)\) (?P<type>psychic) damage on a failed "
    r"save, or half as much damage on a successful one\. "
    r"The target's hit point maximum is reduced by an amount equal to the damage taken\. "
    r"This reduction lasts until the target finishes a long rest\. "
    r"The target dies if this effect reduces its hit point maximum to 0\.",
    re.IGNORECASE,
)


def source_proven_owned_condition_drains_2014(
    monster: SourceMonster2014,
) -> list[SaveCapabilityDefinition]:
    """Compile the source-charmed hostile branch using existing save/HP semantics."""
    try:
        sections = source_sections_2014(
            monster.source_actions, include_continuations=True,
        )
        actions: list[SaveCapabilityDefinition] = []
        for name in monster.action_names:
            printed = sections.get(name)
            if not printed:
                continue
            match = _CHARMED_DRAIN.fullmatch(
                " ".join(printed.replace("’", "'").split()),
            )
            if match is None:
                continue
            dc, count, size, bonus, average = (
                int(match[key]) for key in ("dc", "count", "size", "bonus", "average")
            )
            if not (1 <= dc <= 40 and 1 <= count <= 40 and 2 <= size <= 100):
                continue
            if average != count * (size + 1) // 2 + bonus:
                continue
            action_id = re.sub(r"[^a-z0-9]+", "-", name.casefold()).strip("-")
            if not action_id:
                continue
            actions.append(SaveCapabilityDefinition(
                id=action_id, name=name, save_ability=match["save"].casefold(),
                dc=dc, range_ft=5,  # Generic contact/kiss reach in one 5-ft square.
                damage=DiceSpec(count=count, size=size, bonus=bonus),
                damage_type=DamageType(match["type"].casefold()),
                success_damage="half", magical_effect=True,
                target_scope="all-other-creatures",
                target_qualification=TargetQualification(any_of=["source_charmed", "willing"]),
                reduce_hit_point_maximum_on_damage=True,
                max_hp_zero_kills=True, animation="life-drain",
            ))
        return actions
    except Exception:
        logger.exception("Failed source-owned condition drain proof for %s.", monster.id)
        raise
