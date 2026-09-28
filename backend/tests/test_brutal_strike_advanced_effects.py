from __future__ import annotations

from app.combat.brutal_strike import apply_staggering_blow, apply_sundering_blow
from app.combat.defensive_modifier_rules import saving_throw_disadvantage_sources
from app.combat.incoming_attack_bonus import next_incoming_attack_roll_flat_bonus
from app.combat.hit_modifiers import expire_source_turn_start_modifiers
from app.combat.opportunity_attack_rules import opportunity_attacks_suppressed
from app.combat.state import build_combatant_state
from app.content.audited_fighter import build_karnok_stoneward
from app.domain.encounters import EncounterCombatant


def _state():
    return build_combatant_state(build_karnok_stoneward().model_copy(deep=True))


def test_staggering_blow_reuses_save_disadvantage_and_oa_suppression() -> None:
    target = _state()
    assert apply_staggering_blow(target, "source") is True
    assert saving_throw_disadvantage_sources(target) == 1
    reactor = EncounterCombatant(combatant_id="target", side="monsters", position_ft=0, state=target)
    assert opportunity_attacks_suppressed(reactor) is True
    assert expire_source_turn_start_modifiers([target], "source") == 2
    assert saving_throw_disadvantage_sources(target) == 0
    assert opportunity_attacks_suppressed(reactor) is False


def test_sundering_blow_reuses_generic_next_incoming_attack_bonus() -> None:
    target = _state()
    assert apply_sundering_blow(target, "source") is True
    assert next_incoming_attack_roll_flat_bonus(target, "source") == 0
    assert next_incoming_attack_roll_flat_bonus(target, "ally") == 5
    assert expire_source_turn_start_modifiers([target], "source") == 1
    assert next_incoming_attack_roll_flat_bonus(target, "ally") == 0
