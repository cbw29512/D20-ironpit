from app.combat.attack_actions import resolve_attack_action
from app.combat.condition_lifecycle import resolve_source_condition_timing
from app.combat.dice import FixedDiceProvider
from app.combat.encounter_setup import build_encounter_setup
from app.combat.state import begin_turn
from app.domain.grid import GridPosition
from app.domain.models import EncounterSelection


def test_lion_roar_replaces_one_rend_then_frightened_expires_at_source_turn_start() -> None:
    setup = build_encounter_setup(EncounterSelection(
        hero_ids=["karnok-stoneward-l1"], monster_ids=["srd-lion"],
    ))
    hero, lion = setup.heroes[0], setup.monsters[0]
    hero.state.position = GridPosition(x=6, y=6)
    lion.state.position = GridPosition(x=7, y=6)
    begin_turn(lion.state)

    events, sequence = resolve_attack_action(
        1, 1, lion, setup, FixedDiceProvider([1, 19, 4]),
    )

    assert [event.event_type for event in events] == ["saving_throw", "attack"]
    assert events[0].feature_id == "lion-roar"
    assert events[0].save_succeeded is False
    assert events[0].applied_condition_ids == ["frightened"]
    assert events[1].attack_name == "Rend"
    assert "frightened" in hero.state.active_effect_ids
    fear = next(effect for effect in hero.state.timed_effects if effect.effect_id == "frightened")
    assert fear.source_id == lion.combatant_id
    assert fear.source_effect_id == "lion-roar"
    assert fear.expiry_timing == "source_turn_start"
    assert fear.repeat_save_ability is None

    expiry, sequence = resolve_source_condition_timing(
        sequence, 2, lion, setup, "source_turn_start",
    )
    assert len(expiry) == 1
    assert expiry[0].removed_condition_ids == ["frightened"]
    assert "frightened" not in hero.state.active_effect_ids
