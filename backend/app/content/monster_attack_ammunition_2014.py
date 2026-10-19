"""Bind printed finite ammunition to shared per-attack resource semantics.

Source wording is checked here, never in the combat resolver.
"""
from __future__ import annotations

import logging
import re

from app.content.monster_source_sections_2014 import source_sections_2014
from app.content.monster_definition_adapter_support_2014 import attack_id_2014
from app.domain.attack_action_definitions import AttackActionSlot, AttackActionVariant

logger = logging.getLogger(__name__)
_COUNTS = {"twenty-four": 24}
_REGROWTH = re.compile(
    r"The .+? has (twenty-four|\d+) ([\w -]+)\. Used ([\w -]+) regrow when the .+? finishes a long rest\.",
    re.I,
)
_MULTIATTACK = re.compile(
    r"The .+? makes three attacks: one with its (.+?) and two with its (.+?) or three with its (.+?)\.",
    re.I,
)


def attack_ammunition_2014(monster) -> dict[str, int]:
    """Return source-proven attack ID -> finite number of uses per fight."""
    try:
        sections = source_sections_2014(monster.source_traits)
        bindings = {}
        for attack in monster.attacks:
            if attack.id not in monster.limited_action_uses:
                continue
            trait = f"{attack.name} Regrowth"
            body = sections.get(trait)
            if trait not in monster.trait_names or not body:
                continue
            match = _REGROWTH.fullmatch(body)
            if match is None:
                continue
            count_word, projectiles, used = match.groups()
            count = _COUNTS.get(count_word.lower())
            if count is None:
                count = int(count_word)
            attack_plural = attack.name.casefold() + "s"
            last_plural = attack.name.split()[-1].casefold() + "s"
            if (projectiles.casefold() != attack_plural
                or used.casefold() != last_plural
                or attack.kind != "ranged"
                or count <= 0
                or monster.limited_action_uses[attack.id] != count):
                continue
            bindings[attack.id] = count
        return bindings
    except Exception:
        logger.exception("Failed ammunition source binding for %s.", monster.id)
        raise


def ammunition_multiattack_variants_2014(monster) -> list[AttackActionVariant]:
    """Prove complete melee/ranged alternatives from printed grouped wording."""
    try:
        ammunition = attack_ammunition_2014(monster)
        if not ammunition or monster.multiattack_policy is not None:
            return []
        match = _MULTIATTACK.fullmatch(
            source_sections_2014(monster.source_actions).get("Multiattack", "")
        )
        if match is None or len(monster.multiattack_slots) != 3:
            return []
        by_name = {attack.name.casefold(): attack for attack in monster.attacks}
        first, second, ranged = (by_name.get(name.casefold().rstrip("s")) for name in match.groups())
        if any(item is None for item in (first, second, ranged)):
            return []
        if first.kind != "melee" or second.kind != "melee" or ranged.kind != "ranged":
            return []
        if ranged.id not in ammunition or len({first.id, second.id, ranged.id}) != 3:
            return []
        expected = [[first.id, ranged.id], [second.id, ranged.id], [second.id, ranged.id]]
        if monster.multiattack_slots != expected:
            return []
        # All three ranged attacks spend one from the same finite pool.
        return [
            AttackActionVariant(
                id=f"2014-{monster.id}-multiattack-melee", attack_kind="melee",
                slots=[AttackActionSlot(attack_ids=[attack_id_2014(monster, item)]) for item in (first.id, second.id, second.id)],
            ),
            AttackActionVariant(
                id=f"2014-{monster.id}-multiattack-ranged", attack_kind="ranged",
                slots=[AttackActionSlot(attack_ids=[attack_id_2014(monster, ranged.id)]) for _ in range(3)],
            ),
        ]
    except Exception:
        logger.exception("Failed ammunition Multiattack source proof for %s.", monster.id)
        raise
