import pytest

from app.content.capability_compiler import UnsupportedCapabilityError, compile_combatant
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
