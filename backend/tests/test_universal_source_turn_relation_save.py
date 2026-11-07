"""A source-held victim gets owner-turn damage only while its grapple is active."""
from __future__ import annotations

import pytest
from pydantic import ValidationError

from app.combat.dice import FixedDiceProvider
from app.combat.grapple import apply_grapple, release_grapple
from app.combat.source_turn_relation_damage import resolve_source_turn_relation_damage
from app.combat.state import build_combatant_state
from app.content.demo import build_demo_fighter
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.source_turn_relation_damage import SourceTurnRelationDamage
from app.domain.weapons_base import DamageType


def _setup():
    # Source name is intentionally synthetic: mechanics must not dispatch on labels.
    rule = SourceTurnRelationDamage(
        source_name="Renamed Engulf", target_relation="creatures_grappled_by_source",
        dice_count=2, dice_size=8, damage_bonus=4,
        damage_type=DamageType.BLUDGEONING,
        save_ability="constitution", save_dc=14,
    )
    hero = build_demo_fighter().model_copy(update={"max_hp": 60})
    owner_template = hero.model_copy(update={"source_turn_relation_damages": [rule]})
    owner = EncounterCombatant(
        combatant_id="holder", side="monsters", position_ft=0,
        state=build_combatant_state(owner_template),
    )
    target = EncounterCombatant(
        combatant_id="held", side="heroes", position_ft=5,
        state=build_combatant_state(hero),
    )
    setup = EncounterSetup(
        heroes=[target], monsters=[owner], hero_total_levels=1,
        monster_total_cr="1", ruleset="2014",
    )
    return rule, owner, target, setup


def test_save_prevents_damage_and_failure_applies_bonus(monkeypatch):
    import app.combat.source_turn_relation_damage as runtime

    rule, owner, target, setup = _setup()
    original = runtime.apply_damage
    calls = []

    def spy(*args, **kwargs):
        calls.append(1)
        return original(*args, **kwargs)

    monkeypatch.setattr(runtime, "apply_damage", spy)
    assert resolve_source_turn_relation_damage(
        1, 1, owner, setup, FixedDiceProvider([1])
    ) == ([], 1)

    apply_grapple(target.state, owner.combatant_id, 14, 10, restrains=True)
    hp = target.state.current_hp
    events, sequence = resolve_source_turn_relation_damage(
        1, 1, owner, setup, FixedDiceProvider([20]),
    )
    assert sequence == 2 and len(events) == 1
    assert events[0].save_succeeded is True
    assert events[0].damage_components == []
    assert target.state.current_hp == hp and calls == []

    events, sequence = resolve_source_turn_relation_damage(
        2, 2, owner, setup, FixedDiceProvider([1, 8, 8]),
    )
    assert sequence == 3 and events[0].save_succeeded is False
    assert events[0].feature_id == rule.source_name
    assert target.state.current_hp == hp - 20
    assert len(calls) == 1

    release_grapple(target.state, owner.combatant_id)
    assert resolve_source_turn_relation_damage(
        3, 3, owner, setup, FixedDiceProvider([1]),
    ) == ([], 3)


def test_reverse_relation_and_incomplete_save_rejected():
    rule, owner, target, setup = _setup()
    apply_grapple(owner.state, target.combatant_id, 14, 10, restrains=True)
    # Reverse ownership must never trigger a held-target damage profile.
    assert resolve_source_turn_relation_damage(
        1, 1, owner, setup, FixedDiceProvider([1]),
    ) == ([], 1)
    data = rule.model_dump()
    data.pop("save_dc")
    with pytest.raises(ValidationError):
        SourceTurnRelationDamage.model_validate(data)
