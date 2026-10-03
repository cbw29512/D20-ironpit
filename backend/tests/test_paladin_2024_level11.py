from __future__ import annotations

from app.combat.damage import resolve_weapon_damage
from app.combat.dice import FixedDiceProvider
from app.combat.state import build_combatant_state
from app.content.build_audit import assert_character_build_raw_ready
from app.content.canonical_hero_policy import assert_canonical_profile_policy
from app.content.canonical_spell_policy import canonical_spell_package
from app.content.paladin_devotion_2024_combat_profile import build_aurelia_2024_combat_profiles
from app.content.paladin_devotion_2024_profile import build_aurelia_brightshield_2024_profile
from app.content.paladin_devotion_2024_runtime import build_aurelia_brightshield_2024
from app.content.pregen_combat_audit import assert_pregen_combat_stats
from app.domain.models import RollMode


def test_2024_paladin_level_eleven_progression_is_raw_ready() -> None:
    profile = build_aurelia_brightshield_2024_profile(11)
    hero = build_aurelia_brightshield_2024(11)
    combat = next(
        item for item in build_aurelia_2024_combat_profiles() if item.level == 11
    )

    assert profile.final_ability_scores.strength == 20
    assert profile.final_ability_scores.charisma == 15
    assert (hero.max_hp, hero.armor_class) == (92, 19)
    assert hero.weapon_attack.attack_bonus == 9
    assert hero.weapon_attack.damage_bonus == 5
    assert hero.skill_bonuses["athletics"] == 9
    assert {item.id: item.max_uses for item in hero.resources} == {
        "lay-on-hands": 55,
        "spell-slot-1": 4,
        "paladins-smite-free-cast": 1,
        "channel-divinity": 3,
        "spell-slot-2": 3,
        "faithful-steed-free-cast": 1,
        "spell-slot-3": 3,
    }

    package = canonical_spell_package("paladin", 11, "2024", 2)
    assert package is not None
    assert [spell.id for spell in package.spells] == [
        "cure-wounds", "divine-favor", "bless", "searing-smite",
        "thunderous-smite", "shining-smite", "lesser-restoration",
        "aura-of-vitality", "blinding-smite", "crusaders-mantle",
    ]

    assert len(hero.weapon_attack.on_hit_damage) == 1
    rider = hero.weapon_attack.on_hit_damage[0]
    assert (rider.source, rider.dice_count, rider.dice_size, rider.damage_type.value) == (
        "Radiant Strikes", 1, 8, "radiant",
    )
    assert hero.alternate_weapon_attacks[0].on_hit_damage == []

    audits = {item.feature_id: item for item in profile.feature_audits}
    assert audits["radiant-strikes"].automated is True
    assert audits["crusaders-mantle"].automated is False

    assert_canonical_profile_policy(profile)
    assert_character_build_raw_ready(profile, hero)
    assert_pregen_combat_stats(hero, combat)


def test_2024_radiant_strikes_rolls_and_critically_doubles_without_resource_cost() -> None:
    state = build_combatant_state(build_aurelia_brightshield_2024(11))
    before = {item.id: item.current_uses for item in state.resources}

    _, components = resolve_weapon_damage(
        state,
        state.template.weapon_attack,
        FixedDiceProvider([4, 7]),
        False,
        RollMode.NORMAL,
        "1:aurelia-radiant-strikes",
    )
    rider = next(item for item in components if item.source == "Radiant Strikes")
    assert rider.notation == "1d8+0"
    assert {item.id: item.current_uses for item in state.resources} == before

    _, critical_components = resolve_weapon_damage(
        state,
        state.template.weapon_attack,
        FixedDiceProvider([4, 5, 7, 8]),
        True,
        RollMode.NORMAL,
        "1:aurelia-radiant-strikes-crit",
    )
    critical_rider = next(
        item for item in critical_components if item.source == "Radiant Strikes"
    )
    assert critical_rider.notation == "2d8+0"


def test_level_ten_snapshot_remains_stable_after_level_eleven() -> None:
    level10 = build_aurelia_brightshield_2024(10)
    assert level10.max_hp == 84
    assert level10.weapon_attack.attack_bonus == 9
    assert level10.weapon_attack.on_hit_damage == []
    assert next(
        item for item in level10.resources if item.id == "channel-divinity"
    ).max_uses == 2
    assert next(
        item for item in level10.resources if item.id == "spell-slot-3"
    ).max_uses == 2
