"""Synthetic source-neutral target-selected saving throw regressions."""
from __future__ import annotations

import pytest
from pydantic import ValidationError

from app.combat.state import build_combatant_state
from app.combat.target_chosen_save import choose_save_ability
from app.content.demo import build_demo_fighter
from app.content.capability_compiler import _compile_save
from app.domain.capability_attacks import SaveCapabilityDefinition


def _target():
    # A manufactured template tests the engine rather than a named monster.
    template = build_demo_fighter()
    bonuses = dict(template.saving_throw_bonuses)
    bonuses.update(strength=2, dexterity=4)
    template = template.model_copy(update={"saving_throw_bonuses": bonuses})
    return build_combatant_state(template)


def test_chooses_best_live_save_before_rolling() -> None:
    target = _target()
    options = ["strength", "dexterity"]
    assert choose_save_ability(target, options, 16) == "dexterity"

    # A higher Dexterity bonus loses to an unrestricted Strength roll if
    # Restrained imposes Disadvantage on the Dexterity save.
    target.active_effect_ids.append("restrained")
    assert choose_save_ability(target, options, 16) == "strength"
    target.active_effect_ids.remove("restrained")

    # All score changes are fight-state only; the source card stays immutable.
    original = target.template.ability_scores.score("dexterity")
    target.ability_score_reductions["dexterity"] = 10
    assert choose_save_ability(target, options, 16) == "strength"
    assert target.template.ability_scores.score("dexterity") == original


def test_save_choices_compile_and_fail_closed_on_bad_cards() -> None:
    definition = SaveCapabilityDefinition(
        id="renamed-source", name="Custom Landing Shock",
        save_ability="strength", save_ability_choices=["strength", "dexterity"],
        dc=16, range_ft=15,
    )
    compiled = _compile_save(definition)
    assert compiled.save_ability_choices == ["strength", "dexterity"]
    assert compiled.name == "Custom Landing Shock"
    with pytest.raises(ValidationError, match="distinct"):
        SaveCapabilityDefinition(
            id="wrong", name="Unknown Source", save_ability="strength",
            save_ability_choices=["strength", "strength"], dc=16, range_ft=15,
        )
    with pytest.raises(ValueError, match="distinct"):
        choose_save_ability(_target(), ["strength", "strength"], 16)
