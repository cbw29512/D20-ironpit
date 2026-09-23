from __future__ import annotations

from app.content.monk_open_hand_2014_combat_profile import build_kael_2014_combat_profile
from app.content.monk_open_hand_2014_profile import build_kael_stillwater_2014_profile
from app.content.monk_open_hand_2014_runtime import build_kael_stillwater_2014


def test_level19_asi_recompiles_all_changed_combat_values() -> None:
    profile = build_kael_stillwater_2014_profile(19)
    combat = build_kael_2014_combat_profile(19)
    hero = build_kael_stillwater_2014(19)

    assert profile.final_ability_scores == combat.abilities == hero.ability_scores
    assert hero.ability_scores.strength == 14
    assert hero.ability_scores.dexterity == 20
    assert hero.ability_scores.constitution == 14
    assert hero.ability_scores.wisdom == 20

    assert hero.armor_class == 20
    assert hero.max_hp == 136
    assert hero.speed_ft == 55
    assert hero.initiative_bonus == 5

    assert {item.id: item.max_uses for item in hero.resources} == {
        "ki": 19,
        "wholeness-of-body": 1,
    }
    assert hero.saving_throw_bonuses == {
        "strength": 8,
        "dexterity": 11,
        "constitution": 8,
        "intelligence": 6,
        "wisdom": 11,
        "charisma": 5,
    }
    assert hero.skill_bonuses == {
        "acrobatics": 11,
        "stealth": 11,
        "insight": 11,
        "religion": 6,
    }

    attacks = [hero.weapon_attack, *hero.alternate_weapon_attacks]
    assert all(attack.attack_bonus == 11 for attack in attacks)
    assert all(attack.damage_bonus == 5 for attack in attacks)
    assert hero.weapon_attack.weapon.dice_size == 10

    assert hero.progression_features.opening_targeting_ward is not None
    assert hero.progression_features.opening_targeting_ward.save_dc == 19
    assert hero.progression_features.deferred_save_effect is not None
    assert hero.progression_features.deferred_save_effect.save_dc == 19

    assert hero.timed_self_buff_actions[0].id == "empty-body"
    audit = next(item for item in profile.feature_audits if item.feature_id == "ability-score-improvement-l19")
    assert audit.automated is True
    assert "+1 Wisdom, +1 Strength" in audit.feature_name
