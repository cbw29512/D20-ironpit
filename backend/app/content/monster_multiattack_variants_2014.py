"""Source-proven complete alternatives; runtime never dispatches on creature names."""
from __future__ import annotations
from itertools import permutations
import logging
import re
from app.content.monster_source_sections_2014 import source_sections_2014, requires_two_hands_2014
from app.content.monster_hit_followup_2014 import hit_followup_variants_2014
from app.content.monster_offhand_loadout_2014 import offhand_variants_2014, offhand_unavailable_reason_2014
from app.content.monster_definition_adapter_support_2014 import attack_id_2014
from app.domain.attack_action_definitions import AttackActionSlot, AttackActionVariant
logger = logging.getLogger(__name__)
_NUMBERS = {"one": 1, "two": 2, "three": 3}
_MODE_SOURCE = re.compile(
    r"The (.+?) makes (?:either )?(\w+) melee attacks"
    r"(?:: (.+?)\. Or the \1 makes |--(.+?)--or | or )"
    r"(\w+) ranged attacks(?: with its (.+?))?\.", re.I)


def source_variants_2014(monster):
    try:
        policy = monster.multiattack_policy
        text = source_sections_2014(monster.source_actions).get("Multiattack", "")
        attacks = {attack.id: attack for attack in monster.attacks}
        slots = monster.multiattack_slots
        if not isinstance(policy, dict) or not slots or any(
            not slot or any(i not in attacks for i in slot) for slot in slots
        ):
            return []
        if policy.get("kind") == "drawn-offhand-additional-attack":
            return offhand_variants_2014(monster)
        if "requires_previous_hit_slots" in policy or "same_target_as_previous_slots" in policy:
            return hit_followup_variants_2014(monster)
        branches = []
        if policy == {"distinct_attack_ids": True}:
            if not re.fullmatch(r"The .+? makes two melee attacks, each one with a different weapon\.", text):
                return []
            if len(slots) != 2 or slots[0] != slots[1] or any(attacks[i].kind != "melee" for i in slots[0]):
                return []
            branches = [("melee", [[first], [second]]) for first, second in permutations(slots[0], 2)]
        elif policy.get("kind") == "different-count-by-mode":
            match = _MODE_SOURCE.fullmatch(text)
            if not match:
                return []
            melee_count, ranged_count = _NUMBERS.get(match[2]), _NUMBERS.get(match[5])
            if policy != {"kind": "different-count-by-mode", "melee_attack_count": melee_count,
                          "ranged_attack_count": ranged_count} or len(slots) != melee_count:
                return []
            for mode, count in [("melee", melee_count), ("ranged", ranged_count)]:
                choices = [[i for i in slot if attacks[i].kind == mode] for slot in slots[:count]]
                if not all(choices):
                    return []
                named = (match[3] or match[4]) if mode == "melee" else match[6]
                if named:
                    if mode == "melee":
                        parts = re.fullmatch(r"(\w+) with its (.+?) and (\w+) with its (.+)", named)
                        if not parts:
                            return []
                        names = ([parts[2]] * _NUMBERS.get(parts[1], 0)
                                 + [parts[4]] * _NUMBERS.get(parts[3], 0))
                        if len(names) != count or any(
                            any(attacks[i].name.lower() != name.lower() for i in slot)
                            for slot, name in zip(choices, names)
                        ):
                            return []
                    elif any(attacks[i].name.lower().rstrip("s") != named.lower().rstrip("s")
                             for slot in choices for i in slot):
                        return []
                branches.append((mode, choices))
        return [AttackActionVariant(
            id=f"2014-{monster.id}-multiattack-{mode}-{index}", attack_kind=mode,
            slots=[AttackActionSlot(attack_ids=[attack_id_2014(monster, i) for i in slot]) for slot in branch],
        ) for index, (mode, branch) in enumerate(branches)]
    except Exception:
        logger.exception("Failed complete Multiattack source proof for %s.", monster.id)
        raise


def attack_unavailable_reason_2014(monster, attack):
    """Preserve conditional two-hand damage while retaining the printed shield loadout."""
    try:
        offhand = offhand_unavailable_reason_2014(monster, attack)
        if offhand:
            return offhand
        if "shield" in (monster.armor_class_text or "").lower() and requires_two_hands_2014(monster, attack):
            return "Shield remains equipped; this printed damage requires two hands."
        return None
    except Exception:
        logger.exception("Failed fixed equipment legality for %s / %s.", monster.id, attack.id)
        raise
