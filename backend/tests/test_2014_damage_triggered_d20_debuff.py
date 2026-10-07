from __future__ import annotations

import pytest

from app.combat.damage_triggered_d20 import expire_damage_triggered_d20_debuffs
from app.combat.exhaustion import (
    ability_check_disadvantage_sources,
    attack_disadvantage_sources,
    saving_throw_disadvantage_sources,
)
from app.combat.state import build_combatant_state
from app.combat.zero_hp import apply_damage
from app.content.capability_compiler import compile_combatant
from app.content.monster_basic_candidates_2014 import basic_blockers_2014, unsupported_traits_2014
from app.content.monster_damage_triggered_d20_2014 import damage_triggered_d20_debuffs_2014
from app.content.monster_definition_adapter_2014 import adapt_basic_monster_2014
from app.content.monster_source_2014 import load_monster_source_2014
from app.domain.models import DamageRollComponent
from app.domain.weapons import DamageType


def _source(monster_id: str):
    return next(item for item in load_monster_source_2014() if item.id == monster_id)


def _state(monster_id: str):
    return build_combatant_state(compile_combatant(adapt_basic_monster_2014(_source(monster_id))))


def _component(damage_type: DamageType, amount: int) -> DamageRollComponent:
    return DamageRollComponent(
        source="Test Damage",
        notation=str(amount),
        rolls=[],
        modifier=0,
        damage_type=damage_type,
        total=amount,
        applied_total=amount,
    )


def _damage(state, damage_type: DamageType, amount: int = 5) -> None:
    apply_damage(
        state,
        amount,
        damage_types={damage_type},
        damage_components=[_component(damage_type, amount)],
    )


def test_fire_aversion_sources_bind_to_one_universal_rule() -> None:
    yeti = _source("yeti")
    flesh_golem = _source("flesh-golem")

    yeti_rule = damage_triggered_d20_debuffs_2014(yeti)
    golem_rule = damage_triggered_d20_debuffs_2014(flesh_golem)

    assert [(item.source_name, item.trigger_damage_type) for item in yeti_rule] == [
        ("Fear of Fire", DamageType.FIRE),
    ]
    assert [(item.source_name, item.trigger_damage_type) for item in golem_rule] == [
        ("Aversion of Fire", DamageType.FIRE),
    ]
    for rule in [*yeti_rule, *golem_rule]:
        assert rule.attack_roll_disadvantage is True
        assert rule.ability_check_disadvantage is True
        assert rule.duration_target_turns == 1

    assert unsupported_traits_2014(yeti) == ()
    assert basic_blockers_2014(yeti) == ()
    assert unsupported_traits_2014(flesh_golem) == ("Berserk",)


def test_fire_aversion_binding_fails_closed_when_printed_semantics_change() -> None:
    yeti = _source("yeti")
    assert yeti.source_traits is not None
    altered = yeti.model_copy(
        update={"source_traits": yeti.source_traits.replace("ability checks", "saving throws", 1)},
        deep=True,
    )
    with pytest.raises(ValueError, match="unsupported Fear of Fire wording"):
        damage_triggered_d20_debuffs_2014(altered)


def test_fire_damage_immediately_disadvantages_attacks_and_checks_but_not_saves() -> None:
    state = _state("yeti")
    _damage(state, DamageType.FIRE)

    assert [item.source_name for item in state.active_damage_triggered_d20_debuffs] == ["Fear of Fire"]
    assert attack_disadvantage_sources(state) == 1
    assert ability_check_disadvantage_sources(state, "strength") == 1
    assert saving_throw_disadvantage_sources(state) == 0

    other = _state("yeti")
    _damage(other, DamageType.COLD)
    assert other.active_damage_triggered_d20_debuffs == []


def test_fire_before_next_turn_expires_at_that_turn_end() -> None:
    state = _state("yeti")
    assert state.turns_started_count == 0
    _damage(state, DamageType.FIRE)

    active = state.active_damage_triggered_d20_debuffs[0]
    assert active.expires_after_target_turn_count == 1

    state.turns_started_count = 1
    assert expire_damage_triggered_d20_debuffs(state) == ["Fear of Fire"]
    assert state.active_damage_triggered_d20_debuffs == []


def test_fire_during_own_turn_persists_through_following_turn() -> None:
    state = _state("yeti")
    state.turns_started_count = 1
    _damage(state, DamageType.FIRE)

    active = state.active_damage_triggered_d20_debuffs[0]
    assert active.expires_after_target_turn_count == 2

    assert expire_damage_triggered_d20_debuffs(state) == []
    assert attack_disadvantage_sources(state) == 1

    state.turns_started_count = 2
    assert expire_damage_triggered_d20_debuffs(state) == ["Fear of Fire"]
    assert attack_disadvantage_sources(state) == 0


def test_repeated_fire_refreshes_the_next_turn_expiry() -> None:
    state = _state("yeti")
    _damage(state, DamageType.FIRE)
    assert state.active_damage_triggered_d20_debuffs[0].expires_after_target_turn_count == 1

    state.turns_started_count = 1
    _damage(state, DamageType.FIRE)
    assert len(state.active_damage_triggered_d20_debuffs) == 1
    assert state.active_damage_triggered_d20_debuffs[0].expires_after_target_turn_count == 2
