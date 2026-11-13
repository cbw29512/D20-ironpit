"""Source-complete Dryad Fey Charm binds to ordinary saves and Charmed."""
from __future__ import annotations

import logging

import pytest

from app.combat.saving_throw_legality import legal_save_action
from app.combat.state import build_combatant_state
from app.content.capability_compiler import _compile_save
from app.content.demo import build_demo_fighter, build_goblin_warrior
from app.content.monster_basic_candidates_2014 import basic_blockers_2014
from app.content.monster_save_capabilities_2014 import save_capabilities_2014
from app.content.monster_source_2014 import load_monster_source_2014
from app.content.monster_source_fey_charm_2014 import source_proven_fey_charm_2014
from app.content.monster_supported_extra_actions_2014 import source_supported_extra_action_labels_2014
from app.domain.encounters import EncounterCombatant
from app.domain.save_effects import FailedSaveTimedEffect
from scripts.browser_template_serializer import _save

logger = logging.getLogger(__name__)


def _card():
    try:
        matches = [card for card in load_monster_source_2014()
                   if source_proven_fey_charm_2014(card)]
        assert len(matches) == 1
        return matches[0]
    except Exception:
        logger.exception("The printed 2014 Fey Charm action cannot be located.")
        raise


def test_fey_charm_source_uses_generic_target_sight_save_and_capacity() -> None:
    try:
        source = _card()
        baseline = source.model_dump_json()
        (capability,) = source_proven_fey_charm_2014(source)
        action = _compile_save(capability)
        serialized = _save(action)
        assert action.id == "fey-charm" and action.name == "Fey Charm"
        assert action.dc == 14 and action.save_ability == "wisdom"
        assert action.range_ft == 30 and action.requires_target_sight
        assert action.requires_target_to_see_source
        assert action.required_target_creature_types == ["humanoid", "beast"]
        assert action.effect_tags == ["charmed"]
        assert action.source_effect_immunity_on_success
        rider = action.failed_save_timed_effect
        assert rider is not None
        assert rider.effect_id == "charmed"
        assert rider.duration_rounds == 14400
        assert rider.source_target_limit is None
        assert rider.source_target_limits_by_creature_type == {
            "humanoid": 1, "beast": 3,
        }
        assert rider.damage_repeat_save_trigger == "source_or_allies"
        assert rider.repeat_save_timing is None
        assert rider.ends_if_source_dead and not rider.source_effect_immunity_on_end
        assert rider.source_effect_immunity_on_repeat_save_success
        browser = serialized["failedSaveTimedEffect"]
        assert browser["sourceTargetLimitsByCreatureType"] == {
            "humanoid": 1, "beast": 3,
        }
        assert browser["damageRepeatSaveTrigger"] == "source_or_allies"
        assert browser["sourceEffectImmunityOnRepeatSaveSuccess"] is True
        assert serialized["requiresTargetToSeeSource"]
        assert "fey charm" in source_supported_extra_action_labels_2014(source)
        assert "Fey Charm" in [x.name for x in save_capabilities_2014(source)]
        assert basic_blockers_2014(source) == ()
        assert source.model_dump_json() == baseline
    except Exception:
        logger.exception("2014 Fey Charm source/runtime/browser parity failed.")
        raise


@pytest.mark.parametrize("old,new", [
    ("30 feet", "40 feet"),
    ("DC 14 Wisdom", "DC 16 Wisdom"),
    ("humanoid or beast", "humanoid or fiend"),
    ("If the target can see the dryad", "If the target can hear the dryad"),
    ("isn't under the dryad's control", "is under the dryad's control"),
    ("the dryad or its allies", "any creature"),
    ("effect lasts 24 hours", "effect lasts 12 hours"),
    ("the dryad dies", "the dryad sleeps"),
    ("next 24 hours", "next 12 hours"),
    ("one humanoid and up to three beasts", "two humanoids and one beast"),
])
def test_fey_charm_source_mutations_fail_closed(old, new):
    try:
        original = _card()
        assert old in original.source_actions
        edited = original.model_copy(update={
            "source_actions": original.source_actions.replace(old, new),
        })
        assert source_proven_fey_charm_2014(edited) == []
        assert "fey charm" not in source_supported_extra_action_labels_2014(edited)
        assert "source:extra-action" in basic_blockers_2014(edited)
    except Exception:
        logger.exception("Changed printed Fey Charm source was incorrectly admitted.")
        raise


def test_fey_charm_target_types_and_reciprocal_sight_are_generic():
    try:
        source = _card()
        renamed = source.model_copy(update={"id": "fey-synthetic", "name": "Any Fey"})
        assert source_proven_fey_charm_2014(renamed) == source_proven_fey_charm_2014(source)
        action = _compile_save(source_proven_fey_charm_2014(renamed)[0])
        caster = EncounterCombatant(
            combatant_id="caster", side="monsters", position_ft=0,
            state=build_combatant_state(build_goblin_warrior()),
        )
        target = EncounterCombatant(
            combatant_id="target", side="heroes", position_ft=5,
            state=build_combatant_state(build_demo_fighter().model_copy(
                update={"creature_type": "humanoid"},
            )),
        )
        assert legal_save_action(action, target, 5, caster.combatant_id, caster)
        target.state.active_effect_ids.append("blinded")
        assert not legal_save_action(action, target, 5, caster.combatant_id, caster)
        target.state.active_effect_ids.remove("blinded")
        other = target.state.template.model_copy(update={"creature_type": "construct"})
        target.state.template = other
        assert not legal_save_action(action, target, 5, caster.combatant_id, caster)
    except Exception:
        logger.exception("Fey Charm generic target eligibility regressed.")
        raise


def test_typed_capacity_validation_rejects_unbounded_configuration():
    try:
        with pytest.raises(ValueError, match="limit"):
            FailedSaveTimedEffect(effect_id="charmed",
                                  source_target_limits_by_creature_type={"beast": 21})
        with pytest.raises(ValueError, match="combine"):
            FailedSaveTimedEffect(effect_id="charmed", source_target_limit=1,
                                  source_target_limits_by_creature_type={"beast": 3})
    except Exception:
        logger.exception("Source-specific type-capacity schema accepted illegal values.")
        raise
