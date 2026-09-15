from app.content.monster_catalog_2014 import compile_monster_2014
from app.content.monster_catalog_2014_models import CatalogMonster2014
from app.domain.models import DamageType


def _monster(*, source_complete: bool = True) -> CatalogMonster2014:
    return CatalogMonster2014.model_validate({
        "id": "ember-brute", "name": "Ember Brute", "ruleset": "2014",
        "size": "Medium", "creature_type": "elemental", "armor_class": 13, "max_hp": 25,
        "speed": {"walk": 30},
        "abilities": {"str": 16, "dex": 10, "con": 14, "int": 6, "wis": 10, "cha": 6},
        "attacks": [{
            "id": "slam", "name": "Slam", "kind": "melee", "attack_bonus": 5,
            "damage": {"average": 6, "dice_count": 1, "dice_size": 6, "bonus": 3, "type": "bludgeoning"},
            "on_hit_damage": [{"average": 7, "dice_count": 2, "dice_size": 6, "bonus": 0, "type": "fire"}],
            "source_complete": source_complete,
        }],
        "action_names": ["Slam"],
    })


def test_secondary_damage_compiles_as_shared_on_hit_damage() -> None:
    template = compile_monster_2014(_monster())
    rider = template.weapon_attack.on_hit_damage[0]
    assert (rider.dice_count, rider.dice_size, rider.damage_type) == (2, 6, DamageType.FIRE)
