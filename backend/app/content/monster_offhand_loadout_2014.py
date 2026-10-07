"""Source-only fixed offhand preparation; ordinary sequence engine stays unchanged."""
from __future__ import annotations
import logging
import re
from app.content.monster_source_2014 import SourceMonster2014, SourceAttack2014
from app.content.monster_source_sections_2014 import source_sections_2014, requires_two_hands_2014
from app.content.monster_definition_adapter_support_2014 import attack_id_2014
from app.domain.attack_action_definitions import AttackActionSlot, AttackActionVariant
logger = logging.getLogger(__name__)
_WORD_COUNTS = {"one": 1, "two": 2, "three": 3}


def _offhand_slots(monster: SourceMonster2014) -> list[list[str]] | None:
    try:
        policy = monster.multiattack_policy
        if not isinstance(policy, dict) or policy.get("kind") != "drawn-offhand-additional-attack":
            return None
        if set(policy) != {"kind", "offhand_attack_id", "incompatible_attack_ids"}:
            return None
        offhand_id, incompatible = policy["offhand_attack_id"], policy["incompatible_attack_ids"]
        if not isinstance(offhand_id, str) or not isinstance(incompatible, list) or not all(isinstance(i, str) for i in incompatible):
            return None
        text = source_sections_2014(monster.source_actions).get("Multiattack", "")
        match = re.fullmatch(r"The .+? makes (one|two|three) (.+?) attacks\. If it has a (.+?) drawn, it can also make a (.+?) attack\.", text, re.I)
        if not match:
            return None
        count = _WORD_COUNTS[match[1].lower()]
        slots = monster.multiattack_slots
        attacks = {a.id: a for a in monster.attacks}
        if len(slots) != count+1 or slots[-1] != [offhand_id] or any(
            not slot or any(i not in attacks for i in slot) for slot in slots
        ):
            return None
        offhand = attacks[offhand_id]
        hand_ids = {i for slot in slots[:count] for i in slot}
        if offhand.kind != "melee" or offhand.name.lower() != match[3].lower() or match[3].lower() != match[4].lower():
            return None
        if offhand_id in hand_ids or any(attacks[i].kind != "melee" or attacks[i].name.lower() != match[2].lower() for i in hand_ids):
            return None
        proved = {i for i in hand_ids if requires_two_hands_2014(monster, attacks[i])}
        if not proved or set(incompatible) != proved or len(incompatible) != len(proved):
            return None
        choices = [[i for i in slot if i not in proved] for slot in slots[:count]] + [[offhand_id]]
        return choices if all(choices) else None
    except Exception:
        logger.exception("Failed fixed offhand source binding for %s.", monster.id)
        raise


def offhand_variants_2014(monster: SourceMonster2014) -> list[AttackActionVariant]:
    try:
        slots = _offhand_slots(monster)
        if slots is None:
            return []
        return [AttackActionVariant(id=f"2014-{monster.id}-multiattack-offhand", attack_kind="melee",
            slots=[AttackActionSlot(attack_ids=[attack_id_2014(monster, i) for i in slot]) for slot in slots])]
    except Exception:
        logger.exception("Failed fixed offhand variant for %s.", monster.id)
        raise


def offhand_unavailable_reason_2014(monster: SourceMonster2014, attack: SourceAttack2014) -> str | None:
    try:
        if _offhand_slots(monster) is not None and attack.id in monster.multiattack_policy["incompatible_attack_ids"]:
            return "Printed offhand weapon stays drawn; this conditional damage requires two hands."
        return None
    except Exception:
        logger.exception("Failed fixed offhand attack availability for %s / %s.", monster.id, attack.id)
        raise
