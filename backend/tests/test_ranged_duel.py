from app.combat.dice import FixedDiceProvider
from app.combat.engine import run_duel
from app.content.demo import build_demo_fighter, build_goblin_warrior
from app.domain.models import RollMode


def test_ninety_foot_duel_forces_dash_then_shortbow_attack() -> None:
    battle = run_duel(
        build_demo_fighter(),
        build_goblin_warrior(),
        FixedDiceProvider([20, 1, 20, 6, 6]),
    )

    event_types = [event.event_type for event in battle.events]
    ranged_attack = next(
        event for event in battle.events
        if event.event_type == "attack" and event.weapon_id == "shortbow"
    )

    assert event_types[:5] == ["initiative", "initiative", "movement", "dash", "movement"]
    assert battle.battlefield.distance_ft == 30
    assert ranged_attack.projectile == "arrow"
    assert ranged_attack.attack_roll is not None
    assert ranged_attack.attack_roll.mode is RollMode.NORMAL
    assert ranged_attack.critical is True
    assert ranged_attack.damage_roll is not None
    assert ranged_attack.damage_roll.total == 14
    assert battle.winner_id == "srd-goblin-warrior"
