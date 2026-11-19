"""Source-semantic binding for no-impact-damage smothering attacks."""
from __future__ import annotations

import re

from app.content.monster_definition_adapter_support_2014 import attack_id_2014
from app.content.monster_source_2014 import SourceMonster2014
from app.content.monster_source_sections_2014 import source_sections_2014
from app.domain.actions import GrapplePeriodicDamage
from app.domain.capability_attack_definitions import AttackCapabilityDefinition
from app.domain.capability_effects import GrappleEffectDefinition
from app.domain.size import CreatureSize
from app.domain.weapons_base import DamageType

_SMOTHER = re.compile(
    # Full action shape, not heading or card identity, owns admission.
    r"Melee Weapon Attack: \+(?P<bonus>\d+) to hit, reach (?P<reach>\d+) ft\., "
    r"one (?P<size>\w+) or smaller creature\. Hit: The creature is grappled "
    r"\(escape DC (?P<dc>\d+)\)\. Until this grapple ends, the target is "
    r"restrained, blinded, and at risk of suffocating, and the (?P<owner>.+?) "
    r"can't smother another target\. In addition, at the start of each of the "
    r"target's turns, the target takes (?P<average>\d+) \((?P<count>\d+)d"
    r"(?P<die>\d+) \+ (?P<damage_bonus>\d+)\) (?P<damage_type>\w+) damage\.",
    re.IGNORECASE,
)


def source_proven_smother_attacks_2014(
    monster: SourceMonster2014,
) -> list[AttackCapabilityDefinition]:
    actions = source_sections_2014(monster.source_actions, include_continuations=True)
    output: list[AttackCapabilityDefinition] = []
    for heading in monster.action_names:
        match = _SMOTHER.fullmatch(actions.get(heading, ""))
        if match is None:
            continue
        try:
            size = CreatureSize(match["size"].lower())
            damage_type = DamageType(match["damage_type"].lower())
        except ValueError:
            continue
        count, die, bonus = (int(match[key]) for key in ("count", "die", "damage_bonus"))
        if int(match["average"]) != count * (die + 1) // 2 + bonus:
            continue
        source_id = re.sub(r"[^a-z0-9]+", "-", heading.lower()).strip("-")
        action_id = attack_id_2014(monster, source_id)
        output.append(AttackCapabilityDefinition(
            id=action_id, weapon_id=action_id, name=heading,
            attack_kind="melee", attack_bonus=int(match["bonus"]),
            reach_ft=int(match["reach"]), fixed_damage=0,
            damage_type=DamageType.BLUDGEONING, animation="slash",
            effects=[GrappleEffectDefinition(
                escape_dc=int(match["dc"]), max_target_size=size,
                restrains=True, blinds=True, requires_source_free=True,
                prevents_breathing=True,
                periodic_damage=GrapplePeriodicDamage(
                    source_name=heading, dice_count=count, dice_size=die,
                    damage_bonus=bonus, damage_type=damage_type.value,
                ),
            )],
        ))
    return output
