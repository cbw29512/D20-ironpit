from __future__ import annotations

from app.content.build_audit import assert_character_build_raw_ready
from app.content.canonical_hero_policy import assert_canonical_profile_policy
from app.content.canonical_spell_policy import canonical_spell_package
from app.content.paladin_devotion_2024_combat_profile import build_aurelia_2024_combat_profiles
from app.content.paladin_devotion_2024_profile import build_aurelia_brightshield_2024_profile
from app.content.paladin_devotion_2024_runtime import build_aurelia_brightshield_2024
from app.content.pregen_combat_audit import assert_pregen_combat_stats


def test_2024_paladin_level_one_is_raw_ready() -> None:
    profile = build_aurelia_brightshield_2024_profile(1)
    hero = build_aurelia_brightshield_2024(1)
    combat = build_aurelia_2024_combat_profiles()[0]

    assert profile.final_ability_scores.model_dump() == {
        "strength": 17, "dexterity": 10, "constitution": 14,
        "intelligence": 10, "wisdom": 10, "charisma": 14,
    }
    assert (hero.armor_class, hero.max_hp, hero.starts_with_heroic_inspiration) == (18, 12, True)
    assert hero.weapon_masteries == ["longsword", "javelin"]
    assert hero.weapon_attack.weapon.mastery_property == "Sap"
    assert hero.alternate_weapon_attacks[0].weapon.mastery_property == "Slow"
    assert {item.id: item.max_uses for item in hero.resources} == {"lay-on-hands": 5, "spell-slot-1": 2}

    lay_on_hands, cure_wounds = hero.healing_actions
    assert (lay_on_hands.action_cost, lay_on_hands.healing_bonus, lay_on_hands.resource_cost) == ("bonus_action", 5, 5)
    assert (cure_wounds.dice_count, cure_wounds.dice_size, cure_wounds.healing_bonus) == (2, 8, 2)
    assert hero.condition_removal_actions[0].resource_costs_per_condition == {"lay-on-hands": 5}

    divine_favor = hero.defensive_spell_actions[0]
    assert (divine_favor.id, divine_favor.action_cost, divine_favor.concentration) == ("divine-favor", "bonus_action", False)
    rider = divine_favor.modifier_effects[0]
    assert (rider.kind, rider.dice_count, rider.dice_size, rider.damage_type) == ("bonus-damage", 1, 4, "radiant")

    package = canonical_spell_package("paladin", 1, "2024", 2)
    assert package is not None
    assert [(spell.id, spell.role) for spell in package.spells] == [
        ("cure-wounds", "healing"), ("divine-favor", "damage"),
    ]

    assert_canonical_profile_policy(profile)
    assert_character_build_raw_ready(profile, hero)
    assert_pregen_combat_stats(hero, combat)
