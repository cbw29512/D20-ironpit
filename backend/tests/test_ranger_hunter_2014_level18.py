from __future__ import annotations

from app.combat.conditions import attack_roll_condition_sources
from app.content.ranger_hunter_2014_runtime import build_rowan_ashtrail_2014
from app.domain.models import CombatantState


def _state(template):
    return CombatantState(template=template, current_hp=template.max_hp)


def test_level_eighteen_feral_senses_suppresses_only_visibility_disadvantage() -> None:
    before = _state(build_rowan_ashtrail_2014(17))
    ranger = _state(build_rowan_ashtrail_2014(18))
    target = _state(build_rowan_ashtrail_2014(18))

    before.active_effect_ids.append("blinded")
    target.active_effect_ids.append("invisible")
    _, before_disadvantage = attack_roll_condition_sources(before, target, 30)

    ranger.active_effect_ids.append("blinded")
    _, feral_disadvantage = attack_roll_condition_sources(ranger, target, 30)

    assert before_disadvantage == 2
    assert feral_disadvantage == 0
    assert ranger.template.progression_features.ignore_unseen_target_attack_disadvantage is True


def test_level_eighteen_feral_senses_does_not_grant_sight_or_remove_other_disadvantage() -> None:
    ranger = _state(build_rowan_ashtrail_2014(18))
    target = _state(build_rowan_ashtrail_2014(18))
    ranger.active_effect_ids.extend(["poisoned", "blinded"])
    target.active_effect_ids.append("invisible")

    _, disadvantage = attack_roll_condition_sources(ranger, target, 30)

    assert disadvantage == 1
