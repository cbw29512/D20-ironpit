from __future__ import annotations

from app.content.barbarian_combat_levels import BARBARIAN_COMBAT_LEVELS
from app.content.cleric_combat_levels import CLERIC_COMBAT_LEVELS
from app.content.fighter_combat_levels import FIGHTER_COMBAT_LEVELS
from app.content.pregen_combat_audit import AttackExpectation, PregenCombatProfile


def _modifier(score: int) -> int:
    return (score - 10) // 2


def _scores(strength: int, dexterity: int, constitution: int, intelligence: int, wisdom: int, charisma: int) -> tuple[tuple[str, int], ...]:
    return (
        ("strength", strength), ("dexterity", dexterity), ("constitution", constitution),
        ("intelligence", intelligence), ("wisdom", wisdom), ("charisma", charisma),
    )


_KARNOK_ATTACKS = (
    AttackExpectation("longsword", "strength", 1, 8, "slashing"),
    AttackExpectation("longbow", "dexterity", 1, 8, "piercing"),
)
_ROKHAN_ATTACKS = (
    AttackExpectation("greataxe", "strength", 1, 12, "slashing"),
    AttackExpectation("handaxe", "strength", 1, 6, "slashing"),
)


def _karnok_profile(level: int) -> PregenCombatProfile:
    row = FIGHTER_COMBAT_LEVELS[level]
    abilities = _scores(row.strength, row.dexterity, row.constitution, 10, 10, 10)
    return PregenCombatProfile(
        f"karnok-stoneward-l{level}", "Fighter", level, abilities, ("strength", "constitution"),
        row.armor_class, row.max_hp, 30,
        (("athletics", row.proficiency_bonus + _modifier(row.strength)), ("acrobatics", _modifier(row.dexterity))),
        _KARNOK_ATTACKS, row.weapon_masteries,
        (("second-wind", row.second_wind_uses),),
    )


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
        *(_karnok_profile(level) for level in range(1, 15)),
        *(_rokhan_profile(level) for level in range(1, 8)), *(_seraphine_profile(level) for level in range(1, 5)),
        build_mara_quickstep_combat_profile(),
    ]
    return {profile.template_id: profile for profile in profiles}
