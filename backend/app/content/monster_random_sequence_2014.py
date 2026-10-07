"""Source-proven random repetitions of one printed attack; engine stays generic."""
import logging
import re
from app.content.monster_source_sections_2014 import source_sections_2014
from app.content.monster_definition_adapter_support_2014 import attack_id_2014
from app.domain.attack_action_definitions import AttackActionSlot, AttackActionVariant, AttackSequenceRepetition
logger = logging.getLogger(__name__)


def random_sequence_variants_2014(monster):
    try:
        policy = monster.multiattack_policy
        if not isinstance(policy, dict) or set(policy) != {"repeat_slot_index", "repeat_dice_count", "repeat_dice_size"}:
            return []
        text = source_sections_2014(monster.source_actions).get("Multiattack", "")
        match = re.fullmatch(r"The .+? makes (\d+)d(\d+) (.+?) attacks\.", text, re.I)
        slots, attacks = monster.multiattack_slots, {a.id: a for a in monster.attacks}
        if not match or len(slots) != 1 or len(slots[0]) != 1 or slots[0][0] not in attacks:
            return []
        count, size = map(int, match.groups()[:2])
        if any(type(v) is not int for v in policy.values()) or policy != {"repeat_slot_index": 0, "repeat_dice_count": count, "repeat_dice_size": size}:
            return []
        attack = attacks[slots[0][0]]
        if attack.name.lower() != match[3].lower() or not 1 <= count <= 4 or not 2 <= size <= 8 or count*size > 8:
            return []
        return [AttackActionVariant(id=f"2014-{monster.id}-multiattack-random", attack_kind=attack.kind,
            repetitions=AttackSequenceRepetition(dice_count=count, dice_size=size),
            slots=[AttackActionSlot(attack_ids=[attack_id_2014(monster, attack.id)])])]
    except Exception:
        logger.exception("Failed printed random sequence binding for %s.", monster.id)
        raise
