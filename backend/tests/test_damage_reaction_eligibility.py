from __future__ import annotations

from app.combat.damage_reaction_eligibility import DamageReactionTrigger, damage_reaction_is_eligible
from app.domain.reactions import DamageReactionAttack


def _trigger(**overrides: object) -> DamageReactionTrigger:
    values: dict[str, object] = {
        "applied_damage": 7,
        "source_is_creature": True,
        "source_distance_ft": 5,
        "reaction_available": True,
        "reactor_can_react": True,
    }
    values.update(overrides)
    return DamageReactionTrigger(**values)  # type: ignore[arg-type]


def test_damage_reaction_requires_policy_and_all_runtime_facts() -> None:
    policy = DamageReactionAttack(source_feature="retaliation")
    assert damage_reaction_is_eligible(policy, _trigger()) is True
    assert damage_reaction_is_eligible(None, _trigger()) is False
    assert damage_reaction_is_eligible(policy, _trigger(applied_damage=0)) is False
    assert damage_reaction_is_eligible(policy, _trigger(source_is_creature=False)) is False
    assert damage_reaction_is_eligible(policy, _trigger(reaction_available=False)) is False
    assert damage_reaction_is_eligible(policy, _trigger(reactor_can_react=False)) is False


def test_damage_reaction_enforces_authoritative_source_range() -> None:
    policy = DamageReactionAttack(source_feature="retaliation", source_range_ft=5)
    assert damage_reaction_is_eligible(policy, _trigger(source_distance_ft=5)) is True
    assert damage_reaction_is_eligible(policy, _trigger(source_distance_ft=10)) is False
    assert damage_reaction_is_eligible(policy, _trigger(source_distance_ft=-1)) is False
