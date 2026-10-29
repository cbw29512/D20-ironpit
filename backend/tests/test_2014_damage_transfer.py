from __future__ import annotations

import pytest

from app.combat.state import build_combatant_state
from app.combat.zero_hp import apply_damage
from app.content.capability_compiler import compile_combatant
from app.content.monster_definition_adapter_2014 import adapt_monster_mechanics_2014
from app.content.monster_damage_transfer_2014 import damage_transfer_rule_2014
from app.content.monster_source_2014 import load_monster_source_2014
from app.content.monsters import build_commoner
from app.domain.actions import GrappleSource
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import DamageRollComponent, DamageType


def _source(card_id: str):
    return next(row for row in load_monster_source_2014() if row.id == card_id)


def _setup(card_id: str = "cloaker"):
    source = _source(card_id)
    template = compile_combatant(adapt_monster_mechanics_2014(source))
    owner = EncounterCombatant(
        combatant_id="owner", side="monsters", position_ft=0,
        state=build_combatant_state(template),
    )
    victim = EncounterCombatant(
        combatant_id="victim", side="heroes", position_ft=0,
        state=build_combatant_state(build_commoner().model_copy(update={"max_hp": 40})),
    )
    setup = EncounterSetup(
        heroes=[victim], monsters=[owner], hero_total_levels=1,
        monster_total_cr=source.challenge_rating, ruleset="2014",
    )
    return source, owner, victim, setup


def test_semantic_source_proof_binds_both_cards_and_preserves_source() -> None:
    for card_id in ("cloaker", "rug-of-smothering"):
        source = _source(card_id)
        before = source.model_dump_json()
        rule = damage_transfer_rule_2014(source)
        assert rule is not None
        assert rule.source_name == "Damage Transfer"
        assert rule.source_rounding == "down"
        assert rule.transferred_damage_retriggers is False
        template = compile_combatant(adapt_monster_mechanics_2014(source))
        assert template.damage_transfer == rule
        assert source.model_dump_json() == before

    renamed = _source("cloaker").model_copy(update={
        "trait_names": ["Shared Harm", "False Appearance", "Light Sensitivity"],
        "source_traits": (_source("cloaker").source_traits or "").replace(
            "Damage Transfer.", "Shared Harm.",
        ),
    })
    assert damage_transfer_rule_2014(renamed).source_name == "Shared Harm"


def test_changed_or_incomplete_printed_clause_fails_closed() -> None:
    source = _source("cloaker")
    changed = source.model_copy(update={
        "source_traits": (source.source_traits or "").replace(
            "takes the other half", "takes 3 damage",
        ),
    })
    with pytest.raises(ValueError, match="source proof"):
        damage_transfer_rule_2014(changed)


def test_active_relation_splits_odd_damage_and_fresh_fight_resets() -> None:
    _, owner, victim, setup = _setup()
    victim.state.grapple_sources.append(GrappleSource(source_id="owner", escape_dc=13))
    owner_before, victim_before = owner.state.current_hp, victim.state.current_hp
    apply_damage(owner.state, 9, setup=setup)
    assert owner.state.current_hp == owner_before - 4
    assert victim.state.current_hp == victim_before - 5

    _, fresh_owner, fresh_victim, fresh_setup = _setup()
    fresh_before = fresh_owner.state.current_hp
    apply_damage(fresh_owner.state, 9, setup=fresh_setup)
    assert fresh_owner.state.current_hp == fresh_before - 9
    assert fresh_victim.state.current_hp == fresh_victim.state.template.max_hp


def test_transferred_damage_does_not_chain() -> None:
    _, owner, victim, setup = _setup()
    third = EncounterCombatant(
        combatant_id="third", side="heroes", position_ft=0,
        state=build_combatant_state(build_commoner().model_copy(update={"max_hp": 40})),
    )
    setup.heroes.append(third)
    victim.state.template = owner.state.template.model_copy()
    victim.state.current_hp = 40
    victim.state.grapple_sources.append(GrappleSource(source_id="owner", escape_dc=13))
    third.state.grapple_sources.append(GrappleSource(source_id="victim", escape_dc=13))
    apply_damage(owner.state, 8, setup=setup)
    assert victim.state.current_hp == 36
    assert third.state.current_hp == 40


def test_split_preserves_typed_components_for_both_creatures() -> None:
    _, owner, victim, setup = _setup()
    victim.state.grapple_sources.append(GrappleSource(source_id="owner", escape_dc=13))
    components = [
        DamageRollComponent(
            source="first", notation="5", rolls=[], damage_type=DamageType.FIRE,
            total=5, applied_total=5,
        ),
        DamageRollComponent(
            source="second", notation="5", rolls=[], damage_type=DamageType.COLD,
            total=5, applied_total=5,
        ),
    ]
    apply_damage(
        owner.state, 10, setup=setup,
        damage_types={DamageType.FIRE, DamageType.COLD}, damage_components=components,
    )
    assert owner.state.damage_taken_this_turn_by_type == {"fire": 3, "cold": 2}
    assert victim.state.damage_taken_this_turn_by_type == {"fire": 2, "cold": 3}
    assert [item.applied_total for item in components] == [5, 5]


def test_active_rule_without_encounter_context_fails_closed() -> None:
    _, owner, _, _ = _setup()
    with pytest.raises(ValueError, match="encounter setup"):
        apply_damage(owner.state, 1)
