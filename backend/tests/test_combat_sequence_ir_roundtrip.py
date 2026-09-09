from app.content.capability_registry import load_capability_definitions
from app.content.combat_sequence_ir_adapters import multiattack_capability_to_ir, multiattack_ir_to_capability


def test_all_registry_multiattacks_round_trip_through_sequence_ir() -> None:
    for definition in load_capability_definitions().values():
        if definition.attack_action is None:
            continue
        original = definition.attack_action
        rebuilt = multiattack_ir_to_capability(multiattack_capability_to_ir(original))
        assert rebuilt.model_dump() == original.model_dump(), f"sequence IR drift: {definition.name} / {original.name}"
