from __future__ import annotations

from app.combat.ability_checks import ability_check_roll_mode
from app.combat.conditions import attack_roll_condition_sources
from app.combat.defensive_modifier_rules import saving_throw_advantage_sources
from app.combat.modifier_stack import add_modifier
from app.combat.state import build_combatant_state
from app.content.audited_fighter import build_karnok_stoneward
from app.domain.modifiers import CombatModifier
from app.domain.models import RollMode


def _state():
    return build_combatant_state(build_karnok_stoneward())


def _foresight_like_modifier() -> CombatModifier:
    return CombatModifier(
        id="source:foresight:self:0",
        source_id="source",
        source_effect_id="foresight",
        source_name="Foresight",
        source_is_magical=True,
        kind="d20-test-advantage",
    )


def test_d20_test_advantage_applies_to_attacks_saves_and_checks() -> None:
    attacker = _state()
    defender = _state()
    add_modifier(attacker, _foresight_like_modifier())

    attack_advantage, _ = attack_roll_condition_sources(
        attacker, defender, 5, "defender",
    )
    assert attack_advantage == 1
    assert saving_throw_advantage_sources(attacker, "wisdom") == 1
    assert ability_check_roll_mode(attacker) is RollMode.ADVANTAGE


def test_d20_test_advantage_cancels_ability_check_disadvantage() -> None:
    state = _state()
    add_modifier(state, _foresight_like_modifier())
    assert ability_check_roll_mode(state, disadvantage_sources=1) is RollMode.NORMAL
