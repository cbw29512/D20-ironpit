from app.combat.attack_actions import resolve_attack_action
from app.combat.dice import FixedDiceProvider
from app.combat.state import build_combatant_state
from app.content.demo import build_goblin_warrior
from app.content.gladiators import build_mara_stone


def test_extra_attack_resolves_two_attacks_for_one_action() -> None:
    mara = build_combatant_state(build_mara_stone())
    goblin = build_combatant_state(build_goblin_warrior())

    events = resolve_attack_action(
        1,
        1,
        mara,
        goblin,
        mara.template.weapon_attack,
        5,
        FixedDiceProvider([10, 4, 12, 5]),
    )

    assert len(events) == 2
    assert [event.sequence for event in events] == [1, 2]
    assert goblin.current_hp == 0
    assert mara.action_available is False


def test_extra_attack_stops_when_first_attack_drops_target() -> None:
    mara = build_combatant_state(build_mara_stone())
    goblin = build_combatant_state(build_goblin_warrior())

    events = resolve_attack_action(
        8,
        2,
        mara,
        goblin,
        mara.template.weapon_attack,
        5,
        FixedDiceProvider([20, 8, 8]),
    )

    assert len(events) == 1
    assert events[0].critical is True
    assert goblin.current_hp == 0
