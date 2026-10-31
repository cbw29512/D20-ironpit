"""2014 source grammar: ranged attack whose only on-hit damage follows a save.

One generic attack-roll + on-hit save-damage shape. Immutable card is the
sole authority for attack bonus, range, DC, dice, type and success outcome.
"""
from __future__ import annotations

import logging
import re

from app.content.monster_definition_adapter_support_2014 import attack_id_2014
from app.content.monster_source_2014 import SourceMonster2014
from app.content.monster_source_sections_2014 import source_sections_2014
from app.domain.capability_attack_definitions import AttackCapabilityDefinition
from app.domain.capability_effects import DiceSpec, SaveDamageEffectDefinition
from app.domain.weapons_base import DamageType

logger = logging.getLogger(__name__)

# Anchored to a whole printed action. The heading is never a runtime switch.
_RANGED_SAVE_ONLY_HIT = re.compile(
    r"Ranged Weapon Attack: \\+(?P<hit>\\d+) to hit, "
    r"range (?P<short>\\d+)/(?P<long>\\d+) ft\\., one creature\\. "
    r"Hit: The target must make a DC (?P<dc>\\d+) "
    r"(?P<ability>Strength|Dexterity|Constitution|Intelligence|Wisdom|Charisma) "
    r"saving throw, taking (?P<average>\\d+) "
    r"\\((?P<count>\\d+)d(?P<size>\\d+)\\) "
    r"(?P<damage_type>acid|bludgeoning|cold|fire|force|lightning|necrotic|"
    r"piercing|poison|psychic|radiant|slashing|thunder) damage "
    r"on a failed save, or half as much damage on a successful one\\.",
    re.IGNORECASE,
)


def source_ranged_save_only_hit_attacks_2014(
    monster: SourceMonster2014,
) -> list[AttackCapabilityDefinition]:
    """Compile only source-complete ordinary-hit/failed-or-half save Actions."""
    try:
        printed_attacks = {attack.name.casefold() for attack in monster.attacks}
        source = source_sections_2014(
            monster.source_actions, include_continuations=True,
        )
        actions: list[AttackCapabilityDefinition] = []
        for heading in monster.action_names:
            if heading.casefold() in printed_attacks:
                continue
            body = source.get(heading)
            if body is None:
                continue
            match = _RANGED_SAVE_ONLY_HIT.fullmatch(body)
            if match is None:
                continue
            v = match.groupdict()
            count, die_size = int(v["count"]), int(v["size"])
            # Verify the printed 2014 damage average against its dice.
            if count < 1 or die_size < 2 or count > 40 or die_size > 100:
                continue
            if int(v["average"]) != count * (die_size + 1) // 2:
                continue
            short, long = int(v["short"]), int(v["long"])
            if short < 1 or long < short:
                continue
            source_id = re.sub(r"[^a-z0-9]+", "-", heading.lower()).strip("-")
            action_id = attack_id_2014(monster, source_id)
            actions.append(AttackCapabilityDefinition(
                id=action_id, weapon_id=action_id, name=heading,
                attack_kind="ranged", attack_bonus=int(v["hit"]),
                normal_range_ft=short, long_range_ft=long,
                projectile="projectile", animation="projectile",
                fixed_damage=0, damage_type=DamageType(v["damage_type"].lower()),
                effects=[SaveDamageEffectDefinition(
                    source=heading, save_ability=v["ability"].lower(),
                    dc=int(v["dc"]), dice=DiceSpec(count=count, size=die_size),
                    damage_type=DamageType(v["damage_type"].lower()),
                    success_damage="half",
                )],
            ))
        return actions
    except Exception:
        logger.exception("Failed source-only ranged attack/save binding for %s.", monster.id)
        raise
