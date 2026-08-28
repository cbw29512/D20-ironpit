import pytest

from app.combat.attacks import resolve_attack
from app.combat.dice import FixedDiceProvider
from app.combat.state import build_combatant_state
from app.content.demo import build_demo_fighter, build_goblin_warrior
from app.domain.models import ActorVisibilityState, BattlefieldState, CoverLevel


def battlefield_with_cover(target_id: str, cover: CoverLevel) -> BattlefieldState:
    return BattlefieldState(
        distance_ft=30,
        visibility_by_actor={target_id: ActorVisibilityState(cover=cover)},
    )


def test_half_cover_adds_two_to_target_ac() -> None:
    goblin = build_combatant_state(build_goblin_warrior())
    fighter = build_combatant_state(build_demo_fighter())
    shortbow = goblin.template.alternate_weapon_attacks[0]
    battlefield = battlefield_with_cover(fighter.template.id, CoverLevel.HALF)

    event = resolve_attack(
        1, 1, goblin, fighter, shortbow, 30, FixedDiceProvider([16]),
        battlefield=battlefield,
    )

    assert event.attack_roll is not None
    assert event.attack_roll.total == 20
    assert event.hit is False
    assert "Cover adds +2 AC" in event.description


def test_three_quarters_cover_adds_five_to_target_ac() -> None:
    goblin = build_combatant_state(build_goblin_warrior())
    fighter = build_combatant_state(build_demo_fighter())
    shortbow = goblin.template.alternate_weapon_attacks[0]
    battlefield = battlefield_with_cover(fighter.template.id, CoverLevel.THREE_QUARTERS)

    event = resolve_attack(
        1, 1, goblin, fighter, shortbow, 30, FixedDiceProvider([19]),
        battlefield=battlefield,
    )

    assert event.attack_roll is not None
    assert event.attack_roll.total == 23
    assert event.hit is False
    assert "Cover adds +5 AC" in event.description


def test_total_cover_prevents_direct_attack_targeting() -> None:
    goblin = build_combatant_state(build_goblin_warrior())
    fighter = build_combatant_state(build_demo_fighter())
    shortbow = goblin.template.alternate_weapon_attacks[0]
    battlefield = battlefield_with_cover(fighter.template.id, CoverLevel.TOTAL)

    with pytest.raises(RuntimeError, match="Attack resolution failed"):
        resolve_attack(
            1, 1, goblin, fighter, shortbow, 30, FixedDiceProvider([20]),
            battlefield=battlefield,
        )


def test_natural_twenty_still_hits_through_partial_cover() -> None:
    goblin = build_combatant_state(build_goblin_warrior())
    fighter = build_combatant_state(build_demo_fighter())
    shortbow = goblin.template.alternate_weapon_attacks[0]
    battlefield = battlefield_with_cover(fighter.template.id, CoverLevel.THREE_QUARTERS)

    event = resolve_attack(
        1, 1, goblin, fighter, shortbow, 30, FixedDiceProvider([20, 3, 4]),
        battlefield=battlefield,
    )

    assert event.critical is True
    assert event.hit is True
