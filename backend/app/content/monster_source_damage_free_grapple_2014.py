"""Compile damage-free source grapples using existing attack and grapple primitives.

This is a partial Roper Tendril binding. Printed Strength penalties,
individual tendril destruction, regeneration and Multiattack ordering are
NOT modeled here. Source admission must remain blocked.
"""
from __future__ import annotations

import logging
import re

from app.content.monster_definition_adapter_support_2014 import attack_id_2014
from app.content.monster_source_2014 import SourceMonster2014
from app.content.monster_source_sections_2014 import source_sections_2014
from app.domain.capability_attack_definitions import AttackCapabilityDefinition
from app.domain.capability_effects import GrappleEffectDefinition
from app.domain.weapons_base import DamageType

logger = logging.getLogger(__name__)

# The whole source Action must match. The owner reference is checked against
# the printed trait, not a combat runtime name or class.
_TENDRIL = re.compile(
    r"Melee Weapon Attack: \+(?P<bonus>\d+) to hit, reach (?P<reach>\d+) ft\., "
    r"one creature\. Hit: The target is grappled \(escape DC (?P<dc>\d+)\)\. "
    r"Until the grapple ends, the target is restrained and has disadvantage on "
    r"Strength checks and Strength saving throws, and the (?P<owner>[a-z]+) "
    r"can't use the same tendril on another target\.",
    re.IGNORECASE,
)
_TRAIT = re.compile(
    r"The (?P<owner>[a-z]+) can have up to (?P<limit>\w+) tendrils at a time\. "
    r"Each tendril can be attacked \(AC (?P<ac>\d+); (?P<hp>\d+) hit points; "
    r"immunity to poison and psychic damage\)\. "
    r"Destroying a tendril deals no damage to the (?P=owner), which can extrude "
    r"a replacement tendril on its next turn\. A tendril can also be broken "
    r"if a creature takes an action and succeeds on a DC (?P<break_dc>\d+) "
    r"Strength check against it\.",
    re.IGNORECASE,
)
_WORD_COUNTS = {"six": 6}


def source_proven_damage_free_grapple_attacks_2014(
    monster: SourceMonster2014,
) -> list[AttackCapabilityDefinition]:
    """Bind only the already-supported part of a complete printed source."""
    try:
        actions = source_sections_2014(
            monster.source_actions, include_continuations=True,
        )
        traits = source_sections_2014(
            monster.source_traits, include_continuations=True,
        )
        trait = _TRAIT.fullmatch(traits.get("Grasping Tendrils", ""))
        if trait is None:
            return []
        limit = _WORD_COUNTS.get(trait["limit"].lower())
        if limit is None:
            return []
        # This partial binding is certified only against the pinned source.
        # Changed durability must fail closed until the generic object rider
        # actually supports that source profile.
        if (int(trait["break_dc"]), int(trait["ac"]), int(trait["hp"])) != (15, 20, 10):
            return []
        output: list[AttackCapabilityDefinition] = []
        for heading in monster.action_names:
            source = actions.get(heading, "")
            match = _TENDRIL.fullmatch(source)
            if match is None:
                continue
            if match["owner"].lower() != trait["owner"].lower():
                continue
            bonus, reach, dc = (int(match[key]) for key in ("bonus", "reach", "dc"))
            if bonus < 0 or reach <= 0 or reach % 5 or not (1 <= dc <= 40):
                continue
            source_id = re.sub(r"[^a-z0-9]+", "-", heading.lower()).strip("-")
            if not source_id or any(attack.name.casefold() == heading.casefold()
                                    for attack in monster.attacks):
                continue
            action_id = attack_id_2014(monster, source_id)
            output.append(AttackCapabilityDefinition(
                id=action_id, weapon_id=action_id, name=heading,
                attack_kind="melee", attack_bonus=bonus, reach_ft=reach,
                # The Action deals no damage. This type is a zero-damage
                # carrier required by the existing attack schema.
                fixed_damage=0, damage_type=DamageType.BLUDGEONING,
                animation="slash",
                effects=[GrappleEffectDefinition(
                    escape_dc=dc, restrains=True, max_active_grapples=limit,
                )],
            ))
        return output
    except Exception:
        logger.exception("Failed source-only damage-free grapple binding for %s", monster.id)
        raise
