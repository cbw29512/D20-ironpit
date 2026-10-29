"""Generic swallowed damage accounting, independent of monster names."""
from app.combat.swallowed_damage_accounting import (
    record_swallowed_victim_damage, swallowed_regurgitation_ready,
)
from app.domain.size import CreatureSize
from app.domain.swallowed_state import SwallowedState


def _effect():
    return SwallowedState(
        source_id="owner", source_name="Swallow", damage_dice_count=6,
        damage_dice_size=6, damage_type="acid", exit_movement_ft=15,
        target_size=CreatureSize.MEDIUM,
        regurgitation_damage_threshold=30, regurgitation_save_ability="constitution",
        regurgitation_save_dc=14, regurgitation_range_ft=10,
    )


def test_damage_accumulates_only_from_swallowed_victim_in_same_turn():
    effect = _effect()
    def record(attacker, amount, turn="round2:victim"):
        return record_swallowed_victim_damage(
            effect, victim_id="victim", attacker_id=attacker,
            owner_id="owner", actual_damage=amount, turn_key=turn,
        )
    assert record("other", 60) == 0
    assert effect.damage_from_victim_this_turn == 0
    assert record("victim", 18) == 18
    assert not swallowed_regurgitation_ready(effect)
    assert record("victim", 12) == 30
    assert swallowed_regurgitation_ready(effect)
    assert record("victim", 4, "round3:victim") == 4
    assert not swallowed_regurgitation_ready(effect)


def test_unrelated_owner_or_negative_damage_cannot_trigger():
    import pytest

    effect = _effect()
    assert record_swallowed_victim_damage(
        effect, victim_id="victim", attacker_id="victim",
        owner_id="other", actual_damage=100, turn_key="1:victim",
    ) == 0
    with pytest.raises(ValueError):
        record_swallowed_victim_damage(
            effect, victim_id="victim", attacker_id="victim",
            owner_id="owner", actual_damage=-1, turn_key="1:victim",
        )
