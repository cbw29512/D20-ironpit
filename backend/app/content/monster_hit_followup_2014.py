"""Printed previous-hit/same-target sequence proof; no creature-name resolver."""
import logging
import re
from app.content.monster_source_sections_2014 import source_sections_2014
from app.content.monster_definition_adapter_support_2014 import attack_id_2014
from app.domain.attack_action_definitions import AttackActionSlot, AttackActionVariant, PreviousAttackRequirement
logger = logging.getLogger(__name__)


def hit_followup_variants_2014(monster):
    try:
        if monster.multiattack_policy != {"requires_previous_hit_slots": [1], "same_target_as_previous_slots": [1]}:
            return []
        text = source_sections_2014(monster.source_actions).get("Multiattack", "")
        match = re.fullmatch(r"The .+? makes one attack with its (.+?)\. If that attack hits, the .+? can make one (.+?) attack against the same target\.", text, re.I)
        slots = monster.multiattack_slots
        attacks = {a.id: a for a in monster.attacks}
        if not match or len(slots) != 2 or any(len(s) != 1 or s[0] not in attacks for s in slots):
            return []
        if any(attacks[slot[0]].name.lower() != name.lower() or attacks[slot[0]].kind != "melee"
               for slot, name in zip(slots, match.groups())):
            return []
        return [AttackActionVariant(id=f"2014-{monster.id}-multiattack-hit-followup", attack_kind="melee", slots=[
            AttackActionSlot(attack_ids=[attack_id_2014(monster, slots[0][0])]),
            AttackActionSlot(attack_ids=[attack_id_2014(monster, slots[1][0])],
                            previous_attack=PreviousAttackRequirement(hit=True, same_target=True)),
        ])]
    except Exception:
        logger.exception("Failed printed hit follow-up binding for %s.", monster.id)
        raise
