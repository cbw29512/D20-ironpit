import json

import pytest

from app.combat.attacks import resolve_attack
from app.combat.damage_defenses import adjusted_damage_amount
from app.combat.dice import FixedDiceProvider
from app.combat.state import build_combatant_state
from app.content.monster_catalog_2014 import (
    MVP_CATALOG_PATH,
    compile_monster_2014,
    load_catalog_2014,
    monster_by_id_2014,
    unsupported_mechanics_2014,
)
from app.domain.models import DamageType


def _monster(monster_id: str):
    return monster_by_id_2014(monster_id, MVP_CATALOG_PATH)


def test_mvp_catalog_loads_and_uses_json_stats() -> None:
    catalog = load_catalog_2014(MVP_CATALOG_PATH)
    assert {monster.id for monster in catalog} == {"goblin", "skeleton", "brown-bear", "bandit"}
    bandit = _monster("bandit")
    assert bandit.armor_class == 12
    assert bandit.max_hp == 11
    assert bandit.speed_ft == 30
    assert bandit.ability_scores.dexterity == 12
    assert bandit.weapon_attack.weapon.name == "Scimitar"
    assert bandit.alternate_weapon_attacks[0].weapon.name == "Light Crossbow"
    assert bandit.alternate_weapon_attacks[0].weapon.normal_range_ft == 80
    assert bandit.alternate_weapon_attacks[0].weapon.long_range_ft == 320


def test_json_ranged_attack_runs_through_universal_resolver() -> None:
    attacker = build_combatant_state(_monster("bandit"))
    defender = build_combatant_state(_monster("skeleton"))
    crossbow = attacker.template.alternate_weapon_attacks[0]
    event = resolve_attack(1, 1, attacker, defender, crossbow, 80, FixedDiceProvider([10, 4]))
    assert event.hit is True
    assert defender.current_hp == 8


def test_json_defenses_feed_shared_damage_engine() -> None:
    skeleton = build_combatant_state(_monster("skeleton"))
    assert adjusted_damage_amount(5, DamageType.BLUDGEONING, skeleton) == 10
    assert adjusted_damage_amount(5, DamageType.POISON, skeleton) == 0
    assert adjusted_damage_amount(5, DamageType.PIERCING, skeleton) == 5


def test_runtime_state_is_fresh_for_each_fight() -> None:
    template = _monster("bandit")
    first = build_combatant_state(template)
    second = build_combatant_state(template)
    first.current_hp = 1
    assert second.current_hp == 11
    assert template.max_hp == 11


def test_unresolved_monster_mechanics_fail_closed() -> None:
    catalog = {monster.id: monster for monster in load_catalog_2014(MVP_CATALOG_PATH)}
    assert "trait:Nimble Escape" in unsupported_mechanics_2014(catalog["goblin"])
    assert "action:Multiattack" in unsupported_mechanics_2014(catalog["brown-bear"])
    with pytest.raises(RuntimeError, match="could not be compiled"):
        _monster("goblin")


def test_declarative_multiattack_reuses_shared_action_slots() -> None:
    catalog = {monster.id: monster for monster in load_catalog_2014(MVP_CATALOG_PATH)}
    source = catalog["brown-bear"].model_copy(
        update={"trait_names": [], "multiattack_slots": [["bite"], ["claws"]]}
    )
    assert "action:Multiattack" not in unsupported_mechanics_2014(source)
    bear = compile_monster_2014(source)
    assert bear.attack_action is not None
    assert [slot.attack_ids for slot in bear.attack_action.slots] == [["bite"], ["claws"]]


def test_new_basic_monster_is_data_only(tmp_path) -> None:
    record = {
        "id": "test-brute", "name": "Test Brute", "ruleset": "2014",
        "size": "Medium", "creature_type": "humanoid", "alignment": "unaligned",
        "armor_class": 14, "max_hp": 20, "hit_dice": "3d8+6", "speed": {"walk": 30},
        "abilities": {"str": 16, "dex": 12, "con": 14, "int": 8, "wis": 10, "cha": 8},
        "saving_throws": {}, "skills": {}, "damage_resistances": [], "damage_immunities": [],
        "damage_vulnerabilities": [], "condition_immunities": [], "challenge_rating": "1",
        "trait_names": [], "action_names": ["Club"], "reaction_names": [], "legendary_action_names": [],
        "attacks": [{"id": "club", "name": "Club", "kind": "melee", "attack_bonus": 5,
                     "reach_ft": 5, "damage": {"average": 6, "dice_count": 1, "dice_size": 6,
                                                   "bonus": 3, "type": "bludgeoning"}}],
    }
    path = tmp_path / "monster.json"
    path.write_text(json.dumps([record]), encoding="utf-8")
    brute = monster_by_id_2014("test-brute", path)
    assert brute.armor_class == 14
    assert brute.weapon_attack.attack_bonus == 5
    assert brute.weapon_attack.weapon.damage_type == DamageType.BLUDGEONING
