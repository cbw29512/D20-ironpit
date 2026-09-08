from app.combat.dice import FixedDiceProvider
from app.combat.savage_attacker import roll_weapon_component
from app.combat.state import build_combatant_state
from app.content.fighter_progression import build_karnok_stoneward_level
from app.domain.models import DamageType


def test_savage_attacker_preserves_both_damage_candidates_and_accepted_choice() -> None:
    state = build_combatant_state(build_karnok_stoneward_level(1))
    component = roll_weapon_component(
        state,
        FixedDiceProvider([1, 2, 6, 6]),
        source="Greatsword",
        dice_count=2,
        dice_size=6,
        modifier=3,
        damage_type=DamageType.SLASHING,
        critical=False,
        turn_key="1:karnok",
    )

    assert component.rolls == [6, 6]
    assert component.total == 15
    assert len(component.revisions) == 1
    revision = component.revisions[0]
    assert revision.source_effect_id == "savage-attacker"
    assert revision.kind == "roll_twice_choose"
    assert revision.original_rolls == [1, 2]
    assert revision.replacement_rolls == [6, 6]
    assert revision.original_total == 6
    assert revision.replacement_total == 15
    assert revision.accepted == "replacement"


def test_savage_attacker_records_when_original_candidate_wins() -> None:
    state = build_combatant_state(build_karnok_stoneward_level(1))
    component = roll_weapon_component(
        state,
        FixedDiceProvider([6, 5, 1, 1]),
        source="Greatsword",
        dice_count=2,
        dice_size=6,
        modifier=3,
        damage_type=DamageType.SLASHING,
        critical=False,
        turn_key="1:karnok",
    )

    assert component.rolls == [6, 5]
    assert component.total == 14
    revision = component.revisions[0]
    assert revision.original_rolls == [6, 5]
    assert revision.replacement_rolls == [1, 1]
    assert revision.accepted == "original"
