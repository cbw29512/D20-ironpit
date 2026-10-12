"""2014 Bugbear: one opening attack when its initiative precedes the target."""
from __future__ import annotations

import pytest

from app.combat.attacks import resolve_attack
from app.combat.dice import FixedDiceProvider
from app.combat.state import build_combatant_state
from app.content.monster_basic_candidates_2014 import basic_blockers_2014, unsupported_traits_2014
from app.content.monster_once_per_turn_traits_2014 import surprise_attack_rider_2014
from app.content.monster_source_2014 import load_monster_source_2014
from app.content.monster_trait_bindings_2014 import progression_features_2014
from app.content.monsters import build_commoner


def _source(monster_id: str):
    return next(monster for monster in load_monster_source_2014() if monster.id == monster_id)


def _combatants():
    attacker_template = build_commoner().model_copy(deep=True)
    attacker_template.progression_features = progression_features_2014(_source("bugbear"))
    attacker = build_combatant_state(attacker_template)
    attacker.turns_started = 1  # This creature won initiative over the still-unacted target.
    target_template = build_commoner().model_copy(update={"max_hp": 100})
    target = build_combatant_state(target_template)
    return attacker, target, attacker_template.weapon_attack


def _swing(attacker, target, attack, rolls, *, round_number=1):
    return resolve_attack(
        1, round_number, attacker, target, attack, 5, FixedDiceProvider(rolls),
        spend_action=False, turn_key=f"{round_number}:bugbear",
    )


def test_source_proof_binds_only_2014_bugbear_without_touching_its_card():
    source = _source("bugbear")
    before = source.model_dump_json()
    rider = surprise_attack_rider_2014(source)
    assert rider is not None
    assert (rider.source_name, rider.dice_count, rider.dice_size) == ("Surprise Attack", 2, 6)
    assert rider.requires_first_attack_of_fight and rider.requires_attacker_first_turn
    assert rider.requires_target_unacted
    assert "Surprise Attack" not in unsupported_traits_2014(source)
    assert "attack:complex" in basic_blockers_2014(source)  # Morningstar/Javelin still queued.
    assert surprise_attack_rider_2014(_source("doppelganger")) is None
    assert source.model_dump_json() == before


def test_missing_source_damage_fails_closed():
    source = _source("bugbear")
    mutated = source.model_copy(update={
        "source_traits": (source.source_traits or "").replace("(2d6)", "(4d10)")
    })
    with pytest.raises(ValueError, match="source damage is incomplete"):
        surprise_attack_rider_2014(mutated)


def test_first_hit_after_winning_initiative_adds_printed_dice():
    attacker, target, attack = _combatants()
    hit = _swing(attacker, target, attack, [18, 2, 3, 4])
    assert hit.hit
    rider = next(c for c in hit.damage_components if c.source == "Surprise Attack")
    assert rider.rolls == [3, 4]
    assert rider.damage_type == attack.weapon.damage_type
    assert attacker.feature_use_counts["weapon_attack_attempts"] == 1
    assert attacker.template.progression_features.advantage_against_unacted_targets is False
    assert attacker.template.progression_features.critical_hits_against_surprised_targets is False


def test_miss_spends_first_attempt_and_later_hit_has_no_bonus():
    attacker, target, attack = _combatants()
    miss = _swing(attacker, target, attack, [2])
    assert not miss.hit
    assert attacker.feature_use_counts["weapon_attack_attempts"] == 1
    hit = _swing(attacker, target, attack, [18, 2])
    assert hit.hit
    assert all(c.source != "Surprise Attack" for c in hit.damage_components)


@pytest.mark.parametrize("attacker_turn,target_turn", [(1, 1), (2, 0)])
def test_losing_initiative_or_missing_own_opening_turn_disables_bonus(attacker_turn, target_turn):
    attacker, target, attack = _combatants()
    attacker.turns_started = attacker_turn
    target.turns_started = target_turn
    hit = _swing(attacker, target, attack, [18, 2])
    assert hit.hit
    assert all(c.source != "Surprise Attack" for c in hit.damage_components)


def test_opening_critical_doubles_rider_dice_and_new_fight_resets_counter():
    attacker, target, attack = _combatants()
    critical = _swing(attacker, target, attack, [20, 2, 3, 4, 5, 6, 1])
    assert critical.critical
    bonus = next(c for c in critical.damage_components if c.source == "Surprise Attack")
    assert bonus.rolls == [4, 5, 6, 1]
    fresh, fresh_target, fresh_attack = _combatants()
    assert fresh.feature_use_counts == {}
    again = _swing(fresh, fresh_target, fresh_attack, [18, 2, 3, 4])
    assert any(c.source == "Surprise Attack" for c in again.damage_components)
