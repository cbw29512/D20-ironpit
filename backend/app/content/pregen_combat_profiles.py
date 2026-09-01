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


_COMMON_FIGHTER = _scores(17, 13, 15, 10, 12, 8)
_ARCHER_FIGHTER = _scores(13, 17, 15, 10, 12, 8)
_ROGUE = _scores(10, 17, 15, 13, 12, 8)
_ORC = _scores(17, 13, 15, 8, 12, 10)
_KARNOK_ATTACKS = (
    AttackExpectation("greatsword", "strength", 2, 6, "slashing"),
    AttackExpectation("shortbow", "dexterity", 1, 6, "piercing", normal_range_ft=80, long_range_ft=320),
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
        PregenCombatProfile(
            "rokhan-stonefury-l1", "Barbarian", 1, _ORC, ("strength", "constitution"), 13, 14, 30,
            (("athletics", 5), ("acrobatics", 1)),
            (AttackExpectation("greataxe", "strength", 1, 12, "slashing"),
             AttackExpectation("handaxe", "strength", 1, 6, "slashing", normal_range_ft=20, long_range_ft=60)),
            ("flail", "pike"), (("rage", 2), ("adrenaline-rush", 2), ("relentless-endurance", 1)),
            rage_damage_bonus=2,
        ),
        PregenCombatProfile(
            "aldric-vane-l1", "Fighter", 1, _COMMON_FIGHTER, ("strength", "constitution"), 19, 12, 30,
            (("athletics", 5), ("acrobatics", 1)),
            (AttackExpectation("longsword", "strength", 1, 8, "slashing"),),
            ("greataxe", "greatsword", "halberd"), (("second-wind", 2),), "Defense",
        ),
        PregenCombatProfile(
            "brom-ironmark-l1", "Fighter", 1, _COMMON_FIGHTER, ("strength", "constitution"), 17, 12, 30,
            (("athletics", 5), ("acrobatics", 1)),
            (AttackExpectation("greataxe", "strength", 1, 12, "slashing"),),
            ("greataxe", "greatsword", "halberd"), (("second-wind", 2),), "Defense",
        ),
        PregenCombatProfile(
            "selene-asharrow-l1", "Fighter", 1, _ARCHER_FIGHTER, ("strength", "constitution"), 16, 12, 30,
            (("athletics", 1), ("acrobatics", 5)),
            (AttackExpectation("longbow", "dexterity", 1, 8, "piercing", normal_range_ft=150, long_range_ft=600, style_attack_bonus=2),),
            ("greataxe", "greatsword", "halberd"), (("second-wind", 2),), "Archery",
        ),
        PregenCombatProfile(
            "mara-quickstep-l1", "Rogue", 1, _ROGUE, ("dexterity", "intelligence"), 14, 10, 30,
            (("athletics", 0), ("acrobatics", 5)),
            (AttackExpectation("shortsword", "dexterity", 1, 6, "piercing", conditional_damage=((1, 6, "piercing"),)),
             AttackExpectation("shortbow", "dexterity", 1, 6, "piercing", normal_range_ft=80, long_range_ft=320, conditional_damage=((1, 6, "piercing"),))),
            ("dagger", "rapier"),
        ),
    ]
    return {profile.template_id: profile for profile in profiles}
