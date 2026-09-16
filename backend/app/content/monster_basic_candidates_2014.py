from __future__ import annotations

from collections import Counter

from app.content.arena_neutral_bonus_actions import is_arena_neutral_bonus_action
from app.content.monster_basic_attack_effects_2014 import supports_basic_attack_effects_2014
from app.content.monster_source_2014 import SourceMonster2014
from app.domain.traits import CombatTrait
from app.domain.weapons import DamageType

_MODELED_2014_TRAITS = {
    "Pack Tactics": CombatTrait.PACK_TACTICS,
    "Undead Fortitude": CombatTrait.UNDEAD_FORTITUDE,
}
_ARENA_NEUTRAL_TRAITS = frozenset({
    "Amphibious", "False Appearance", "Flyby", "Hold Breath", "Illumination",
    "Keen Hearing", "Keen Hearing and Smell", "Keen Hearing and Sight", "Keen Sight",
    "Keen Sight and Smell", "Keen Smell", "Mimicry", "Sunlight Sensitivity", "Water Breathing",
})
_DAMAGE_TYPES = frozenset(item.value for item in DamageType)


def _attack_blockers(monster: SourceMonster2014) -> list[str]:
    blockers: list[str] = []
    for attack in monster.attacks:
        if not attack.source_complete:
            blockers.append("attack:incomplete")
        if attack.damage.type not in _DAMAGE_TYPES:
            blockers.append("attack:damage-type")
        if not supports_basic_attack_effects_2014(attack):
            blockers.append("attack:complex")
        if attack.kind == "ranged" and (
            attack.normal_range_ft is None or attack.long_range_ft is None
        ):
            blockers.append("attack:range")
    return blockers


def _multiattack_blockers(monster: SourceMonster2014) -> list[str]:
    if monster.multiattack_policy is not None or monster.multiattack_binding is not None:
        return ["multiattack:complex"]
    attack_ids = {attack.id for attack in monster.attacks}
    if any(len(slot) != 1 or slot[0] not in attack_ids for slot in monster.multiattack_slots):
        return ["multiattack:choice-or-binding"]
    return []


def _source_name_blockers(monster: SourceMonster2014) -> list[str]:
    allowed_actions = {attack.name.casefold() for attack in monster.attacks}
    if monster.multiattack_slots:
        allowed_actions.add("multiattack")
    extras = [name for name in monster.action_names if name.casefold() not in allowed_actions]
    certified_traits = set(_ARENA_NEUTRAL_TRAITS) | set(_MODELED_2014_TRAITS)
    bad_traits = [
        name for name in monster.trait_names
        if name not in certified_traits and not is_arena_neutral_bonus_action(name)
    ]
    blockers = []
    if extras:
        blockers.append("source:extra-action")
    if bad_traits:
        blockers.append("source:trait")
    if monster.reaction_names or monster.parry_ac_bonus is not None:
        blockers.append("source:reaction")
    if monster.legendary_action_names:
        blockers.append("source:legendary")
    return blockers


def modeled_combat_traits_2014(monster: SourceMonster2014) -> list[CombatTrait]:
    return [
        runtime_trait for source_name, runtime_trait in _MODELED_2014_TRAITS.items()
        if source_name in monster.trait_names
    ]


def basic_blockers_2014(monster: SourceMonster2014) -> tuple[str, ...]:
    blockers: list[str] = []
    if not monster.attacks:
        blockers.append("attack:none")
    blockers.extend(_attack_blockers(monster))
    blockers.extend(_multiattack_blockers(monster))
    blockers.extend(_source_name_blockers(monster))
    families = {
        "defense": monster.unsupported_defense_text,
        "save-action": monster.saving_throw_actions,
        "swallow": monster.swallow_actions,
        "death-trigger": monster.death_trigger_actions,
        "healing": monster.healing_actions,
        "limited-use": monster.limited_action_uses,
        "spellcasting": monster.innate_spellcasting or monster.spellcasting,
        "zero-hp": monster.zero_hp_prevention,
        "regeneration": monster.regeneration,
        "legendary": monster.legendary_actions or monster.legendary_action_uses
            or monster.unsupported_legendary_action_names,
        "recharge": monster.action_recharges or monster.rest_recharge_action_ids,
    }
    blockers.extend(f"mechanic:{name}" for name, value in families.items() if value)
    return tuple(sorted(set(blockers)))


def is_basic_candidate_2014(monster: SourceMonster2014) -> bool:
    return not basic_blockers_2014(monster)


def blocker_counts_2014(monsters: tuple[SourceMonster2014, ...]) -> Counter[str]:
    return Counter(blocker for monster in monsters for blocker in basic_blockers_2014(monster))
