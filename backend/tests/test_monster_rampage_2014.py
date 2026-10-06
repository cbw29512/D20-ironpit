from __future__ import annotations

import pytest

from app.combat.bonus_attacks import resolve_bonus_attack_grant
from app.combat.damage_reaction_wrappers import resolve_attack_event_chain
from app.combat.dice import FixedDiceProvider
from app.combat.state import build_combatant_state
from app.content.capability_compiler import compile_combatant
from app.content.demo import build_demo_fighter
from app.content.monster_basic_candidates_2014 import unsupported_traits_2014
from app.content.monster_definition_adapter_2014 import adapt_basic_monster_2014
from app.content.monster_source_2014 import load_monster_source_2014
from app.domain.encounters import EncounterCombatant, EncounterSetup


def _source(name: str):
    return next(item for item in load_monster_source_2014() if item.name == name)


def _member(template, combatant_id: str, side: str, position: int) -> EncounterCombatant:
    return EncounterCombatant(
        combatant_id=combatant_id,
        side=side,
        position_ft=position,
        state=build_combatant_state(template),
    )


@pytest.mark.parametrize("name", ["Giant Hyena", "Gnoll"])
def test_rampage_binds_to_one_triggered_bonus_action_bite(name: str) -> None:
    source = _source(name)
    assert "Rampage" not in unsupported_traits_2014(source)

    template = compile_combatant(adapt_basic_monster_2014(source))
    assert len(template.bonus_attack_grants) == 1
    grant = template.bonus_attack_grants[0]
    assert grant.name == "Rampage"
    assert grant.trigger == "source_melee_zero_hp_this_turn"
    assert grant.attack_count == 1
    assert len(grant.attack_ids) == 1
    bite = next(
        attack
        for attack in [template.weapon_attack, *template.alternate_weapon_attacks]
        if attack.id == grant.attack_ids[0]
    )
    assert bite.weapon.name == "Bite"
    assert bite.weapon.attack_kind.value == "melee"


def test_rampage_requires_own_turn_melee_zero_hp_transition_and_spends_bonus_action() -> None:
    source = _source("Gnoll")
    attacker = _member(
        compile_combatant(adapt_basic_monster_2014(source)),
        "gnoll",
        "monsters",
        5,
    )
    victim_template = build_demo_fighter().model_copy(update={"armor_class": 1})
    victim = _member(victim_template, "victim", "heroes", 0)
    next_target = _member(victim_template, "next-target", "heroes", 0)
    victim.state.current_hp = 1
    setup = EncounterSetup(
        heroes=[victim, next_target],
        monsters=[attacker],
        hero_total_levels=2,
        monster_total_cr=source.challenge_rating,
        ruleset="2014",
    )
    melee = next(
        attack
        for attack in [attacker.state.template.weapon_attack, *attacker.state.template.alternate_weapon_attacks]
        if attack.weapon.attack_kind.value == "melee"
    )

    pre_events, sequence = resolve_attack_event_chain(
        1, 1, attacker, victim, melee, 5,
        FixedDiceProvider([19, *([1] * max(1, melee.weapon.dice_count))]),
        setup,
        spend_action=False,
        turn_key="1:gnoll",
    )
    assert pre_events[0].hp_before == 1
    assert pre_events[0].hp_after == 0
    grant = attacker.state.template.bonus_attack_grants[0]
    assert attacker.state.feature_last_turn_keys[f"bonus-attack-trigger:{grant.id}"] == "1:gnoll"

    bite = next(
        attack
        for attack in [attacker.state.template.weapon_attack, *attacker.state.template.alternate_weapon_attacks]
        if attack.id == grant.attack_ids[0]
    )
    events, final_sequence = resolve_bonus_attack_grant(
        sequence, 1, attacker, setup,
        FixedDiceProvider([19, *([1] * max(1, bite.weapon.dice_count))]),
        "1:gnoll",
    )

    assert final_sequence == sequence + 1
    assert len(events) == 1
    assert events[0].feature_id == grant.id
    assert events[0].attack_name == "Bite"
    assert events[0].target_id == "next-target"
    assert attacker.state.bonus_action_available is False

    blocked_events, blocked_sequence = resolve_bonus_attack_grant(
        final_sequence, 1, attacker, setup, FixedDiceProvider([19, 1]), "1:gnoll",
    )
    assert blocked_events == []
    assert blocked_sequence == final_sequence


def test_rampage_does_not_fire_without_qualifying_trigger() -> None:
    source = _source("Giant Hyena")
    attacker = _member(
        compile_combatant(adapt_basic_monster_2014(source)),
        "hyena",
        "monsters",
        5,
    )
    target = _member(build_demo_fighter().model_copy(update={"armor_class": 1}), "target", "heroes", 0)
    setup = EncounterSetup(
        heroes=[target],
        monsters=[attacker],
        hero_total_levels=1,
        monster_total_cr=source.challenge_rating,
        ruleset="2014",
    )

    events, sequence = resolve_bonus_attack_grant(
        1, 1, attacker, setup, FixedDiceProvider([19, 1]), "1:hyena",
    )

    assert events == []
    assert sequence == 1
    assert attacker.state.bonus_action_available is True
