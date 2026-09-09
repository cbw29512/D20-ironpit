from app.content.capability_registry import load_capability_definitions
from app.content.combatant_action_ir_compiler import compile_combatant_action_ir


def test_all_declarative_combatants_compile_to_action_ir() -> None:
    definitions = load_capability_definitions()
    for definition in definitions.values():
        action_ir = compile_combatant_action_ir(definition)
        assert action_ir.combatant_id == definition.id
        assert action_ir.primary_attack_id == definition.primary_attack_id
        expected_count = len(definition.attacks) + len(definition.save_actions)
        assert len(action_ir.actions) == expected_count
        assert (action_ir.attack_sequence is None) == (definition.attack_action is None)
