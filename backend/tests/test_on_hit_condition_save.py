from __future__ import annotations

from app.combat.attacks import resolve_attack
from app.combat.dice import FixedDiceProvider
from app.combat.state import build_combatant_state
from app.content.audited_fighter import build_karnok_stoneward
from app.content.demo import build_goblin_warrior
from app.domain.size import CreatureSize
from app.domain.weapons import OnHitConditionSave


def _attacker():
    state = build_combatant_state(build_karnok_stoneward().model_copy(update={"combat_traits": []}, deep=True))
    attack = state.template.weapon_attack.model_copy(update={
        "id": "save-to-prone-test",
        "on_hit_condition_save": OnHitConditionSave(
            save_ability="strength", dc=13, condition_id="prone", max_target_size=CreatureSize.LARGE,
        ),
    }, deep=True)
    return state, attack


def _target(*, size: CreatureSize = CreatureSize.MEDIUM, immune: bool = False):
    source = build_goblin_warrior()
    bonuses = dict(source.saving_throw_bonuses); bonuses["strength"] = 0
    template = source.model_copy(update={
        "armor_class": 10, "max_hp": 40, "saving_throw_bonuses": bonuses, "size": size,
        "condition_immunities": ["prone"] if immune else [],
    }, deep=True)
    return build_combatant_state(template)


def _hit(target, values):
    attacker, attack = _attacker()
    return resolve_attack(1, 1, attacker, target, attack, 5, FixedDiceProvider(values), spend_action=False)


def test_failed_on_hit_save_applies_condition_and_records_audit_fields() -> None:
    target = _target()
    event = _hit(target, [15, 4, 5])
    assert event.hit is True
    assert event.save_ability == "strength"
    assert event.save_dc == 13
    assert event.save_succeeded is False
    assert event.saving_throw_roll is not None and event.saving_throw_roll.total == 5
    assert "prone" in event.applied_condition_ids
    assert "prone" in target.active_effect_ids


def test_successful_on_hit_save_does_not_apply_condition() -> None:
    target = _target()
    event = _hit(target, [15, 4, 18])
    assert event.save_succeeded is True
    assert "prone" not in target.active_effect_ids
    assert "prone" not in event.applied_condition_ids


def test_on_hit_save_skips_oversized_and_immune_targets() -> None:
    huge = _target(size=CreatureSize.HUGE)
    immune = _target(immune=True)
    huge_event = _hit(huge, [15, 4])
    immune_event = _hit(immune, [15, 4])
    assert huge_event.save_dc is None and "prone" not in huge.active_effect_ids
    assert immune_event.save_dc is None and "prone" not in immune.active_effect_ids
