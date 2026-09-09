from app.content.capability_registry import load_capability_definitions
from app.content.combatant_action_ir_compiler import compile_combatant_action_ir


def test_all_declarative_combatants_compile_to_action_ir() -> None:
    definitions = load_capability_definitions()
    for definition in definitions.values():
        action_ir = compile_combatant_action_ir(definition)
        assert action_ir.combatant_id == definition.id
        assert action_ir.primary_attack_id == definition.primary_attack_id
        expected_reaction_ids = set()
        if definition.parry_reaction is not None:
            expected_reaction_ids.add("parry")
        if definition.redirect_attack_reaction is not None:
            expected_reaction_ids.add("redirect-attack")
        expected_count = (
            len(definition.attacks)
            + len(definition.save_actions)
            + len(definition.healing_actions)
            + len(definition.condition_removal_actions)
            + len(expected_reaction_ids)
        )
        assert len(action_ir.actions) == expected_count
        expected_ids = {
            *(action.id for action in definition.attacks),
            *(action.id for action in definition.save_actions),
            *(action.id for action in definition.healing_actions),
            *(action.id for action in definition.condition_removal_actions),
            *expected_reaction_ids,
        }
        assert {action.id for action in action_ir.actions} == expected_ids
        assert (action_ir.attack_sequence is None) == (definition.attack_action is None)
