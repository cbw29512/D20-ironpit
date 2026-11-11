"""Bind a source-verified ordered zero-damage-control plus damaging attack sequence.

Only the printed sequence is specialized here. Every actual attack still
resolves through the universal Attack/Multiattack engine; displacement-only
actions are omitted under the locked arena policy, never executed as a hit.
"""
from __future__ import annotations

import logging
import re

from app.content.monster_definition_adapter_support_2014 import attack_id_2014
from app.content.monster_informational_action_proofs_2014 import verified_nonactionable_action_2014
from app.content.monster_source_2014 import SourceMonster2014
from app.content.monster_source_damage_free_grapple_2014 import (
    source_proven_damage_free_grapple_attacks_2014,
)
from app.content.monster_source_sections_2014 import source_sections_2014
from app.domain.capability_attacks import CapabilityActionSlot

logger = logging.getLogger(__name__)

_PRINTED_SEQUENCE = re.compile(
    r"The (?P<actor>[a-z][a-z-]*) makes (?P<count>four) attacks with its "
    r"(?P<control>tendrils), uses Reel, and makes one attack with its "
    r"(?P<damage>bite)\.",
    re.IGNORECASE,
)


def source_proven_control_then_damage_slots_2014(
    monster: SourceMonster2014,
) -> list[CapabilityActionSlot] | None:
    """Return ordered universal slots only when all source semantics match."""
    try:
        sections = source_sections_2014(
            monster.source_actions, include_continuations=True,
        )
        match = _PRINTED_SEQUENCE.fullmatch(
            " ".join(sections.get("Multiattack", "").split())
        )
        if match is None or "Multiattack" not in monster.action_names:
            return None
        # The explicitly displacement-only Action is already fully
        # source-certified as nonactionable under the Pit arena rules.
        if not verified_nonactionable_action_2014(monster, "Reel"):
            return None
        proven = source_proven_damage_free_grapple_attacks_2014(monster)
        if len(proven) != 1 or proven[0].name.casefold() != match["control"][:-1].casefold():
            return None
        damage = [
            attack for attack in monster.attacks
            if attack.name.casefold() == match["damage"].casefold()
            and attack.source_complete and attack.id == "bite"
        ]
        if len(damage) != 1:
            return None
        control_id = proven[0].id
        damage_id = attack_id_2014(monster, damage[0].id)
        # Four individually resolved Tendril hits, then Bite.
        # Each Tendril still observes its universal source Grapple capacity.
        return [
            *[CapabilityActionSlot(attack_ids=[control_id]) for _ in range(4)],
            CapabilityActionSlot(attack_ids=[damage_id]),
        ]
    except Exception:
        logger.exception("Failed source-verified control/damage Multiattack for %s", monster.id)
        raise
