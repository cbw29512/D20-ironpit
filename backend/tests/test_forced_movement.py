from app.combat.forced_movement import apply_attack_push
from app.combat.state import build_combatant_state
from app.content.demo import build_demo_fighter, build_goblin_warrior
from app.domain.encounters import EncounterCombatant
from app.domain.size import CreatureSize


def _member(combatant_id: str, side: str, position_ft: int, template) -> EncounterCombatant:
    return EncounterCombatant(
        combatant_id=combatant_id,
        side=side,
        position_ft=position_ft,
        state=build_combatant_state(template),
    )


def _push_attack(maximum: CreatureSize):
    return build_demo_fighter().weapon_attack.model_copy(
        update={"push_target_away_ft": 10, "push_target_max_size": maximum},
    )


def test_attack_push_moves_allowed_target_straight_away() -> None:
    attacker = _member("attacker", "heroes", 0, build_demo_fighter())
    target = _member("target", "monsters", 5, build_goblin_warrior())

    moved = apply_attack_push(attacker, target, _push_attack(CreatureSize.LARGE), hit=True)

    assert moved == 10
    assert target.position_ft == 15


def test_attack_push_respects_maximum_target_size() -> None:
    attacker = _member("attacker", "heroes", 0, build_demo_fighter())
    target_template = build_goblin_warrior().model_copy(update={"size": CreatureSize.HUGE})
    target = _member("target", "monsters", 5, target_template)

    moved = apply_attack_push(attacker, target, _push_attack(CreatureSize.LARGE), hit=True)

    assert moved == 0
    assert target.position_ft == 5


def test_attack_push_does_nothing_on_miss() -> None:
    attacker = _member("attacker", "heroes", 0, build_demo_fighter())
    target = _member("target", "monsters", 5, build_goblin_warrior())

    moved = apply_attack_push(attacker, target, _push_attack(CreatureSize.LARGE), hit=False)

    assert moved == 0
    assert target.position_ft == 5


def test_attack_push_does_not_move_dead_target() -> None:
    attacker = _member("attacker", "heroes", 0, build_demo_fighter())
    target = _member("target", "monsters", 5, build_goblin_warrior())
    target.state.current_hp = 0
    target.state.is_alive = False
    target.state.is_dead = True

    moved = apply_attack_push(attacker, target, _push_attack(CreatureSize.LARGE), hit=True)

    assert moved == 0
    assert target.position_ft == 5
