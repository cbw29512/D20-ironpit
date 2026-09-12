import json

from app.combat.attacks import resolve_attack
from app.combat.damage_defenses import adjusted_damage_amount
from app.combat.dice import FixedDiceProvider
from app.combat.state import build_combatant_state
from app.content.monster_catalog_2014 import load_catalog_2014, monster_by_id_2014
from app.domain.models import DamageType


def test_mvp_catalog_loads_and_uses_json_stats() -> None:
    catalog = load_catalog_2014()
    assert {monster.id for monster in catalog} == {"goblin", "skeleton", "brown-bear", "bandit"}

    goblin = monster_by_id_2014("goblin")
    assert goblin.armor_class == 15
    assert goblin.max_hp == 7
    assert goblin.speed_ft == 30
    assert goblin.ability_scores.dexterity == 14
    assert goblin.weapon_attack.weapon.name == "Scimitar"
    assert goblin.alternate_weapon_attacks[0].weapon.name == "Shortbow"
    assert goblin.alternate_weapon_attacks[0].weapon.normal_range_ft == 80
    assert goblin.alternate_weapon_attacks[0].weapon.long_range_ft == 320


def test_json_ranged_attack_runs_through_universal_resolver() -> None:
    attacker = build_combatant_state(monster_by_id_2014("goblin"))
    defender = build_combatant_state(monster_by_id_2014("skeleton"))
    shortbow = attacker.template.alternate_weapon_attacks[0]

    event = resolve_attack(
        1, 1, attacker, defender, shortbow, 80,
        FixedDiceProvider([10, 4]),
    )

    assert event.hit is True
    assert defender.current_hp == 7


def test_json_defenses_feed_shared_damage_engine() -> None:
    skeleton = build_combatant_state(monster_by_id_2014("skeleton"))
    assert adjusted_damage_amount(5, DamageType.BLUDGEONING, skeleton) == 10
    assert adjusted_damage_amount(5, DamageType.POISON, skeleton) == 0
    assert adjusted_damage_amount(5, DamageType.PIERCING, skeleton) == 5


def test_runtime_state_is_fresh_for_each_fight() -> None:
    template = monster_by_id_2014("brown-bear")
    first = build_combatant_state(template)
    second = build_combatant_state(template)
    first.current_hp = 1

    assert second.current_hp == 34
    assert template.max_hp == 34


def test_new_basic_monster_is_data_only(tmp_path) -> None:
    record = {
        "id": "test-brute", "name": "Test Brute", "ruleset": "2014",
        "size": "Medium", "creature_type": "humanoid", "alignment": "unaligned",
        "armor_class": 14, "max_hp": 20, "hit_dice": "3d8+6",
        "speed": {"walk": 30},
        "abilities": {"str": 16, "dex": 12, "con": 14, "int": 8, "wis": 10, "cha": 8},
        "saving_throws": {}, "skills": {},
        "damage_resistances": [], "damage_immunities": [],
        "damage_vulnerabilities": [], "condition_immunities": [],
        "challenge_rating": "1", "trait_names": [], "action_names": ["Club"],
        "reaction_names": [], "legendary_action_names": [],
        "attacks": [{
            "id": "club", "name": "Club", "kind": "melee", "attack_bonus": 5,
            "reach_ft": 5,
            "damage": {"average": 6, "dice_count": 1, "dice_size": 6, "bonus": 3, "type": "bludgeoning"},
        }],
    }
    path = tmp_path / "monster.json"
    path.write_text(json.dumps([record]), encoding="utf-8")

    brute = monster_by_id_2014("test-brute", path)
    assert brute.armor_class == 14
    assert brute.weapon_attack.attack_bonus == 5
    assert brute.weapon_attack.weapon.damage_type == DamageType.BLUDGEONING
