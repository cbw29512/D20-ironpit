from __future__ import annotations

from app.combat.condition_rules import can_see
from app.combat.conditions import attack_roll_condition_sources
from app.combat.dice import FixedDiceProvider
from app.combat.encounter_setup import build_encounter_setup
from app.combat.hp_threshold_instant_death import legal_hp_threshold_instant_death
from app.combat.opportunity_attacks import resolve_opportunity_attack
from app.combat.state import build_combatant_state
from app.combat.visibility_rules import effective_sense_range_ft
from app.content.audited_druid import build_thalen_greenbough_level
from app.content.warlock_fiend_2014_runtime import build_varek_ashenmark_2014
from app.domain.encounters import EncounterCombatant
from app.domain.grid import GridPosition
from app.domain.models import EncounterSelection


def _states(*, blindsight_ft: int = 0, truesight_ft: int = 0):
    observer = build_combatant_state(
        build_thalen_greenbough_level(2).model_copy(
            update={"blindsight_ft": blindsight_ft, "truesight_ft": truesight_ft},
        )
    )
    target = build_combatant_state(build_thalen_greenbough_level(2))
    return observer, target


def test_truesight_sees_invisible_only_inside_declared_range() -> None:
    observer, target = _states(truesight_ft=60)
    target.active_effect_ids.append("invisible")

    assert can_see(observer, target, 60) is True
    assert can_see(observer, target, 65) is False
    assert can_see(observer, target) is False


def test_blindsight_perceives_invisible_inside_range() -> None:
    observer, target = _states(blindsight_ft=30)
    target.active_effect_ids.append("invisible")

    assert can_see(observer, target, 30) is True
    assert can_see(observer, target, 35) is False


def test_blinded_blocks_truesight_but_not_in_range_blindsight() -> None:
    sighted, target = _states(truesight_ft=60)
    blind_sight, _ = _states(blindsight_ft=10)
    sighted.active_effect_ids.append("blinded")
    blind_sight.active_effect_ids.append("blinded")
    target.active_effect_ids.append("invisible")

    assert can_see(sighted, target, 5) is False
    assert can_see(blind_sight, target, 10) is True
    assert can_see(blind_sight, target, 15) is False


def test_effective_sense_hook_defaults_to_source_range() -> None:
    observer, _ = _states(blindsight_ft=15, truesight_ft=60)
    assert effective_sense_range_ft(observer, "blindsight") == 15
    assert effective_sense_range_ft(observer, "truesight") == 60


def test_hearing_flag_suppresses_effective_blindsight_while_deafened() -> None:
    observer, target = _states(blindsight_ft=30)
    object.__setattr__(observer.template, "blindsight_requires_hearing", True)
    object.__setattr__(observer, "blindsight_requires_hearing", True)
    target.active_effect_ids.append("invisible")

    assert effective_sense_range_ft(observer, "blindsight") == 30
    assert can_see(observer, target, 30) is True
    observer.active_effect_ids.append("deafened")
    assert effective_sense_range_ft(observer, "blindsight") == 0
    assert can_see(observer, target, 30) is False
    observer.active_effect_ids.remove("deafened")
    assert observer.template.blindsight_ft == 30
    assert effective_sense_range_ft(observer, "blindsight") == 30


def test_truesight_removes_unseen_attack_penalty_inside_range() -> None:
    observer, target = _states(truesight_ft=60)
    ordinary, _ = _states()
    _, baseline = attack_roll_condition_sources(ordinary, target, 30)
    target.active_effect_ids.append("invisible")

    _, hidden = attack_roll_condition_sources(ordinary, target, 30)
    _, seen = attack_roll_condition_sources(observer, target, 30)
    _, out_of_range = attack_roll_condition_sources(observer, target, 65)
    assert hidden == baseline + 1
    assert seen == baseline
    assert out_of_range == baseline + 1


def test_truesight_lets_opportunity_attack_see_invisible_mover_inside_range() -> None:
    setup = build_encounter_setup(EncounterSelection(
        hero_ids=["karnok-stoneward-l1"], monster_ids=["srd-commoner"],
    ))
    reactor, mover = setup.monsters[0], setup.heroes[0]
    reactor.state.template = reactor.state.template.model_copy(update={"truesight_ft": 60})
    mover.state.active_effect_ids.append("invisible")

    event = resolve_opportunity_attack(
        1, 1, reactor, mover, setup, 5, 10, "speed", FixedDiceProvider([19, 1]),
    )
    assert event is not None
    assert event.feature_id == "opportunity-attack"


def test_truesight_does_not_let_opportunity_attack_see_invisible_mover_outside_range() -> None:
    setup = build_encounter_setup(EncounterSelection(
        hero_ids=["karnok-stoneward-l1"], monster_ids=["srd-plesiosaurus"],
    ))
    reactor, mover = setup.monsters[0], setup.heroes[0]
    reactor.state.template = reactor.state.template.model_copy(update={"truesight_ft": 5})
    mover.state.active_effect_ids.append("invisible")

    assert resolve_opportunity_attack(
        1, 1, reactor, mover, setup, 10, 15, "speed", FixedDiceProvider([19]),
    ) is None
    assert reactor.state.reaction_available is True


def test_power_word_sight_gate_uses_truesight_range() -> None:
    actor = EncounterCombatant(
        combatant_id="actor",
        side="heroes",
        position_ft=0,
        state=build_combatant_state(
            build_varek_ashenmark_2014(17).model_copy(update={"truesight_ft": 30}),
        ),
    )
    target = EncounterCombatant(
        combatant_id="target",
        side="monsters",
        position_ft=40,
        state=build_combatant_state(build_varek_ashenmark_2014(17)),
    )
    actor.state.position = GridPosition(x=0, y=0)
    target.state.position = GridPosition(x=8, y=0)
    target.state.current_hp = 100
    target.state.active_effect_ids.append("invisible")
    kill = actor.state.template.hp_threshold_instant_death_actions[0]

    assert can_see(actor.state, target.state) is False
    assert legal_hp_threshold_instant_death(actor, target, kill) is False

    actor.state.template = actor.state.template.model_copy(update={"truesight_ft": 60})
    assert can_see(actor.state, target.state) is True
    assert legal_hp_threshold_instant_death(actor, target, kill) is True
