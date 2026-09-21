from app.combat.conditions import attack_roll_condition_sources
from app.combat.state import build_combatant_state
from app.content.fighter_champion_2014_runtime import build_karnok_stoneward_2014


def test_invisible_is_a_universal_attack_advantage_and_defense_disadvantage_source() -> None:
    attacker = build_combatant_state(build_karnok_stoneward_2014(5))
    defender = build_combatant_state(build_karnok_stoneward_2014(5))

    attacker.active_effect_ids.append("invisible")
    advantage, disadvantage = attack_roll_condition_sources(attacker, defender, 5, defender.template.id)
    assert (advantage, disadvantage) == (1, 0)

    attacker.active_effect_ids.remove("invisible")
    defender.active_effect_ids.append("invisible")
    advantage, disadvantage = attack_roll_condition_sources(attacker, defender, 5, defender.template.id)
    assert (advantage, disadvantage) == (0, 1)

    attacker.active_effect_ids.append("invisible")
    advantage, disadvantage = attack_roll_condition_sources(attacker, defender, 5, defender.template.id)
    assert advantage == 1
    assert disadvantage == 1
