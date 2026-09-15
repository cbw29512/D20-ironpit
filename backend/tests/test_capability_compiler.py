import pytest

from app.content.capability_compiler import UnsupportedCapabilityError, compile_combatant
from app.content.capability_from_template import definition_from_template
from app.domain.capabilities import CombatantDefinition
from app.domain.size import CreatureSize
from app.domain.traits import CombatTrait


def _definition(**updates) -> CombatantDefinition:
    data = {
        "id": "contract-combatant",
        "name": "Contract Combatant",
        "archetype": "contract",
        "kind": "monster",
        "armor_class": 12,
        "max_hp": 20,
        "speed_ft": 30,
        "initiative_bonus": 1,
        "attacks": [{
            "id": "contract-bite",
            "name": "Bite",
            "attack_kind": "melee",
            "attack_bonus": 4,
            "damage": {"count": 1, "size": 6, "bonus": 2},
            "damage_type": "piercing",
            "animation": "bite",
            "effects": [
                {"kind": "damage", "source": "venom", "dice": {"count": 1, "size": 4}, "damage_type": "poison"},
                {"kind": "prone", "max_target_size": "medium"}
            ]
        }],
        "primary_attack_id": "contract-bite",
        "combat_traits": ["pack-tactics"],
        "visual": {"armor": "natural", "main_hand": "bite", "body_style": "beast"},
        "source": "contract-test"
    }
    data.update(updates)
    return CombatantDefinition.model_validate(data)


def test_compiler_maps_composable_attack_effects() -> None:
    template = compile_combatant(_definition())
    assert template.weapon_attack.attack_bonus == 4
    assert template.weapon_attack.damage_bonus == 2
    assert template.weapon_attack.knocks_prone_max_size == CreatureSize.MEDIUM
    assert template.weapon_attack.on_hit_damage[0].damage_type.value == "poison"
    assert template.combat_traits == [CombatTrait.PACK_TACTICS]
    assert template.movement_modes.walk_ft == 30


def test_compiler_preserves_weapon_property_mastery_and_ability_facts() -> None:
    definition = _definition(
        attacks=[{
            "id": "contract-scimitar",
            "name": "Scimitar",
            "weapon_id": "scimitar",
            "attack_kind": "melee",
            "attack_bonus": 5,
            "damage": {"count": 1, "size": 6, "bonus": 3},
            "damage_type": "slashing",
            "animation": "slash",
            "mastery_property": "Nick",
            "light": True,
            "attack_ability": "dexterity",
            "attack_ability_modifier": 3,
        }],
        primary_attack_id="contract-scimitar",
        weapon_masteries=["scimitar"],
        attack_action={
            "id": "attack",
            "name": "Attack",
            "is_attack_action": True,
            "slots": [{"attack_ids": ["contract-scimitar"]}],
        },
    )
    template = compile_combatant(definition)
    attack = template.weapon_attack
    assert attack.weapon.id == "scimitar"
    assert attack.weapon.light is True
    assert attack.weapon.mastery_property == "Nick"
    assert attack.attack_ability == "dexterity"
    assert attack.attack_ability_modifier == 3
    assert template.weapon_masteries == ["scimitar"]
    assert template.attack_action is not None
    assert template.attack_action.is_attack_action is True


def test_capability_round_trip_preserves_resources_and_area_geometry() -> None:
    definition = _definition(
        attacks=[{
            "id": "recharge-rock", "name": "Rock", "attack_kind": "ranged", "attack_bonus": 5,
            "damage": {"count": 2, "size": 6, "bonus": 3}, "damage_type": "bludgeoning",
            "animation": "throw", "normal_range_ft": 25, "long_range_ft": 50,
            "resource_id": "rock-recharge", "resource_cost": 1,
        }],
        primary_attack_id="recharge-rock",
        save_actions=[{
            "id": "breath", "name": "Breath", "save_ability": "dexterity", "dc": 13,
            "range_ft": 0, "area": {"shape": "cone", "origin": "self", "length_ft": 15},
            "damage": {"count": 3, "size": 6}, "damage_type": "fire", "success_damage": "half",
            "resource_id": "breath-recharge", "resource_cost": 1,
        }],
        resources=[
            {"id": "rock-recharge", "name": "Rock", "max_uses": 1,
             "recharge": {"trigger": "start_of_turn", "die_size": 6, "minimum_roll": 6}},
            {"id": "breath-recharge", "name": "Breath", "max_uses": 1,
             "recharge": {"trigger": "start_of_turn", "die_size": 6, "minimum_roll": 5}},
        ],
    )
    runtime = compile_combatant(definition)
    rebuilt_definition = definition_from_template(runtime)
    rebuilt = compile_combatant(rebuilt_definition)

    assert rebuilt.weapon_attack.resource_id == "rock-recharge"
    assert rebuilt.weapon_attack.resource_cost == 1
    save = rebuilt.saving_throw_actions[0]
    assert save.resource_id == "breath-recharge"
    assert save.resource_cost == 1
    assert save.area is not None
    assert save.area.shape == "cone"
    assert save.area.origin == "self"
    assert save.area.length_ft == 15
    thresholds = {resource.id: resource.recharge.minimum_roll for resource in rebuilt.resources}
    assert thresholds == {"rock-recharge": 6, "breath-recharge": 5}


def test_attack_ability_modifier_requires_declared_ability() -> None:
    with pytest.raises(ValueError, match="requires an explicit attack ability"):
        _definition(attacks=[{
            "id": "bad-attack", "name": "Bad", "attack_kind": "melee", "attack_bonus": 4,
            "damage": {"count": 1, "size": 6, "bonus": 2}, "damage_type": "slashing",
            "animation": "slash", "attack_ability_modifier": 2,
        }], primary_attack_id="bad-attack")


def test_compiler_fails_closed_for_declared_unsupported_capability() -> None:
    definition = _definition(unsupported_capabilities=["recharge:5-6"])
    with pytest.raises(UnsupportedCapabilityError, match="recharge:5-6"):
        compile_combatant(definition)
