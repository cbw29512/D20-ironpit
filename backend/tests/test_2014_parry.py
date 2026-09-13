from app.content.monster_catalog_2014 import compile_monster_2014, unsupported_mechanics_2014
from app.content.monster_catalog_2014_models import CatalogMonster2014


def test_parry_binds_to_existing_reaction_primitive() -> None:
    source = CatalogMonster2014.model_validate({
        "id": "duelist", "name": "Duelist", "ruleset": "2014",
        "size": "Medium", "creature_type": "humanoid", "armor_class": 15, "max_hp": 40,
        "speed": {"walk": 30},
        "abilities": {"str": 14, "dex": 16, "con": 14, "int": 10, "wis": 10, "cha": 10},
        "attacks": [{
            "id": "sword", "name": "Sword", "kind": "melee", "attack_bonus": 5,
            "damage": {"average": 6, "dice_count": 1, "dice_size": 6, "bonus": 3, "type": "slashing"},
        }],
        "action_names": ["Sword"], "reaction_names": ["Parry"], "parry_ac_bonus": 3,
    })

    assert unsupported_mechanics_2014(source) == []
    template = compile_monster_2014(source)
    assert template.parry_reaction is not None
    assert template.parry_reaction.ac_bonus == 3
