"""Source-proven complete alternatives; runtime never dispatches on creature names."""
from __future__ import annotations
from itertools import permutations
import logging
import re
from app.content.monster_source_sections_2014 import source_sections_2014, requires_two_hands_2014
from app.content.monster_random_sequence_2014 import random_sequence_variants_2014
from app.content.monster_hit_followup_2014 import hit_followup_variants_2014
from app.content.monster_offhand_loadout_2014 import offhand_variants_2014, offhand_unavailable_reason_2014
from app.content.monster_definition_adapter_support_2014 import attack_id_2014
from app.domain.attack_action_definitions import AttackActionSlot, AttackActionVariant
logger = logging.getLogger(__name__)
_NUMBERS = {"one": 1, "two": 2, "three": 3}
_FORM_QUALIFIED_MULTIATTACK = re.compile(
    r"multiattack\.? \(humanoid or hybrid form only\)", re.I,
)
_MODE_SOURCE = re.compile(
    r"The (.+?) makes (?:either )?(\w+) melee attacks"
    r"(?:: (.+?)\. Or the \1 makes |--(.+?)--or | or )"
    r"(\w+) ranged attacks(?: with its (.+?))?\.", re.I)


def source_multiattack_text_2014(monster) -> str:
    """Return the printed Multiattack paragraph, including form-gated headings."""
    sections = source_sections_2014(monster.source_actions)
    text = sections.get("Multiattack", "")
    if text:
        return text
    for name in monster.action_names:
        if name.casefold().startswith("multiattack"):
            return sections.get(name, "")
    return ""


def source_form_qualified_multiattack_labels_2014(monster) -> set[str]:
    """Return exact printed form-gated Multiattack headings.

    The heading is source data, not a runtime dispatch key.  This proof is
    deliberately narrow: an edited form gate stays unsupported until its
    semantics are audited instead of inheriting this classification.
    """
    sections = source_sections_2014(monster.source_actions)
    return {
        name.strip().casefold()
        for name in monster.action_names
        if _FORM_QUALIFIED_MULTIATTACK.fullmatch(name.strip())
        and bool(sections.get(name, "").strip())
    }


def _printed_attack_name(attack) -> str:
    return re.split(r"[.(]", attack.name, maxsplit=1)[0].strip().casefold()


def _at_most_once_source_proven(text: str, limited_attacks: list[object]) -> bool:
    match = re.fullmatch(
        r"The .+? makes two attacks, only one of which can be "
        r"(?:(?:with its )|(?:a ))?(.+?)(?: attack)?\.", text, re.I,
    )
    return bool(
        match
        and len(limited_attacks) == 1
        and match.group(1).strip().casefold() == _printed_attack_name(limited_attacks[0])
    )


def _same_attack_source_proven(text: str, choices: list[object]) -> bool:
    return all(
        re.search(rf"\btwo\s+{re.escape(_printed_attack_name(attack))}s?\s+attacks?\b", text, re.I)
        for attack in choices
    )


def source_variants_2014(monster):
    try:
        policy = monster.multiattack_policy
        text = source_multiattack_text_2014(monster)
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
        if "repeat_slot_index" in policy:
            return random_sequence_variants_2014(monster)
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
        # Lycanthrope slot rules: at most one of a named attack, or both slots the same.
        if not branches and isinstance(policy, dict):
            if set(policy) == {"at_most_once_attack_ids"}:
                limited = set(policy["at_most_once_attack_ids"])
                # Two slots of the same alternatives; limit one slot to the restricted attack.
                limited_attacks = [attacks[i] for i in limited if i in attacks]
                if (len(slots) == 2 and slots[0] == slots[1]
                        and limited <= set(slots[0])
                        and _at_most_once_source_proven(text, limited_attacks)):
                    choices = slots[0]
                    # Variant: one limited + one other, or two non-limited.
                    for limited_id in limited:
                        others = [i for i in choices if i != limited_id]
                        if others:
                            branches.append((None, [[limited_id], others]))
                            branches.append((None, [others, [limited_id]]))
                    non_limited = [i for i in choices if i not in limited]
                    if non_limited:
                        branches.append((None, [non_limited, non_limited]))
            elif policy == {"same_attack_as_previous_slots": [1]}:
                # Both slots must be the same attack.
                if (len(slots) == 2 and slots[0] == slots[1]
                        and _same_attack_source_proven(text, [attacks[i] for i in slots[0]])):
                    for attack_id in slots[0]:
                        branches.append((attacks[attack_id].kind, [[attack_id], [attack_id]]))
        return [AttackActionVariant(
            id=f"2014-{monster.id}-multiattack-{mode or 'mixed'}-{index}", attack_kind=mode,
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
