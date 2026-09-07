from app.content.monster_survival_source_audit import survival_action_issues
from app.content.roster import build_arena_roster
from app.domain.models import DamageType, MaxHpReductionRider


def _attack_with_drain(damage_type: DamageType | None = None):
    base = next(item for item in build_arena_roster().monsters if item.name == "Commoner").weapon_attack
    return base.model_copy(update={"max_hp_reduction": MaxHpReductionRider(damage_type=damage_type)})


def test_hit_point_maximum_reduction_fails_closed_without_runtime_rider() -> None:
    actions = (
        "Life Drain. Melee Attack Roll: +4, reach 5 ft. Hit: 7 (2d6) Necrotic damage. "
        "If the target is a creature, its Hit Point maximum decreases by an amount equal to the damage taken."
    )
    assert survival_action_issues(actions) == [
        "unsupported-survival-rider:hit-point-maximum-reduction"
    ]


def test_hit_point_maximum_reduction_is_modeled_by_normalized_attack_rider() -> None:
    actions = (
        "Life Drain. Melee Attack Roll: +4, reach 5 ft. Hit: 7 (2d6) Necrotic damage. "
        "If the target is a creature, its Hit Point maximum decreases by an amount equal to the damage taken."
    )
    assert survival_action_issues(actions, [_attack_with_drain()]) == []


def test_typed_hit_point_maximum_reduction_requires_matching_damage_type() -> None:
    actions = "The target’s Hit Point maximum is reduced by an amount equal to the Acid damage taken."
    assert survival_action_issues(actions, [_attack_with_drain(DamageType.NECROTIC)]) == [
        "survival-rider-damage-type-mismatch"
    ]
    assert survival_action_issues(actions, [_attack_with_drain(DamageType.ACID)]) == []


def test_hit_point_maximum_reduction_tolerates_source_line_breaks() -> None:
    actions = "The target’s Hit Point maximum\n\ndecreases by an amount equal to the Necrotic damage taken."
    assert survival_action_issues(actions) == [
        "unsupported-survival-rider:hit-point-maximum-reduction",
        "survival-rider-damage-type-mismatch",
    ]


def test_immediate_combatant_creation_action_fails_closed() -> None:
    actions = (
        "Create Specter. The wraith targets a Humanoid corpse within 10 feet. "
        "The target's spirit rises as a Specter in the nearest unoccupied space."
    )
    assert survival_action_issues(actions) == ["unsupported-combatant-creation-action"]


def test_delayed_resurrection_outside_combat_does_not_block() -> None:
    actions = "A Humanoid slain by this attack rises 24 hours later as a Zombie under the wight's control."
    assert survival_action_issues(actions) == []


def test_plain_damage_attack_has_no_survival_rider_issue() -> None:
    actions = "Bite. Melee Attack Roll: +4, reach 5 ft. Hit: 7 (2d4 + 2) Piercing damage."
    assert survival_action_issues(actions) == []
