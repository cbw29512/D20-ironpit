"""Exact source proof of object-only mechanics in a fixed natural-form arena."""
from __future__ import annotations

import logging
import re

from app.content.monster_source_2014 import SourceMonster2014, SourceAttack2014
from app.content.monster_source_sections_2014 import source_sections_2014

logger = logging.getLogger(__name__)

_ADHESIVE = re.compile(
    r"The (?P<owner>[a-z][a-z -]*) adheres to anything that touches it\. "
    r"A Huge or smaller creature adhered to the (?P=owner) is also grappled by it "
    r"\(escape DC (?P<dc>\d+)\)\. "
    r"Ability checks made to escape this grapple have disadvantage\.",
    re.IGNORECASE,
)
_FALSE_APPEARANCE = re.compile(
    r"While the (?P<owner>[a-z][a-z -]*) remains motionless, it is "
    r"indistinguishable from an ordinary object\.",
    re.IGNORECASE,
)
_PSEUDOPOD = re.compile(
    r"Melee Weapon Attack: \+(?P<bonus>\d+) to hit, reach (?P<reach>\d+) ft\., "
    r"one target\. Hit: (?P<average>\d+) \((?P<count>\d+)d(?P<size>\d+) "
    r"\+ (?P<modifier>\d+)\) bludgeoning damage\. "
    r"If the (?P<owner>[a-z][a-z -]*) is in object form, the target is "
    r"subjected to its Adhesive trait\.",
    re.IGNORECASE,
)


def proven_natural_form_only_traits_2014(monster: SourceMonster2014) -> set[str]:
    """Only exact clauses that cannot trigger outside forbidden object form."""
    try:
        if not {"Shapechanger", "Adhesive (Object Form Only)",
                "False Appearance (Object Form Only)"}.issubset(monster.trait_names):
            return set()
        traits = source_sections_2014(
            monster.source_traits, include_continuations=True
        )
        if (_ADHESIVE.fullmatch(traits.get("Adhesive (Object Form Only)", "")) is None
                or _FALSE_APPEARANCE.fullmatch(
                    traits.get("False Appearance (Object Form Only)", "")
                ) is None):
            return set()
        adhesive = _ADHESIVE.fullmatch(traits["Adhesive (Object Form Only)"])
        if adhesive is None or int(adhesive["dc"]) != 13:
            return set()
        return {"Adhesive (Object Form Only)", "False Appearance (Object Form Only)"}
    except Exception:
        logger.exception("Natural-form-only trait proof failed: %s.", monster.id)
        raise


def source_completed_natural_form_attack_2014(
    monster: SourceMonster2014, attack: SourceAttack2014,
) -> SourceAttack2014:
    """Retain printed damage and exclude unreachable object-only on-hit rider."""
    try:
        if (attack.source_complete or attack.kind != "melee"
                or proven_natural_form_only_traits_2014(monster) == set()):
            return attack
        printed = source_sections_2014(
            monster.source_actions, include_continuations=True
        ).get(attack.name, "")
        match = _PSEUDOPOD.fullmatch(printed)
        if match is None or (
            int(match["bonus"]) != attack.attack_bonus
            or int(match["reach"]) != attack.reach_ft
            or int(match["average"]) != attack.damage.average
            or int(match["count"]) != attack.damage.dice_count
            or int(match["size"]) != attack.damage.dice_size
            or int(match["modifier"]) != attack.damage.bonus
            or str(attack.damage.type) != "bludgeoning"
            or attack.control_effect is not None
            or bool(attack.on_hit_damage)
        ):
            return attack
        # The body remains in natural form for the entire battle. Source data
        # remains printed and immutable; only compiler completeness changes.
        return attack.model_copy(update={"source_complete": True})
    except Exception:
        logger.exception("Fixed natural-form attack validation failed: %s/%s",
                         monster.id, attack.id)
        raise
