import pytest

from app.combat.dice import FixedDiceProvider
from app.combat.state import build_combatant_state
from app.combat.unarmed_damage import resolve_unarmed_damage_attack
from app.content.demo import build_demo_fighter, build_goblin_warrior
from app.domain.models import DamageType


def test_unarmed_damage_uses_strength_plus_proficiency_and_flat_damage() -> None:
    fighter = build_combatant_state(build_demo_fighter(), "fighter-1")
    goblin = build_combatant_state(build_goblin_warrior(), "goblin-1")

    event = resolve_unarmed_damage_attack(
        1, 1, fighter, goblin, 5, FixedDiceProvider([10])
    )

    assert event.attack_roll is not None
    assert event.attack_roll.modifier == 5
    assert event.hit is True
    assert event.damage_applied == 4
    assert event.damage_components[0].damage_type is DamageType.BLUDGEONING
    assert event.damage_components[0].rolls == []


def test_unarmed_critical_has_no_damage_die_to_double() -> None:
    fighter = build_combatant_state(build_demo_fighter(), "fighter-1")
    goblin = build_combatant_state(build_goblin_warrior(), "goblin-1")

    event = resolve_unarmed_damage_attack(
        1, 1, fighter, goblin, 5, FixedDiceProvider([20])
    )

    assert event.critical is True
    assert event.damage_applied == 4
    assert event.damage_components[0].rolls == []


def test_unarmed_damage_rejects_target_beyond_five_feet() -> None:
    fighter = build_combatant_state(build_demo_fighter(), "fighter-1")
    goblin = build_combatant_state(build_goblin_warrior(), "goblin-1")

    with pytest.raises(ValueError, match="outside 5-foot reach"):
        resolve_unarmed_damage_attack(
            1, 1, fighter, goblin, 10, FixedDiceProvider([20])
        )
