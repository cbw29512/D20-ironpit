from __future__ import annotations

from dataclasses import dataclass

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
    return AbilityScores(
        strength=strength, dexterity=dexterity, constitution=constitution,
        intelligence=intelligence, wisdom=wisdom, charisma=charisma,
    )


_ORC = _scores(17, 13, 15, 8, 12, 10)
_SERAPHINE = _scores(12, 14, 14, 8, 17, 10)
_KARNOK_L4 = _scores(18, 13, 16, 8, 12, 10)
_KARNOK_ATTACKS = (
    AttackExpectation("greatsword", "strength", 2, 6, "slashing"),
    AttackExpectation("shortbow", "dexterity", 1, 6, "piercing", normal_range_ft=80, long_range_ft=320),
)


def build_karnok_stoneward_level4_combat_profile() -> PregenCombatProfile:
    return PregenCombatProfile(
        "karnok-stoneward-l4", "Fighter", 4, _KARNOK_L4, ("strength", "constitution"), 17, 40, 30,
        (("athletics", 6), ("acrobatics", 1)), _KARNOK_ATTACKS,
        ("flail", "javelin", "spear", "longsword"),
        (("second-wind", 3), ("action-surge", 1), ("adrenaline-rush", 2), ("relentless-endurance", 1)),
        "Defense",
    )


def build_karnok_stoneward_level5_combat_profile() -> PregenCombatProfile:
    return PregenCombatProfile(
        "karnok-stoneward-l5", "Fighter", 5, _KARNOK_L4, ("strength", "constitution"), 17, 49, 30,
        (("athletics", 7), ("acrobatics", 1)), _KARNOK_ATTACKS,
        ("flail", "javelin", "spear", "longsword"),
        (("second-wind", 3), ("action-surge", 1), ("adrenaline-rush", 3), ("relentless-endurance", 1)),
        "Defense",
    )


def _seraphine_profile(level: int, hp: int, slots: int, channel: int = 0) -> PregenCombatProfile:
    resources = [("spell-slot-1", slots)]
    if channel:
        resources.append(("channel-divinity", channel))
    resources.extend((("adrenaline-rush", 2), ("relentless-endurance", 1)))
    return PregenCombatProfile(
        f"seraphine-dawnshield-l{level}", "Cleric", level, _SERAPHINE, ("wisdom", "charisma"), 17, hp, 30,
        (("athletics", 1), ("acrobatics", 2), ("arcana", 1), ("history", 1), ("medicine", 5), ("persuasion", 2)),
        (AttackExpectation("mace", "strength", 1, 6, "bludgeoning"),), (), tuple(resources),
    )


def build_pregen_combat_profiles() -> dict[str, PregenCombatProfile]:
    profiles = [
        PregenCombatProfile(
            "karnok-stoneward-l1", "Fighter", 1, _ORC, ("strength", "constitution"), 17, 12, 30,
            (("athletics", 5), ("acrobatics", 1)), _KARNOK_ATTACKS,
            ("flail", "javelin", "spear"), (("second-wind", 2), ("adrenaline-rush", 2), ("relentless-endurance", 1)),
            "Defense",
        ),
        PregenCombatProfile(
            "karnok-stoneward-l2", "Fighter", 2, _ORC, ("strength", "constitution"), 17, 20, 30,
            (("athletics", 5), ("acrobatics", 1)), _KARNOK_ATTACKS,
            ("flail", "javelin", "spear"),
            (("second-wind", 2), ("action-surge", 1), ("adrenaline-rush", 2), ("relentless-endurance", 1)),
            "Defense",
        ),
        PregenCombatProfile(
            "karnok-stoneward-l3", "Fighter", 3, _ORC, ("strength", "constitution"), 17, 28, 30,
            (("athletics", 5), ("acrobatics", 1)), _KARNOK_ATTACKS,
            ("flail", "javelin", "spear"),
            (("second-wind", 2), ("action-surge", 1), ("adrenaline-rush", 2), ("relentless-endurance", 1)),
            "Defense",
        ),
        build_karnok_stoneward_level4_combat_profile(),
        build_karnok_stoneward_level5_combat_profile(),
        PregenCombatProfile(
            "rokhan-stonefury-l1", "Barbarian", 1, _ORC, ("strength", "constitution"), 13, 14, 30,
            (("athletics", 5), ("acrobatics", 1)),
            (AttackExpectation("greataxe", "strength", 1, 12, "slashing"),
             AttackExpectation("handaxe", "strength", 1, 6, "slashing", normal_range_ft=20, long_range_ft=60)),
            ("flail", "pike"), (("rage", 2), ("adrenaline-rush", 2), ("relentless-endurance", 1)),
            rage_damage_bonus=2,
        ),
        _seraphine_profile(1, 10, 2),
        _seraphine_profile(2, 17, 3, 2),
    ]
    return {profile.template_id: profile for profile in profiles}
