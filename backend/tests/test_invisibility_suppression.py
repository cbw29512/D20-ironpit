from __future__ import annotations

from app.combat.condition_rules import can_see
from app.combat.conditions import attack_roll_condition_sources
from app.combat.state import build_combatant_state
from app.content.audited_druid import build_thalen_greenbough_level
from app.domain.modifiers import CombatModifier, ModifierKind


def _states():
    attacker = build_combatant_state(build_thalen_greenbough_level(2))
    defender = build_combatant_state(build_thalen_greenbough_level(2))
    defender.active_effect_ids.append("invisible")
    return attacker, defender


def test_invisibility_suppression_restores_visibility_and_removes_unseen_disadvantage() -> None:
    attacker, defender = _states()

    assert can_see(attacker, defender) is False
    _, disadvantage = attack_roll_condition_sources(attacker, defender, 30)
    assert disadvantage == 1

    defender.active_modifiers.append(CombatModifier(
        id="caster:faerie-fire:defender:1",
        source_id="caster",
        source_effect_id="faerie-fire",
        source_name="Faerie Fire",
        source_is_magical=True,
        kind=ModifierKind.INVISIBILITY_BENEFITS_SUPPRESSED,
        concentration_required=True,
    ))

    assert can_see(attacker, defender) is True
    _, disadvantage = attack_roll_condition_sources(attacker, defender, 30)
    assert disadvantage == 0


def test_invisibility_suppression_removes_invisible_attacker_advantage() -> None:
    attacker, defender = _states()
    attacker.active_effect_ids.append("invisible")
    advantage, _ = attack_roll_condition_sources(attacker, defender, 30)
    assert advantage == 1

    attacker.active_modifiers.append(CombatModifier(
        id="caster:faerie-fire:attacker:1",
        source_id="caster",
        source_effect_id="faerie-fire",
        source_name="Faerie Fire",
        source_is_magical=True,
        kind=ModifierKind.INVISIBILITY_BENEFITS_SUPPRESSED,
        concentration_required=True,
    ))

    advantage, _ = attack_roll_condition_sources(attacker, defender, 30)
    assert advantage == 0
