from __future__ import annotations

import pytest

from app.content.shared_fire_shield import fire_shield_variants
from app.content.warlock_2024_zone_spells import fire_shield_2024
from app.domain.weapons_base import DamageType


def test_fire_shield_shared_variants_are_identical_across_2014_and_2024_callers() -> None:
    """The two editions may share this mechanic; source contracts remain separate."""
    shared = fire_shield_variants(4)
    from_warlock = fire_shield_2024(4)
    assert [action.model_dump(mode="json") for action in shared] == [
        action.model_dump(mode="json") for action in from_warlock
    ]
    assert {action.id for action in shared} == {"fire-shield-warm", "fire-shield-chill"}
    warm, chill = shared
    assert warm.damage_resistances == [DamageType.COLD]
    assert warm.melee_hit_retaliation.damage_type == DamageType.FIRE
    assert chill.damage_resistances == [DamageType.FIRE]
    assert chill.melee_hit_retaliation.damage_type == DamageType.COLD
    for action in shared:
        assert action.selection_group == "fire-shield-variants"
        assert action.selection_strategy == "incoming-damage"
        assert action.melee_hit_retaliation.dice_count == 2
        assert action.melee_hit_retaliation.dice_size == 8
        assert action.melee_hit_retaliation.range_ft == 5
        assert action.duration_rounds == 100
        assert action.concentration is False
        assert action.resource_id == "spell-slot-4"


def test_fire_shield_legal_slot_levels_are_not_arbitrarily_restricted_to_four() -> None:
    assert fire_shield_variants(9)[0].resource_id == "spell-slot-9"
    with pytest.raises(ValueError, match="fourth-level"):
        fire_shield_variants(3)
