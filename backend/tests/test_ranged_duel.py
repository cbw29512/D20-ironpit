from app.combat.dice import FixedDiceProvider
from app.combat.engine import run_duel
from app.content.demo import build_demo_fighter, build_goblin_warrior


def test_ninety_foot_duel_closes_into_melee_instead_of_kiting() -> None:
    battle = run_duel(
        build_demo_fighter(),
        build_goblin_warrior(),
        FixedDiceProvider([20, 1, 20, 6, 6]),
        starting_distance_ft=90,
    )

    event_types = [event.event_type for event in battle.events]
    attack = next(event for event in battle.events if event.event_type == "attack")

    assert event_types[:6] == [
        "initiative", "initiative", "movement", "dash", "movement", "movement"
    ]
    assert battle.battlefield.distance_ft == 5
    assert attack.weapon_id == "scimitar"
    assert attack.critical is True
    assert attack.damage_roll is not None
    assert attack.damage_roll.total == 14
    assert not any(
        event.event_type == "attack" and event.weapon_id == "shortbow"
        for event in battle.events
    )
    assert battle.winner_id == "srd-goblin-warrior"
