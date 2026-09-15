from app.combat.repeat_save_transition import resolve_repeat_save_transition
from app.combat.timed_conditions import apply_timed_condition
from app.content.demo import build_goblin_warrior
from app.content.monster_source_staged_save_candidates import staged_condition_save_candidates
from app.domain.models import CombatantState


SILVER_BREATH = (
    "Paralyzing Breath. Constitution Saving Throw: DC 13, each creature in a 15-foot Cone. "
    "First Failure: The target has the Incapacitated condition until the end of its next turn, when it repeats the save. "
    "Second Failure: The target has the Paralyzed condition, and it repeats the save at the end of each of its turns, "
    "ending the effect on itself on a success. After 1 minute, it succeeds automatically."
)


def test_paralyzing_breath_compiles_as_staged_repeat_save() -> None:
    actions, resources = staged_condition_save_candidates("Silver Dragon Wyrmling", SILVER_BREATH, "action")
    assert resources == []
    assert len(actions) == 1
    action = actions[0]
    assert action.name == "Paralyzing Breath"
    assert action.save_ability == "constitution"
    assert action.dc == 13
    assert action.area is not None and action.area.shape == "cone" and action.area.length_ft == 15
    effect = action.failure_effects[0]
    assert effect.condition == "incapacitated"
    assert effect.repeat_save_timing == "target_turn_end"
    assert effect.repeat_save_failure_condition == "paralyzed"
    assert effect.automatic_success_after_rounds == 10


def test_second_failure_preserves_repeat_save_and_original_max_duration() -> None:
    template = build_goblin_warrior()
    state = CombatantState(template=template, current_hp=template.max_hp)
    apply_timed_condition(
        state,
        "incapacitated",
        "silver-dragon",
        source_effect_id="paralyzing-breath",
        applied_round=3,
        repeat_save_ability="constitution",
        repeat_save_dc=13,
        repeat_save_timing="target_turn_end",
        repeat_save_failure_condition="paralyzed",
        automatic_success_after_rounds=10,
    )
    effect = state.timed_effects[0]
    removed, applied = resolve_repeat_save_transition(state, effect, False, 4)
    assert removed == ["incapacitated"]
    assert applied == ["paralyzed"]
    escalated = state.timed_effects[0]
    assert escalated.repeat_save_ability == "constitution"
    assert escalated.repeat_save_dc == 13
    assert escalated.repeat_save_timing == "target_turn_end"
    assert escalated.repeat_save_failure_condition is None
    assert escalated.automatic_success_round == 13
