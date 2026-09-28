from __future__ import annotations

from app.combat.modifier_stack import (
    add_modifier,
    consume_next_attack_against_flat,
    next_attack_against_flat_bonus,
)
from app.content.audited_fighter import build_demo_fighter
from app.domain.modifiers import CombatModifier, ModifierKind
from app.domain.runtime import CombatantState


def _state() -> CombatantState:
    template = build_demo_fighter()
    return CombatantState.from_template(template)


def test_next_attack_against_flat_bonus_excludes_source_and_consumes_for_other_attacker() -> None:
    target = _state()
    add_modifier(target, CombatModifier(
        id="barbarian:sundering:target",
        source_id="barbarian",
        source_effect_id="sundering-blow",
        source_name="Sundering Blow",
        kind=ModifierKind.NEXT_ATTACK_AGAINST_FLAT,
        flat_bonus=5,
        consume_on_attack_against=True,
        expires_at_start_of_source_turn=True,
    ))

    assert next_attack_against_flat_bonus(target, "barbarian") == 0
    assert consume_next_attack_against_flat(target, "barbarian") == 0
    assert len(target.active_modifiers) == 1

    assert next_attack_against_flat_bonus(target, "ally") == 5
    assert consume_next_attack_against_flat(target, "ally") == 1
    assert next_attack_against_flat_bonus(target, "another-ally") == 0
