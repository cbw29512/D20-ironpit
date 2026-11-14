"""A legal HP-threshold spell may be blocked by canonical condition immunity."""
from types import SimpleNamespace
from unittest.mock import patch

from app.combat.hp_threshold_condition import resolve_hp_threshold_condition


def _combatant(name, side):
    state = SimpleNamespace(template=SimpleNamespace(name=name),
                            resources={}, active_effect_ids=[], timed_effects=[])
    return SimpleNamespace(combatant_id=name, side=side, state=state)


def test_immune_target_consumes_action_and_records_no_effect():
    """A renamed source ability uses the ordinary no-effect condition result."""
    try:
        caster = _combatant("caster", "heroes")
        target = _combatant("swarm", "monsters")
        action = SimpleNamespace(
            name="Renamed Condition Ability", id="renamed-condition",
            action_cost="action", resource_id=None, resource_cost=1,
            condition_id="stunned", magical_effect=True,
            repeat_save_ability="constitution", repeat_save_dc=18,
            repeat_save_timing="target_turn_end", animation="spell-condition",
        )
        setup = SimpleNamespace(heroes=[caster], monsters=[target])
        with (
            patch("app.combat.hp_threshold_condition.legal_hp_threshold_condition",
                  return_value=True),
            patch("app.combat.hp_threshold_condition.apply_timed_condition",
                  return_value=None) as apply_condition,
            patch("app.combat.hp_threshold_condition.spend") as spend,
        ):
            event = resolve_hp_threshold_condition(1, 1, caster, target, action, setup)
        spend.assert_called_once_with(caster.state, "action")
        apply_condition.assert_called_once()
        assert event.feature_id == action.id
        assert event.applied_condition_ids == []
        assert "is unaffected" in event.description
        assert target.state.active_effect_ids == []
    except Exception:
        import logging
        logging.getLogger(__name__).exception(
            "Immune threshold-condition Python reference regression failed.")
        raise


def test_condition_still_applies_if_not_immune():
    """Ordinary applications retain their standard condition event semantics."""
    try:
        caster = _combatant("caster", "heroes")
        target = _combatant("target", "monsters")
        action = SimpleNamespace(
            name="Generic Threshold Debuff", id="debuff",
            action_cost="action", resource_id=None, resource_cost=1,
            condition_id="stunned", magical_effect=True,
            repeat_save_ability="constitution", repeat_save_dc=18,
            repeat_save_timing="target_turn_end", animation="spell-condition",
        )
        setup = SimpleNamespace(heroes=[caster], monsters=[target])
        with (
            patch("app.combat.hp_threshold_condition.legal_hp_threshold_condition",
                  return_value=True),
            patch("app.combat.hp_threshold_condition.apply_timed_condition",
                  return_value="stunned"),
            patch("app.combat.hp_threshold_condition.spend"),
        ):
            event = resolve_hp_threshold_condition(1, 1, caster, target, action, setup)
        assert event.applied_condition_ids == ["stunned"]
        assert "is Stunned" in event.description
    except Exception:
        import logging
        logging.getLogger(__name__).exception(
            "Nonimmune threshold-condition Python reference regression failed.")
        raise
