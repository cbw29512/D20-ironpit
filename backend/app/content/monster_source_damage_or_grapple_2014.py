"""Printed damage-free melee attack alternative via existing Grapple primitive.

The printed source supplies hit bonus, reach, and escape DC. The engine's
normal attack/Grapple mechanics remain unchanged for every creature.
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

_SOURCE = re.compile(
    r"Melee Weapon Attack: \+(?P<hit>\d+) to hit, reach (?P<reach>\d+) ft\., "
    r"one creature\. Hit: (?P<average>\d+) \((?P<count>\d+)d(?P<size>\d+) "
    r"\+ (?P<bonus>\d+)\) (?P<kind>slashing|bludgeoning) damage\. "
    r"Instead of dealing damage, the (?P<actor>[a-z]+) can grapple the "
    r"target \(escape DC (?P<dc>\d+)\)\.",
    re.IGNORECASE,
)


def source_proven_damage_or_grapple_2014(
    monster: SourceMonster2014,
) -> list[AttackCapabilityDefinition]:
    """Represent the zero-damage branch as a normal universal Grapple hit."""
    try:
        sections = source_sections_2014(monster.source_actions, include_continuations=True)
        actions: list[AttackCapabilityDefinition] = []
        for attack in monster.attacks:
            text = sections.get(attack.name, "")
            match = _SOURCE.fullmatch(text)
            if match is None or attack.kind != "melee":
                continue
            if (
                int(match["hit"]) != attack.attack_bonus
                or int(match["reach"]) != attack.reach_ft
                or int(match["average"]) != attack.damage.average
                or int(match["count"]) != attack.damage.dice_count
                or int(match["size"]) != attack.damage.dice_size
                or int(match["bonus"]) != attack.damage.bonus
                or match["kind"].casefold() != str(attack.damage.type).casefold()
                or not 1 <= int(match["dc"]) <= 40
                or attack.on_hit_damage or attack.on_hit_save_effect
            ):
                continue
            identity = attack_id_2014(monster, attack.id) + "-grapple"
            actions.append(AttackCapabilityDefinition(
                id=identity, weapon_id=identity,
                name=attack.name + " (Grapple)",
                attack_kind="melee",
                attack_bonus=attack.attack_bonus,
                reach_ft=attack.reach_ft,
                # Zero damage is an existing valid attack carrier; it never
                # delivers damage of the placeholder type.
                fixed_damage=0, damage_type=DamageType.BLUDGEONING,
                animation="slash",
                effects=[GrappleEffectDefinition(escape_dc=int(match["dc"]))],
            ))
        return actions
    except Exception:
        logger.exception("2014 source damage-or-grapple binding failed for %s.", monster.id)
        raise
