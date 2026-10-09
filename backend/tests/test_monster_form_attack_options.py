from __future__ import annotations

import pytest

from app.combat.monster_form_attack_options import compose_monster_form_attack_sequences
from app.content.druid_2014_wild_shape_forms import canonical_wild_shape_template_2014
from app.domain.attack_action_definitions import (
    AttackActionDefinition, AttackActionSlot, AttackActionVariant,
    PreviousAttackRequirement,
)


def _sources():
    source = canonical_wild_shape_template_2014(2)
    owner_attack = AttackActionDefinition(
        id="owner-multiattack", name="Multiattack",
        slots=[AttackActionSlot(attack_ids=["owner-mace"]) for _ in range(2)],
        is_attack_action=True,
    )
    form_attack = AttackActionDefinition(
        id="shape-multiattack", name="Multiattack",
        slots=[
            AttackActionSlot(attack_ids=["shape-claw"]),
            AttackActionSlot(
                attack_ids=["shape-sting"],
                previous_attack=PreviousAttackRequirement(same_target=True),
            ),
        ],
        is_attack_action=True,
    )
    return (
        source.model_copy(update={"id": "2014-deva", "attack_action": owner_attack}),
        source.model_copy(update={"id": "2014-test-shape", "attack_action": form_attack}),
    )


def test_original_and_form_source_sequences_remain_alternatives() -> None:
    owner, form = _sources()
    result = compose_monster_form_attack_sequences(owner, form)
    assert result is not None
    assert result.slots == []
    assert len(result.variants) == 2
    assert [v.id for v in result.variants] == [
        "2014-deva:owner-multiattack", "2014-test-shape:shape-multiattack",
    ]
    assert len(result.variants[0].slots) == len(result.variants[1].slots) == 2
    assert result.variants[0].slots[0].attack_ids == ["owner-mace"]
    assert result.variants[1].slots[1].attack_ids == ["shape-sting"]
    assert result.variants[1].slots[1].previous_attack.same_target
    assert result.is_attack_action
    assert owner.attack_action.variants == []
    assert form.attack_action.variants == []
    assert form.attack_action.slots[1].previous_attack.same_target


def test_source_variants_and_nonattack_qualification_stay_intact() -> None:
    owner, form = _sources()
    original = form.attack_action.model_copy(update={
        "slots": [],
        "variants": [
            AttackActionVariant(id="melee", slots=[AttackActionSlot(attack_ids=["shape-claw"])]),
            AttackActionVariant(id="ranged", slots=[AttackActionSlot(attack_ids=["shape-rock"])]),
        ],
        "is_attack_action": False,
    })
    form = form.model_copy(update={"attack_action": original})
    merged = compose_monster_form_attack_sequences(owner, form)
    assert [v.id for v in merged.variants] == [
        "2014-deva:owner-multiattack",
        "2014-test-shape:melee",
        "2014-test-shape:ranged",
    ]
    assert merged.is_attack_action is False


def test_fail_closed_on_cross_edition_or_distinct_actions() -> None:
    owner, form = _sources()
    with pytest.raises(ValueError, match="edition"):
        compose_monster_form_attack_sequences(owner, form.model_copy(update={"ruleset": "2024"}))
    with pytest.raises(ValueError, match="Only monster"):
        compose_monster_form_attack_sequences(owner.model_copy(update={"kind": "character"}), form)
    with pytest.raises(ValueError, match="Distinctly named"):
        renamed = form.attack_action.model_copy(update={"name": "Other action"})
        compose_monster_form_attack_sequences(owner, form.model_copy(update={"attack_action": renamed}))
    unchanged = owner.attack_action
    clone = compose_monster_form_attack_sequences(owner, form.model_copy(update={"attack_action": None}))
    assert clone == unchanged and clone is not unchanged


def test_no_phantom_extra_action_without_two_source_actions() -> None:
    owner, form = _sources()
    no_action = owner.model_copy(update={"attack_action": None})
    result = compose_monster_form_attack_sequences(no_action, form)
    assert result == form.attack_action
    assert result is not form.attack_action
    assert compose_monster_form_attack_sequences(
        no_action, form.model_copy(update={"attack_action": None})
    ) is None
