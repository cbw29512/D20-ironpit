from app.combat.bloodied import target_missing_hp_attack_advantage
from app.content.capability_compiler import compile_combatant
from app.content.monster_catalog import load_monster_rows
from app.content.simple_monster_source_attacks import parse_simple_attacks
from app.content.simple_monster_source_definitions import build_simple_source_definitions
from app.domain.runtime import CombatantState


def _piranha_definition():
    return next(
        item for item in build_simple_source_definitions().values()
        if item.name == "Piranha"
    )


def test_piranha_source_parses_fixed_damage_and_injured_target_advantage() -> None:
    row = next(row for row in load_monster_rows() if row["name"] == "Piranha")
    attacks, multiattack = parse_simple_attacks(row)

    assert multiattack is None
    assert len(attacks) == 1
    attack = attacks[0]
    assert attack["fixed_damage"] == 1
    assert attack["damage_type"] == "piercing"
    assert attack["advantage_if_target_missing_hp"] is True


def test_piranha_source_definition_keeps_injured_target_advantage() -> None:
    attack = _piranha_definition().attacks[0]

    assert attack.fixed_damage == 1
    assert attack.damage_type.value == "piercing"
    assert attack.advantage_if_target_missing_hp is True


def test_injured_target_advantage_starts_after_any_hp_is_missing() -> None:
    template = compile_combatant(_piranha_definition())
    attack = template.weapon_attack
    target = CombatantState(template=template, current_hp=template.max_hp)

    assert target_missing_hp_attack_advantage(attack, target) == 0
    target.current_hp -= 1
    assert target_missing_hp_attack_advantage(attack, target) == 1
