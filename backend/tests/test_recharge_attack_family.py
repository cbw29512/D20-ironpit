from app.combat.action_resources import consume_resource, recharge_start_of_turn, resource_available
from app.content.capability_compiler import compile_combatant
from app.content.monster_catalog import load_monster_rows
from app.content.monster_recharge_attack_batch import (
    build_recharge_attack_monster_definitions,
    discover_recharge_attack_names,
)
from app.content.monster_source_audit import audit_monster_source
from app.content.monster_source_definition import source_row
from app.domain.runtime import CombatantState


class FixedDice:
    def __init__(self, value: int): self.value = value
    def roll(self, sides: int) -> int:
        assert sides == 6
        return self.value


def test_recharge_attack_family_is_discovered_from_srd_not_a_manual_name_list() -> None:
    names = discover_recharge_attack_names()
    source_order = [str(row["name"]) for row in load_monster_rows()]
    assert "Ape" in names
    assert list(names) == [name for name in source_order if name in set(names)]


def test_ape_is_source_derived_recharge_attack_monster() -> None:
    definition = build_recharge_attack_monster_definitions()["srd-ape"]
    template = compile_combatant(definition)
    attacks = [template.weapon_attack, *template.alternate_weapon_attacks]
    assert [attack.weapon.name for attack in attacks] == ["Fist", "Rock"]
    rock = next(attack for attack in attacks if attack.weapon.name == "Rock")
    assert rock.resource_id == "srd-ape-rock-recharge"
    assert rock.weapon.normal_range_ft == 25 and rock.weapon.long_range_ft == 50
    assert template.attack_action is not None and len(template.attack_action.slots) == 2
    assert audit_monster_source(template, source_row("Ape")) == []


def test_recharge_attack_resource_is_shared_and_generic() -> None:
    template = compile_combatant(build_recharge_attack_monster_definitions()["srd-ape"])
    rock = next(attack for attack in [template.weapon_attack, *template.alternate_weapon_attacks] if attack.weapon.name == "Rock")
    state = CombatantState.from_template(template)
    assert resource_available(state, rock)
    assert consume_resource(state, rock) == 0
    assert not resource_available(state, rock)
    recharge_start_of_turn(state, FixedDice(5))
    assert not resource_available(state, rock)
    recharge_start_of_turn(state, FixedDice(6))
    assert resource_available(state, rock)
