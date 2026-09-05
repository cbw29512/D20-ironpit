from app.combat.forced_movement import apply_forced_movement
from app.combat.encounter_setup import build_encounter_setup
from app.domain.forced_movement import ForcedMovement
from app.domain.models import BattleEvent, EncounterSelection
from app.domain.size import CreatureSize


def _fight():
    setup = build_encounter_setup(EncounterSelection(hero_ids=["karnok-stoneward-l1"], monster_ids=["srd-commoner"]))
    source, target = setup.monsters[0], setup.heroes[0]
    source.position_ft, target.position_ft = 10, 20
    event = BattleEvent(sequence=1, round_number=1, event_type="attack", actor_id=source.combatant_id,
                        actor_name=source.state.template.name, target_id=target.combatant_id,
                        target_name=target.state.template.name, hit=True, animation="hit", description="Hit.")
    return setup, source, target, event


def test_push_increases_distance_and_logs_movement() -> None:
    setup, source, target, event = _fight()
    moved = apply_forced_movement(source, target, ForcedMovement(direction="push", distance_ft=10), event, setup)
    assert moved == 10 and abs(target.position_ft - source.position_ft) == 20
    assert event.distance_before_ft == 10 and event.distance_after_ft == 20 and event.movement_ft == 10
    assert "pushed 10 feet" in event.description


def test_pull_stops_at_source_without_overshooting() -> None:
    setup, source, target, event = _fight(); target.position_ft = 18
    moved = apply_forced_movement(source, target, ForcedMovement(direction="pull", distance_ft=15), event, setup)
    assert moved == 8 and target.position_ft == source.position_ft and event.distance_after_ft == 0


def test_size_gate_and_miss_do_not_move() -> None:
    setup, source, target, event = _fight(); before = target.position_ft
    small_only = ForcedMovement(direction="push", distance_ft=10, max_target_size=CreatureSize.SMALL)
    assert apply_forced_movement(source, target, small_only, event, setup) == 0 and target.position_ft == before
    event.hit = False
    assert apply_forced_movement(source, target, ForcedMovement(direction="push", distance_ft=10), event, setup) == 0


def test_push_preserves_pairwise_distances_when_crossing_zero_boundary() -> None:
    setup, source, target, event = _fight(); source.position_ft, target.position_ft = 5, 0
    before_others = [abs(member.position_ft - source.position_ft) for member in [*setup.heroes, *setup.monsters] if member is not target]
    apply_forced_movement(source, target, ForcedMovement(direction="push", distance_ft=10), event, setup)
    assert abs(target.position_ft - source.position_ft) == 15
    after_others = [abs(member.position_ft - source.position_ft) for member in [*setup.heroes, *setup.monsters] if member is not target]
    assert before_others == after_others
