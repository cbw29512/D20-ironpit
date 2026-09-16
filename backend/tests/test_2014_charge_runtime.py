from app.combat.charge import _charged_attack
from app.combat.charge_profiles import charge_profile_for_attack
from app.content.monster_roster_2014 import build_basic_2014_monsters


def _monster(monster_id: str):
    return next(monster for monster in build_basic_2014_monsters() if monster.id == monster_id)


def _attack(monster_id: str, attack_id: str):
    monster = _monster(monster_id)
    return next(
        attack for attack in [monster.weapon_attack, *monster.alternate_weapon_attacks]
        if attack.id == attack_id
    )


def test_2014_elk_charge_maps_strength_save_to_prone() -> None:
    attack = _attack("2014-elk", "2014-elk-ram")
    profile = charge_profile_for_attack(attack)
    assert profile is not None
    assert profile.minimum_move_ft == 20
    assert profile.prone_save_ability == "strength"
    assert profile.prone_save_dc == 13
    charged = _charged_attack(attack, profile)
    assert charged.on_hit_condition_save is not None
    assert charged.on_hit_condition_save.save_ability == "strength"
    assert charged.on_hit_condition_save.dc == 13
    assert charged.on_hit_condition_save.condition_id == "prone"
    assert charged.knocks_prone_max_size is None


def test_2014_minotaur_skeleton_charge_is_damage_only() -> None:
    attack = _attack("2014-minotaur-skeleton", "2014-minotaur-skeleton-gore")
    profile = charge_profile_for_attack(attack)
    assert profile is not None and profile.bonus_damage is not None
    assert profile.minimum_move_ft == 10
    assert (profile.bonus_damage.dice_count, profile.bonus_damage.dice_size) == (2, 8)
    assert profile.bonus_damage.damage_type.value == "piercing"
    assert profile.prone_save_ability is None
    assert profile.prone_save_dc is None
    charged = _charged_attack(attack, profile)
    assert charged.on_hit_condition_save is None
    assert charged.knocks_prone_max_size is None
