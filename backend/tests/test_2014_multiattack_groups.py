from app.combat.attack_action_policy import filtered_slot
from app.domain.actions import AttackActionDefinition, AttackActionSlot
from app.domain.attack_action_policy import AttackActionPolicy


def _definition() -> AttackActionDefinition:
    slot = AttackActionSlot(attack_ids=["longsword", "longbow", "life-drain"])
    return AttackActionDefinition(
        id="wight-multiattack", name="Multiattack", slots=[slot, slot],
        policy=AttackActionPolicy(
            at_most_once_attack_ids=["life-drain"],
            exclusive_attack_groups=[["longsword", "life-drain"], ["longbow"]],
        ),
    )


def test_melee_family_allows_life_drain_substitution_but_not_longbow() -> None:
    definition = _definition(); slot = definition.slots[1]
    after_longsword = filtered_slot(definition, slot, {"longsword"})
    assert after_longsword.attack_ids == ["longsword", "life-drain"]

    after_life_drain = filtered_slot(definition, slot, {"life-drain"})
    assert after_life_drain.attack_ids == ["longsword"]


def test_longbow_family_remains_exclusive() -> None:
    definition = _definition(); slot = definition.slots[1]
    assert filtered_slot(definition, slot, {"longbow"}).attack_ids == ["longbow"]
