from __future__ import annotations

from app.combat.delayed_resource_refill import resolve_delayed_resource_refill_end_turn
from app.combat.state import build_combatant_state
from app.content.warlock_2014_progression import warlock_2014_level
from app.content.warlock_fiend_2014_profile import build_varek_ashenmark_2014_profile
from app.content.warlock_fiend_2014_runtime import build_varek_ashenmark_2014
from app.domain.encounters import EncounterCombatant


def _member(level: int) -> EncounterCombatant:
    return EncounterCombatant(
        combatant_id=f"varek-{level}",
        side="heroes",
        position_ft=0,
        state=build_combatant_state(build_varek_ashenmark_2014(level)),
    )


def test_varek_level_eighteen_adds_eighth_invocation_skill_proficiencies() -> None:
    varek = build_varek_ashenmark_2014(18)
    profile = build_varek_ashenmark_2014_profile(18)

    assert warlock_2014_level(18).invocations_known == 8
    assert profile.skill_proficiencies == ["Arcana", "History", "Deception", "Persuasion"]
    assert varek.skill_bonuses["deception"] == 11
    assert varek.skill_bonuses["persuasion"] == 11

    audits = {item.feature_id: item for item in profile.feature_audits}
    assert audits["beguiling-influence"].automated is True
    assert audits["beguiling-influence"].combat_relevant is False


def test_varek_level_nineteen_caps_constitution_and_keeps_four_pact_slots() -> None:
    l18 = build_varek_ashenmark_2014(18)
    l19 = build_varek_ashenmark_2014(19)
    profile = build_varek_ashenmark_2014_profile(19)

    assert profile.final_ability_scores.constitution == 20
    assert profile.final_ability_scores.charisma == 20
    assert l19.max_hp > l18.max_hp
    assert warlock_2014_level(19).pact_slots == 4
    assert {item.id: item.max_uses for item in l19.resources}["spell-slot-5"] == 4

    audits = {item.feature_id: item for item in profile.feature_audits}
    assert audits["ability-score-improvement-l19"].automated is True


def test_varek_level_twenty_eldritch_master_arms_then_restores_pact_slots_after_ten_rounds() -> None:
    varek = _member(20)
    pact = next(item for item in varek.state.resources if item.id == "spell-slot-5")
    master = next(item for item in varek.state.resources if item.id == "eldritch-master")

    pact.current_uses = 1
    events, sequence = resolve_delayed_resource_refill_end_turn(1, 1, varek)
    assert len(events) == 1
    assert events[0].feature_id == "eldritch-master"
    assert events[0].resource_remaining == 0
    assert pact.current_uses == 1
    assert master.current_uses == 0
    assert varek.state.delayed_resource_refills[0].completes_round == 11

    for round_number in range(2, 11):
        events, sequence = resolve_delayed_resource_refill_end_turn(sequence, round_number, varek)
        assert events == []
        assert pact.current_uses == 1

    events, sequence = resolve_delayed_resource_refill_end_turn(sequence, 11, varek)
    assert len(events) == 1
    assert events[0].feature_id == "eldritch-master"
    assert pact.current_uses == 4
    assert varek.state.delayed_resource_refills == []

    pact.current_uses = 0
    events, _ = resolve_delayed_resource_refill_end_turn(sequence, 12, varek)
    assert events == []
    assert varek.state.delayed_resource_refills == []


def test_varek_level_twenty_does_not_waste_eldritch_master_when_pact_slots_are_full() -> None:
    varek = _member(20)
    events, _ = resolve_delayed_resource_refill_end_turn(1, 1, varek)

    assert events == []
    assert varek.state.delayed_resource_refills == []
    assert next(item.current_uses for item in varek.state.resources if item.id == "eldritch-master") == 1


def test_varek_level_twenty_progression_is_explicitly_certified() -> None:
    varek = build_varek_ashenmark_2014(20)
    profile = build_varek_ashenmark_2014_profile(20)
    rule = varek.progression_features.delayed_resource_refill

    assert rule is not None
    assert rule.source_id == "eldritch-master"
    assert rule.resource_ids == ["spell-slot-5"]
    assert rule.delay_rounds == 10
    assert {item.id: item.max_uses for item in varek.resources}["eldritch-master"] == 1

    audits = {item.feature_id: item for item in profile.feature_audits}
    assert audits["eldritch-master"].automated is True
    assert audits["eldritch-master"].combat_relevant is True
