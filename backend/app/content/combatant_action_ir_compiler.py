from __future__ import annotations

from app.content.combat_ir_adapters import attack_capability_to_ir, save_capability_to_ir
from app.content.combat_ir_reaction_adapters import (
    parry_reaction_to_ir,
    redirect_attack_reaction_to_ir,
)
from app.content.combat_ir_support_adapters import condition_removal_action_to_ir, healing_action_to_ir
from app.content.combat_sequence_ir_adapters import multiattack_capability_to_ir
from app.domain.capabilities import CombatantDefinition
from app.domain.combatant_action_ir import CombatantActionIR


def compile_combatant_action_ir(definition: CombatantDefinition) -> CombatantActionIR:
    actions = [attack_capability_to_ir(attack) for attack in definition.attacks]
    actions.extend(save_capability_to_ir(action) for action in definition.save_actions)
    actions.extend(healing_action_to_ir(action) for action in definition.healing_actions)
    actions.extend(condition_removal_action_to_ir(action) for action in definition.condition_removal_actions)
    if definition.parry_reaction is not None:
        actions.append(parry_reaction_to_ir(definition.parry_reaction))
    if definition.redirect_attack_reaction is not None:
        actions.append(redirect_attack_reaction_to_ir(definition.redirect_attack_reaction))
    sequence = None
    if definition.attack_action is not None:
        sequence = multiattack_capability_to_ir(definition.attack_action)
    return CombatantActionIR(
        combatant_id=definition.id,
        primary_attack_id=definition.primary_attack_id,
        actions=actions,
        attack_sequence=sequence,
    )
