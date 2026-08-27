from app.combat.attack_actions import resolve_attack_action
from app.combat.dice import FixedDiceProvider
from app.combat.state import build_combatant_state
from app.content.demo import build_goblin_warrior
from app.content.gladiators import build_mara_stone
from app.content.srd_monsters import build_knight


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


def test_knight_multiattack_emits_two_complete_attack_events() -> None:
    knight = build_combatant_state(build_knight())
    mara = build_combatant_state(build_mara_stone())

    events = resolve_attack_action(
        20,
        4,
        knight,
        mara,
        knight.template.weapon_attack,
        5,
        FixedDiceProvider([14, 3, 3, 4, 14, 3, 3, 4]),
    )

    assert len(events) == 2
    assert [event.damage_applied for event in events] == [13, 13]
    assert mara.current_hp == 18
    assert knight.action_available is False
