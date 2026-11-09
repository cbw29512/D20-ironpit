"""Save Grapple: source-owned size/capacity without losing save damage."""
from __future__ import annotations

import pytest
from pydantic import ValidationError

from app.combat.saving_throw_effects import apply_save_effects
from app.combat.state import build_combatant_state
from app.content.capability_compiler import _compile_save
from app.content.demo import build_demo_fighter
from app.domain.capabilities import SaveCapabilityDefinition
from app.domain.capability_effects import DiceSpec, GrappleEffectDefinition
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.size import CreatureSize
from app.domain.weapons import DamageType

from scripts.browser_template_serializer import _save


def _member(name: str, side: str, size: CreatureSize) -> EncounterCombatant:
    template = build_demo_fighter().model_copy(update={"size": size, "name": name})
    return EncounterCombatant(
        combatant_id=name, side=side, position_ft=0,
        state=build_combatant_state(template),
    )


def _action():
    return _compile_save(SaveCapabilityDefinition(
        id="synthetic-shared-save", name="Generic Flood",
        save_ability="strength", dc=15, range_ft=0,
        damage=DiceSpec(count=2, size=8, bonus=4),
        damage_type=DamageType.BLUDGEONING,
        success_damage="none",
        grapple=GrappleEffectDefinition(
            escape_dc=14, max_target_size=CreatureSize.LARGE,
            restrains=True, max_active_grapples=2,
            large_target_slot_cost=2, prevents_breathing=True,
            size_only_applies_to_grapple=True,
        ),
    ))


def _battle(sizes: list[CreatureSize]):
    owner = _member("owner", "monsters", CreatureSize.LARGE)
    victims = [_member(f"victim-{i}", "heroes", size)
               for i, size in enumerate(sizes)]
    setup = EncounterSetup(
        heroes=victims, monsters=[owner], ruleset="2014",
        hero_total_levels=1, monster_total_cr="5",
    )
    return owner, victims, setup


def _fail(owner, victim, action, setup):
    return apply_save_effects(
        owner, victim, action, False, None, 1, setup=setup,
    )


def test_save_target_eligibility_is_not_grapple_size_eligibility():
    action = _action()
    assert action.target_max_size is None
    assert action.grapple_max_target_size == CreatureSize.LARGE
    assert action.grapple_max_active_grapples == 2
    assert action.grapple_large_target_slot_cost == 2
    assert action.grapple_prevents_breathing is True
    owner, [huge], setup = _battle([CreatureSize.HUGE])
    assert _fail(owner, huge, action, setup).applied_conditions == []
    assert huge.state.grapple_sources == []


def test_one_large_fills_two_source_slots_and_keeps_breathing_flag():
    owner, (large, medium), setup = _battle(
        [CreatureSize.LARGE, CreatureSize.MEDIUM],
    )
    action = _action()
    assert _fail(owner, large, action, setup).applied_conditions == [
        "grappled", "restrained",
    ]
    assert large.state.grapple_sources[0].prevents_breathing is True
    assert _fail(owner, medium, action, setup).applied_conditions == []
    assert medium.state.grapple_sources == []


def test_two_medium_fill_capacity_and_existing_grapple_is_preserved():
    owner, (a, b, c), setup = _battle([CreatureSize.MEDIUM] * 3)
    action = _action()
    assert _fail(owner, a, action, setup).applied_conditions
    assert _fail(owner, b, action, setup).applied_conditions
    assert _fail(owner, c, action, setup).applied_conditions == []
    prior = a.state.grapple_sources[0]
    assert _fail(owner, a, action, setup).applied_conditions == []
    assert a.state.grapple_sources[0] is prior


def test_source_capacity_requires_setup_and_complete_schema():
    owner, (victim,), _ = _battle([CreatureSize.MEDIUM])
    with pytest.raises(ValueError, match="encounter setup"):
        _fail(owner, victim, _action(), None)
    with pytest.raises(ValidationError, match="total capacity"):
        GrappleEffectDefinition(escape_dc=14, large_target_slot_cost=2)


def test_legacy_save_size_and_browser_json_remain_unchanged():
    # Existing Constrict/held-target saves limit ALL save targets by size.
    # New Whelm-like cards must opt into grapple-only size gating.
    legacy = _compile_save(SaveCapabilityDefinition(
        id="old-constrict", name="Constrict", save_ability="strength",
        dc=12, range_ft=5, grapple=GrappleEffectDefinition(
            escape_dc=12, max_target_size=CreatureSize.MEDIUM,
        ),
    ))
    assert legacy.target_max_size == CreatureSize.MEDIUM
    assert legacy.grapple_max_target_size is None
    browser = _save(legacy)
    assert browser["targetMaxSize"] == "medium"
    assert "grappleMaxTargetSize" not in browser
