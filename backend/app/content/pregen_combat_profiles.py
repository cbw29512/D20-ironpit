from __future__ import annotations

from dataclasses import dataclass, replace

from app.content.barbarian_combat_levels import BARBARIAN_COMBAT_LEVELS
from app.content.cleric_combat_levels import CLERIC_COMBAT_LEVELS
from app.content.fighter_combat_levels import FIGHTER_COMBAT_LEVELS
from app.content.canonical_class_combat_spines import canonical_combat_features
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
    mastery_property: str | None = None
    sneak_attack_eligible: bool = False
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
    sneak_attack_d6: int = 0


def _scores(strength: int, dexterity: int, constitution: int, intelligence: int, wisdom: int, charisma: int) -> AbilityScores:
    return AbilityScores(strength=strength, dexterity=dexterity, constitution=constitution,
                         intelligence=intelligence, wisdom=wisdom, charisma=charisma)


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
    features = canonical_combat_features("fighter", level, "champion")
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


def _rokhan_profile(level: int, _legacy_hp: int | None = None) -> PregenCombatProfile:
    row = BARBARIAN_COMBAT_LEVELS[level]
    abilities = _scores(row.strength, row.dexterity, row.constitution, 10, 10, 10)
    return PregenCombatProfile(
        f"rokhan-stonefury-l{level}", "Barbarian", level, abilities, ("strength", "constitution"),
        row.armor_class, row.max_hp, row.speed_ft,
        (("athletics", row.proficiency_bonus + _modifier(row.strength)), ("acrobatics", _modifier(row.dexterity))),
        _ROKHAN_ATTACKS, row.weapon_masteries,
        (("rage", row.rage_uses), ("adrenaline-rush", row.proficiency_bonus), ("relentless-endurance", 1)),
        rage_damage_bonus=row.rage_damage_bonus,
    )


def _seraphine_profile(level: int, *_legacy: int) -> PregenCombatProfile:
    row = CLERIC_COMBAT_LEVELS[level]
    abilities = _scores(10, 10, 10, 14, row.wisdom, row.charisma)
    resources = [(f"spell-slot-{spell_level}", uses)
                 for spell_level, uses in enumerate(row.spell_slots, start=1) if uses]
    if row.channel_divinity_uses:
        resources.append(("channel-divinity", row.channel_divinity_uses))
    resources.extend((("adrenaline-rush", row.proficiency_bonus), ("relentless-endurance", 1)))
    return PregenCombatProfile(
        f"seraphine-dawnshield-l{level}", "Cleric", level, abilities, ("wisdom", "charisma"),
        row.armor_class, row.max_hp, 30,
        (("athletics", 0), ("acrobatics", 0),
         ("arcana", row.proficiency_bonus + 2), ("history", row.proficiency_bonus + 2),
         ("medicine", row.proficiency_bonus + _modifier(row.wisdom)),
         ("persuasion", row.proficiency_bonus + _modifier(row.charisma))),
        (AttackExpectation("mace", "strength", 1, 6, "bludgeoning"),), (), tuple(resources),
    )


def build_seraphine_dawnshield_level3_combat_profile() -> PregenCombatProfile:
    return _seraphine_profile(3)


def build_seraphine_dawnshield_level4_combat_profile() -> PregenCombatProfile:
    return _seraphine_profile(4)


def build_pregen_combat_profiles() -> dict[str, PregenCombatProfile]:
    from app.content.rogue_combat_fingerprint import build_mara_quickstep_combat_profile
    profiles = [
        *(_karnok_profile(level) for level in range(1, 13)),
        *(_rokhan_profile(level) for level in range(1, 7)),
        *(_seraphine_profile(level) for level in range(1, 5)),
        build_mara_quickstep_combat_profile(),
    ]
    return {profile.template_id: profile for profile in profiles}
