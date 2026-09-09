from app.content.capability_registry import load_capability_definitions
from app.content.combat_ir_adapters import attack_capability_to_ir, save_capability_to_ir
from app.content.combat_ir_reverse_adapters import attack_ir_to_capability, save_ir_to_capability
from app.content.combat_ir_support_adapters import condition_removal_action_to_ir, healing_action_to_ir
from app.content.combat_ir_support_reverse_adapters import condition_removal_ir_to_action, healing_ir_to_action


def test_all_registry_attacks_round_trip_through_combat_ir() -> None:
    for definition in load_capability_definitions().values():
        for attack in definition.attacks:
            rebuilt = attack_ir_to_capability(attack_capability_to_ir(attack))
            assert rebuilt.model_dump() == attack.model_dump(), f"attack IR drift: {definition.name} / {attack.name}"


def test_all_registry_save_actions_are_semantically_stable_through_combat_ir() -> None:
    for definition in load_capability_definitions().values():
        for action in definition.save_actions:
            original_ir = save_capability_to_ir(action)
            rebuilt_ir = save_capability_to_ir(save_ir_to_capability(original_ir))
            assert rebuilt_ir.model_dump() == original_ir.model_dump(), f"save IR drift: {definition.name} / {action.name}"


def test_all_registry_healing_actions_round_trip_through_combat_ir() -> None:
    for definition in load_capability_definitions().values():
        for action in definition.healing_actions:
            rebuilt = healing_ir_to_action(healing_action_to_ir(action))
            assert rebuilt.model_dump() == action.model_dump(), f"healing IR drift: {definition.name} / {action.name}"


def test_all_registry_condition_removal_actions_round_trip_through_combat_ir() -> None:
    for definition in load_capability_definitions().values():
        for action in definition.condition_removal_actions:
            rebuilt = condition_removal_ir_to_action(condition_removal_action_to_ir(action))
            assert rebuilt.model_dump() == action.model_dump(), f"condition-removal IR drift: {definition.name} / {action.name}"
