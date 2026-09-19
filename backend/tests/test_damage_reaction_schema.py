from __future__ import annotations

import pytest
from pydantic import ValidationError

from app.domain.reactions import DamageReactionAttack


def test_damage_reaction_attack_defaults_to_creature_damage_and_melee() -> None:
    rule = DamageReactionAttack(source_feature="retaliation")

    assert rule.trigger == "damaged-by-creature"
    assert rule.source_range_ft == 5
    assert rule.attack_kind == "melee"


def test_damage_reaction_attack_rejects_empty_source_feature() -> None:
    with pytest.raises(ValidationError):
        DamageReactionAttack(source_feature="")


def test_damage_reaction_attack_rejects_nonpositive_source_range() -> None:
    with pytest.raises(ValidationError):
        DamageReactionAttack(source_feature="retaliation", source_range_ft=0)


def test_damage_reaction_attack_rejects_non_melee_policy() -> None:
    with pytest.raises(ValidationError):
        DamageReactionAttack(source_feature="retaliation", attack_kind="ranged")  # type: ignore[arg-type]
