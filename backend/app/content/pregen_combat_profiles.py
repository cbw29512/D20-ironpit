from __future__ import annotations

from dataclasses import dataclass, replace

from app.content.fighter_combat_levels import FIGHTER_COMBAT_LEVELS, fighter_combat_features
from app.domain.character_builds import AbilityScores


@dataclass(frozen=True)
class AttackExpectation:
    weapon_id: str
    ability: str
    dice_count: int
    dice_size: int
    damage_type: str
    reach_ft: int = 5
    normal_range_ft: int | None = None
    long_range_ft: int | None = None
    style_attack_bonus: int = 0
    damage_die_minimum: int | None = None
    conditional_damage: tuple[tuple[int, int, str], ...] = ()


@dataclass(frozen=True)
class PregenCombatProfile:
    template_id: str
    archetype: str
    level: int
    abilities: AbilityScores
    save_proficiencies: tuple[str, ...]
    armor_class: int
    max_hp: int
    speed_ft: int
    skill_bonuses: tuple[tuple[str, int], ...]
    attacks: tuple[AttackExpectation, ...]
    weapon_masteries: tuple[str, ...]
    resources: tuple[tuple[str, int], ...] = ()
    fighting_style: str | None = None
    rage_damage_bonus: int = 0


def _scores(strength: int, dexterity: int, constitution: int, intelligence: int, wisdom: int, charisma: int) -> AbilityScores:
    return AbilityScores(strength=strength, dexterity=dexterity, constitution=constitution,
                         intelligence=intelligence, wisdom=wisdom, charisma=charisma)


_ORC = _scores(17, 13, 15, 10, 10, 10)
_ORC_L4 = _scores(18, 13, 16, 10, 10, 10)
_SERAPHINE = _scores(10, 10, 10, 14, 17, 14)
_SERAPHINE_L4 = _scores(10, 10, 10, 14, 19, 14)
_KARNOK_ATTACKS = (
    AttackExpectation("greatsword", "strength", 2, 6, "slashing"),
    AttackExpectation("shortbow", "dexterity", 1, 6, "piercing", normal_range_ft=80, long_range_ft=320),
)
_ROKHAN_ATTACKS = (
    AttackExpectation("greataxe", "strength", 1, 12, "slashing"),
    AttackExpectation("handaxe", "strength", 1, 6, "slashing", normal_range_ft=20, long_range_ft=60),
)


def _modifier(score: int) -> int:
    return (score - 10) // 2


def _karnok_profile(level: int, _legacy_hp: int | None = None) -> PregenCombatProfile:
    row = FIGHTER_COMBAT_LEVELS[level]
    abilities = _scores(row.strength, row.dexterity, row.constitution, 10, 10, 10)
    resources = [("second-wind", row.second_wind_uses)]
    if row.action_surge_uses:
        resources.append(("action-surge", row.action_surge_uses))
    if row.indomitable_uses:
        resources.append(("indomitable", row.indomitable_uses))
    resources.extend((("adrenaline-rush", row.proficiency_bonus), ("relentless-endurance", 1)))
    features = fighter_combat_features(level)
    attacks = (replace(_KARNOK_ATTACKS[0], damage_die_minimum=3), _KARNOK_ATTACKS[1]) if "great-weapon-fighting" in features else _KARNOK_ATTACKS
    return PregenCombatProfile(
        f"karnok-stoneward-l{level}", "Fighter", level, abilities, ("strength", "constitution"),
        row.armor_class, row.max_hp, 30,
        (("athletics", row.proficiency_bonus + _modifier(row.strength)), ("acrobatics", _modifier(row.dexterity))),
        attacks, row.weapon_masteries, tuple(resources), "Defense",
    )


def build_karnok_stoneward_level4_combat_profile() -> PregenCombatProfile:
    return _karnok_profile(4)


def build_karnok_stoneward_level5_combat_profile() -> PregenCombatProfile:
    return _karnok_profile(5)


def build_karnok_stoneward_level6_combat_profile() -> PregenCombatProfile:
    return _karnok_profile(6)


def build_karnok_stoneward_level7_combat_profile() -> PregenCombatProfile:
    return _karnok_profile(7)


def _rokhan_profile(level: int, hp: int) -> PregenCombatProfile:
    advanced = level >= 4
    abilities = _ORC_L4 if advanced else _ORC
    athletics = 7 if level >= 5 else 6 if advanced else 5
    masteries = ("flail", "pike", "longsword") if advanced else ("flail", "pike")
    rage_uses = 4 if level >= 6 else 3 if level >= 3 else 2
    return PregenCombatProfile(
        f"rokhan-stonefury-l{level}", "Barbarian", level, abilities, ("strength", "constitution"), 14 if advanced else 13, hp, 40 if level >= 5 else 30,
        (("athletics", athletics), ("acrobatics", 1)), _ROKHAN_ATTACKS, masteries,
        (("rage", rage_uses), ("adrenaline-rush", 3 if level >= 5 else 2), ("relentless-endurance", 1)), rage_damage_bonus=2,
    )


def _seraphine_profile(level: int, hp: int, first_slots: int, channel: int = 0, second_slots: int = 0) -> PregenCombatProfile:
    resources = [("spell-slot-1", first_slots)]
    if second_slots:
        resources.append(("spell-slot-2", second_slots))
    if channel:
        resources.append(("channel-divinity", channel))
    resources.extend((("adrenaline-rush", 2), ("relentless-endurance", 1)))
    return PregenCombatProfile(
        f"seraphine-dawnshield-l{level}", "Cleric", level, _SERAPHINE, ("wisdom", "charisma"), 15, hp, 30,
        (("athletics", 0), ("acrobatics", 0), ("arcana", 4), ("history", 4), ("medicine", 5), ("persuasion", 4)),
        (AttackExpectation("mace", "strength", 1, 6, "bludgeoning"),), (), tuple(resources),
    )


def build_seraphine_dawnshield_level3_combat_profile() -> PregenCombatProfile:
    return _seraphine_profile(3, 18, 4, 2, 2)


def build_seraphine_dawnshield_level4_combat_profile() -> PregenCombatProfile:
    return PregenCombatProfile(
        "seraphine-dawnshield-l4", "Cleric", 4, _SERAPHINE_L4, ("wisdom", "charisma"), 15, 23, 30,
        (("athletics", 0), ("acrobatics", 0), ("arcana", 4), ("history", 4), ("medicine", 6), ("persuasion", 4)),
        (AttackExpectation("mace", "strength", 1, 6, "bludgeoning"),), (),
        (("spell-slot-1", 4), ("spell-slot-2", 3), ("channel-divinity", 2),
         ("adrenaline-rush", 2), ("relentless-endurance", 1)),
    )


def build_pregen_combat_profiles() -> dict[str, PregenCombatProfile]:
    profiles = [
        *(_karnok_profile(level) for level in range(1, 9)),
        _rokhan_profile(1, 14), _rokhan_profile(2, 23), _rokhan_profile(3, 32), _rokhan_profile(4, 45),
        _rokhan_profile(5, 55), _rokhan_profile(6, 65),
        _seraphine_profile(1, 8, 2), _seraphine_profile(2, 13, 3, 2),
        build_seraphine_dawnshield_level3_combat_profile(), build_seraphine_dawnshield_level4_combat_profile(),
    ]
    return {profile.template_id: profile for profile in profiles}
