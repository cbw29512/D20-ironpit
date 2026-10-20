"""2014 Sea Hag Death Glare: source card binding and universal target legality."""
from __future__ import annotations

import pytest

from app.combat.dice import FixedDiceProvider
from app.combat.saving_throws import legal_save_action, resolve_save_action
from app.combat.state import build_combatant_state
from app.content.capability_compiler import _compile_save, compile_combatant
from app.content.monster_basic_candidates_2014 import basic_blockers_2014
from app.content.monster_definition_adapter_2014 import adapt_basic_monster_2014
from app.content.monster_source_2014 import load_monster_source_2014
from app.content.monster_source_conditioned_save_2014 import source_proven_conditioned_saves_2014
from app.content.paladin_devotion_2014_runtime import build_aurelia_brightshield_2014
from app.domain.encounters import EncounterCombatant


def _hag():
    try:
        return next(row for row in load_monster_source_2014() if row.id == "sea-hag")
    except Exception:
        raise AssertionError("Missing pinned 2014 Sea Hag") from None


def _members():
    try:
        source = next(row for row in load_monster_source_2014() if row.id == "commoner")
        actor_template = compile_combatant(adapt_basic_monster_2014(source))
        target_template = build_aurelia_brightshield_2014(1).model_copy(update={"max_hp": 60})
        actor = EncounterCombatant(combatant_id="source", side="monsters", position_ft=5,
                                   state=build_combatant_state(actor_template))
        target = EncounterCombatant(combatant_id="hero", side="heroes", position_ft=10,
                                    state=build_combatant_state(target_template))
        action = _compile_save(source_proven_conditioned_saves_2014(_hag())[0])
        return actor, target, action
    except Exception:
        raise


def test_pinned_death_glare_compiles_card_owned_facts_without_admitting_illusion():
    try:
        source = _hag()
        before = source.model_dump_json()
        (definition,) = source_proven_conditioned_saves_2014(source)
        action = _compile_save(definition)
        assert (action.id, action.name, action.save_ability, action.dc, action.range_ft) == (
            "death-glare", "Death Glare", "wisdom", 11, 30
        )
        assert action.required_target_condition == "frightened"
        assert action.requires_target_sight and action.requires_target_to_see_source
        assert action.failure_sets_zero_hp and action.magical_effect
        assert source.model_dump_json() == before
        assert "source:extra-action" in basic_blockers_2014(source)
    except Exception:
        raise


@pytest.mark.parametrize("old,new", [
    ("one frightened creature", "one poisoned creature"),
    ("she can see", "she can hear"),
    ("If the target can see the hag", "If the target can hear the hag"),
    ("Wisdom saving throw", "Strength saving throw"),
    ("against this magic", "against this attack"),
    ("drop to 0 hit points", "take 2d6 damage"),
])
def test_changed_source_effect_or_eligibility_fails_closed(old, new):
    try:
        source = _hag()
        assert old in source.source_actions
        mutated = source.model_copy(update={"source_actions": source.source_actions.replace(old, new)})
        assert source_proven_conditioned_saves_2014(mutated) == []
    except Exception:
        raise


def test_source_range_dc_and_display_name_are_not_combat_dispatch():
    try:
        source = _hag()
        mutated = source.model_copy(update={
            "id": "renamed-monster", "name": "Unrelated Monster",
            "source_actions": source.source_actions.replace("within 30 feet", "within 50 feet")
                .replace("DC 11 Wisdom", "DC 19 Wisdom"),
        })
        (definition,) = source_proven_conditioned_saves_2014(mutated)
        action = _compile_save(definition)
        assert action.range_ft == 50 and action.dc == 19
        assert action.required_target_condition == "frightened"
    except Exception:
        raise


def test_frightened_sight_and_range_are_real_prerequisites():
    try:
        actor, target, action = _members()
        assert not legal_save_action(action, target, 5, actor=actor, source_id=actor.combatant_id)
        target.state.active_effect_ids.append("frightened")
        assert legal_save_action(action, target, 5, actor=actor, source_id=actor.combatant_id)
        assert not legal_save_action(action, target, 35, actor=actor)
        target.state.active_effect_ids.append("blinded")
        assert not legal_save_action(action, target, 5, actor=actor)
        target.state.active_effect_ids.remove("blinded")
        actor.state.active_effect_ids.append("blinded")
        assert not legal_save_action(action, target, 5, actor=actor)
        actor.state.active_effect_ids.remove("blinded")
        assert legal_save_action(action, target, 5, actor=actor)
    except Exception:
        raise


def test_failure_zeroes_hp_once_and_success_leaves_target_untouched():
    try:
        actor, target, action = _members()
        target.state.active_effect_ids.append("frightened")
        saved = action.model_copy(update={"dc": 1})
        outcome = resolve_save_action(1, 1, actor, target, saved, 5,
                                      FixedDiceProvider([20]), spend_action=False)
        assert outcome.save_succeeded and target.state.current_hp == 60
        failed = action.model_copy(update={"dc": 30})
        outcome = resolve_save_action(2, 1, actor, target, failed, 5,
                                      FixedDiceProvider([1]), spend_action=False)
        assert not outcome.save_succeeded
        assert target.state.current_hp == 0 and target.state.is_unconscious
        assert not target.state.is_dead and target.state.death_save_failures == 0
        assert "Death Glare" in outcome.description
    except Exception:
        raise


def test_fresh_fight_restores_original_target_state():
    try:
        actor, target, action = _members()
        target.state.active_effect_ids.append("frightened")
        assert legal_save_action(action, target, 5, actor=actor)
        reset = build_combatant_state(target.state.template)
        assert "frightened" not in reset.active_effect_ids
    except Exception:
        raise
