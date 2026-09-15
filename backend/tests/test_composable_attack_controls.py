from __future__ import annotations

import pytest

from app.content.capability_attack_compiler import UnsupportedCapabilityError, compile_attack
from app.domain.capabilities import AttackCapabilityDefinition


def _definition(*, grapple_size: str = "large", condition_size: str = "large") -> AttackCapabilityDefinition:
    return AttackCapabilityDefinition.model_validate({
        "id": "test-composite-control",
        "name": "Test Composite Control",
        "attack_kind": "melee",
        "attack_bonus": 7,
        "damage": {"count": 1, "size": 8, "bonus": 4},
        "damage_type": "slashing",
        "animation": "slash",
        "attack_ability": "strength",
        "attack_ability_modifier": 4,
        "effects": [
            {
                "kind": "grapple",
                "escape_dc": 15,
                "max_target_size": grapple_size,
                "restrains": True,
            },
            {
                "kind": "condition",
                "condition": "blinded",
                "max_target_size": condition_size,
                "repeat_save_ability": "constitution",
                "repeat_save_dc": 15,
                "repeat_save_timing": "target_turn_end",
            },
        ],
    })


def test_attack_compiler_composes_grapple_and_condition_into_shared_control() -> None:
    attack = compile_attack(_definition())

    control = attack.control_effect
    assert control is not None
    assert control.grapple_escape_dc == 15
    assert control.restrains_while_grappled is True
    assert control.condition_id == "blinded"
    assert control.repeat_save_ability == "constitution"
    assert control.repeat_save_dc == 15
    assert control.repeat_save_timing == "target_turn_end"
    assert control.max_target_size == "large"


def test_attack_compiler_rejects_conflicting_control_size_limits() -> None:
    with pytest.raises(UnsupportedCapabilityError, match="same target-size limit"):
        compile_attack(_definition(condition_size="medium"))
