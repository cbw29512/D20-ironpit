from __future__ import annotations

from app.content.monster_basic_attack_effects_2014 import basic_attack_effects_2014
from app.content.monster_basic_candidates_2014 import (
    basic_blockers_2014, modeled_combat_traits_2014, supports_parry_reaction_2014,
)
from app.content.monster_charge_profile_2014 import charge_profile_2014
from app.content.monster_charge_source_corrections_2014 import corrected_charge_profile_2014
from app.content.monster_source_2014 import SourceAttack2014, SourceMonster2014
from app.content.monster_save_capabilities_2014 import (
    recharge_rules_2014, save_capabilities_2014, save_resources_2014,
)
from app.domain.capabilities import CombatantDefinition
from app.domain.capability_attacks import (
    AttackCapabilityDefinition,
    CapabilityActionSlot,
    MultiattackCapabilityDefinition,
)
from app.domain.capability_effects import DiceSpec
from app.domain.character_builds import AbilityScores
from app.domain.combatants import VisualLoadout
from app.domain.movement import MovementModes
from app.domain.reactions import ParryReaction
from app.domain.size import CreatureSize

_ABILITY_KEYS = {
    "str": "strength", "dex": "dexterity", "con": "constitution",
    "int": "intelligence", "wis": "wisdom", "cha": "charisma",
}
_FULL_ABILITIES = tuple(_ABILITY_KEYS.values())


def _ability_values(monster: SourceMonster2014) -> dict[str, int]:
    normalized = {_ABILITY_KEYS.get(key.lower(), key.lower()): value for key, value in monster.abilities.items()}
    missing = set(_FULL_ABILITIES) - set(normalized)
    if missing:
        raise ValueError(f"{monster.id} is missing ability scores: {sorted(missing)}")
    return {name: int(normalized[name]) for name in _FULL_ABILITIES}


def _save_bonuses(monster: SourceMonster2014, scores: AbilityScores) -> dict[str, int]:
    bonuses = {name: scores.modifier(name) for name in _FULL_ABILITIES}
    for key, value in monster.saving_throws.items():
        name = _ABILITY_KEYS.get(key.lower(), key.lower())
        if name not in bonuses:
            raise ValueError(f"{monster.id} has unknown saving throw ability {key!r}")
        bonuses[name] = int(value)
    return bonuses


def _movement(monster: SourceMonster2014) -> MovementModes:
    speed = {key.lower().replace("_ft", ""): int(value) for key, value in monster.speed.items()}
    return MovementModes(
        walk_ft=speed.get("walk", speed.get("speed", 0)),
        fly_ft=speed.get("fly", 0),
        climb_ft=speed.get("climb", 0),
        swim_ft=speed.get("swim", 0),
        burrow_ft=speed.get("burrow", 0),
    )


def _attack_id(monster: SourceMonster2014, attack: SourceAttack2014) -> str:
    return f"2014-{monster.id}-{attack.id}".replace("--", "-")


def _attack(monster: SourceMonster2014, attack: SourceAttack2014) -> AttackCapabilityDefinition:
    charge_source = corrected_charge_profile_2014(monster, attack)
    kwargs = {
        "id": _attack_id(monster, attack),
        "weapon_id": _attack_id(monster, attack),
        "name": attack.name,
        "attack_kind": attack.kind,
        "attack_bonus": attack.attack_bonus,
        "damage_type": str(attack.damage.type).lower(),
        "animation": "projectile" if attack.kind == "ranged" else "slash",
        "reach_ft": attack.reach_ft,
        "effects": basic_attack_effects_2014(attack),
        "charge_profile": charge_profile_2014(charge_source, monster_id=monster.id),
        "forbid_target_grappled_by_self": attack.forbid_target_grappled_by_self,
    }
    if attack.damage.dice_count:
        kwargs["damage"] = DiceSpec(
            count=attack.damage.dice_count,
            size=attack.damage.dice_size,
            bonus=attack.damage.bonus,
        )
    else:
        kwargs["fixed_damage"] = attack.damage.average
    if attack.kind == "ranged":
        kwargs["normal_range_ft"] = attack.normal_range_ft
        kwargs["long_range_ft"] = attack.long_range_ft
        kwargs["projectile"] = "projectile"
    return AttackCapabilityDefinition(**kwargs)


def _multiattack(monster: SourceMonster2014) -> MultiattackCapabilityDefinition | None:
    if not monster.multiattack_slots:
        return None
    attack_by_source = {attack.id: _attack_id(monster, attack) for attack in monster.attacks}
    return MultiattackCapabilityDefinition(
        id=f"2014-{monster.id}-multiattack",
        name="Multiattack",
        is_attack_action=True,
        slots=[CapabilityActionSlot(attack_ids=[attack_by_source[slot[0]]]) for slot in monster.multiattack_slots],
    )


def adapt_basic_monster_2014(monster: SourceMonster2014) -> CombatantDefinition:
    blockers = basic_blockers_2014(monster)
    if blockers:
        raise ValueError(f"{monster.id} is not a basic 2014 candidate: {', '.join(blockers)}")
    scores = AbilityScores(**_ability_values(monster))
    movement = _movement(monster)
    attacks = [_attack(monster, attack) for attack in monster.attacks]
    return CombatantDefinition(
        id=f"2014-{monster.id}", name=monster.name, archetype=f"2014 {monster.creature_type}",
        challenge_rating=monster.challenge_rating, kind="monster", ruleset="2014",
        size=CreatureSize(monster.size.lower()), ability_scores=scores,
        armor_class=monster.armor_class, max_hp=monster.max_hp, speed_ft=movement.walk_ft,
        movement_modes=movement, initiative_bonus=scores.modifier("dexterity"), attacks=attacks,
        primary_attack_id=attacks[0].id, attack_action=_multiattack(monster),
        save_actions=save_capabilities_2014(monster),
        resources=save_resources_2014(monster), recharge_rules=recharge_rules_2014(monster),
        combat_traits=modeled_combat_traits_2014(monster),
        saving_throw_bonuses=_save_bonuses(monster, scores),
        skill_bonuses={key.lower(): int(value) for key, value in monster.skills.items()},
        source_trait_names=list(monster.trait_names), source_reaction_names=list(monster.reaction_names),
        parry_reaction=ParryReaction(ac_bonus=monster.parry_ac_bonus)
            if supports_parry_reaction_2014(monster) else None,
        damage_resistances=[item.lower() for item in monster.damage_resistances],
        damage_vulnerabilities=[item.lower() for item in monster.damage_vulnerabilities],
        damage_immunities=[item.lower() for item in monster.damage_immunities],
        condition_immunities=[item.lower() for item in monster.condition_immunities],
        visual=VisualLoadout(armor=monster.creature_type, main_hand=monster.attacks[0].name, body_style=monster.creature_type),
        source=f"SRD 5.1 (2014) {monster.name}",
    )