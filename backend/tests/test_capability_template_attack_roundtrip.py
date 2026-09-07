from app.content.capability_compiler import compile_combatant
from app.content.capability_from_template import definition_from_template
from app.content.monsters_swarms import build_swarm_candidates


def test_attack_advantage_flags_survive_template_capability_round_trip() -> None:
    piranhas = next(item for item in build_swarm_candidates() if item.name == "Swarm of Piranhas")
    attack = piranhas.weapon_attack.model_copy(update={"advantage_if_target_grappled_by_self": True})
    source = piranhas.model_copy(update={"weapon_attack": attack})

    definition = definition_from_template(source)
    serialized = definition.attacks[0]
    assert serialized.advantage_if_target_missing_hp is True
    assert serialized.advantage_if_target_grappled_by_self is True

    rebuilt = compile_combatant(definition)
    assert rebuilt.weapon_attack.advantage_if_target_missing_hp is True
    assert rebuilt.weapon_attack.advantage_if_target_grappled_by_self is True
