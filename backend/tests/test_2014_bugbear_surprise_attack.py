"""2014 Bugbear: opening initiative damage is owned by printed attacks, not a duplicate rider."""
from __future__ import annotations

import pytest

from app.combat.attacks import resolve_attack
from app.combat.dice import FixedDiceProvider
from app.combat.range import attack_range_disadvantage_sources
from app.combat.state import build_combatant_state
from app.content.capability_compiler import compile_combatant
from app.content.monster_basic_candidates_2014 import basic_blockers_2014, unsupported_traits_2014
from app.content.monster_definition_adapter_2014 import adapt_basic_monster_2014
from app.content.monster_opening_initiative_2014 import opening_initiative_damage_source_2014
from app.content.monster_source_2014 import load_monster_source_2014
from app.content.monsters import build_commoner
from app.domain.weapons_base import DamageType


def _source():
    return next(row for row in load_monster_source_2014() if row.id == "bugbear")


def _combatants():
    template = compile_combatant(adapt_basic_monster_2014(_source()))
    attacker = build_combatant_state(template)
    attacker.turns_started = 1
    victim = build_combatant_state(build_commoner().model_copy(update={"max_hp": 100}))
    return attacker, victim, template.weapon_attack


def _swing(attacker, victim, attack, values, round_number=1):
    return resolve_attack(
        1, round_number, attacker, victim, attack, 5,
        FixedDiceProvider(values), spend_action=False,
        turn_key=f"{round_number}:bugbear",
    )


def test_source_and_modes_are_pinned_and_source_cards_immutable():
    source = _source()
    before = source.model_dump_json()
    assert opening_initiative_damage_source_2014(source) == "Surprise Attack"
    assert "Surprise Attack" not in unsupported_traits_2014(source)
    assert basic_blockers_2014(source) == ()
    template = compile_combatant(adapt_basic_monster_2014(source))
    attacks = [template.weapon_attack, *template.alternate_weapon_attacks]
    assert len(attacks) == 3
    assert all(row.attack_bonus == 4 for row in attacks)
    morningstar = next(row for row in attacks if row.id.endswith("morningstar"))
    melee = next(row for row in attacks if row.id.endswith("javelin-melee"))
    ranged = next(row for row in attacks if row.id.endswith("javelin-ranged"))
    assert (morningstar.weapon.dice_count, morningstar.weapon.dice_size,
            morningstar.damage_bonus, morningstar.weapon.reach_ft) == (2, 8, 2, 5)
    assert (melee.weapon.dice_count, melee.weapon.dice_size,
            melee.damage_bonus, melee.weapon.reach_ft) == (2, 6, 2, 5)
    assert (ranged.weapon.dice_count, ranged.weapon.dice_size,
            ranged.damage_bonus, ranged.weapon.normal_range_ft,
            ranged.weapon.long_range_ft) == (1, 6, 2, 30, 120)
    assert template.attack_action is None  # No printed 2014 Multiattack.
    for row in attacks:
        assert len(row.conditional_damage) == 1
        assert row.conditional_damage[0].trigger == "round1_initiative_lead"
        assert row.conditional_damage[0].source_name == "Surprise Attack"
    assert attack_range_disadvantage_sources(ranged.weapon, 35) == 1
    assert attack_range_disadvantage_sources(ranged.weapon, 5, True) == 1
    with pytest.raises(ValueError, match="beyond long range"):
        attack_range_disadvantage_sources(ranged.weapon, 125)
    assert source.model_dump_json() == before


def test_missing_printed_source_or_rider_fails_closed():
    source = _source()
    missing = source.model_copy(update={
        "source_traits": (source.source_traits or "").replace("(2d6)", "(4d10)")
    })
    with pytest.raises(ValueError, match="printed source proof"):
        opening_initiative_damage_source_2014(missing)
    attack = source.attacks[0].model_copy(update={"conditional_damage": []})
    mutated = source.model_copy(update={"attacks": [attack, *source.attacks[1:]]})
    with pytest.raises(ValueError, match="differs from source"):
        opening_initiative_damage_source_2014(mutated)


def test_first_hit_winning_initiative_uses_original_printed_2d6_once():
    attacker, victim, attack = _combatants()
    hit = _swing(attacker, victim, attack, [18, 2, 3, 4, 5])
    assert hit.hit
    components = {row.source: row for row in hit.damage_components}
    assert list(components) == ["Morningstar", "Surprise Attack"]
    assert components["Surprise Attack"].rolls == [4, 5]
    assert components["Surprise Attack"].damage_type == DamageType.PIERCING
    assert attacker.feature_use_counts["weapon_attack_attempts"] == 1
    assert not attacker.template.progression_features.advantage_against_unacted_targets


def test_first_miss_consumes_bonus_and_later_attack_cannot_reapply_it():
    attacker, victim, attack = _combatants()
    miss = _swing(attacker, victim, attack, [2])
    assert not miss.hit
    hit = _swing(attacker, victim, attack, [18, 2, 3])
    assert hit.hit
    assert all(row.source != "Surprise Attack" for row in hit.damage_components)
    assert attacker.feature_use_counts["weapon_attack_attempts"] == 2


@pytest.mark.parametrize("own_turn,target_turn", [(1, 1), (2, 0)])
def test_losing_initiative_or_missing_own_first_turn_disables_bonus(own_turn, target_turn):
    attacker, victim, attack = _combatants()
    attacker.turns_started, victim.turns_started = own_turn, target_turn
    hit = _swing(attacker, victim, attack, [18, 2, 3])
    assert hit.hit
    assert all(row.source != "Surprise Attack" for row in hit.damage_components)


def test_critical_doubles_printed_rider_and_fresh_fight_resets():
    attacker, victim, attack = _combatants()
    event = _swing(attacker, victim, attack, [20, 2, 3, 4, 5, 1, 2, 3, 4])
    assert event.critical
    surprise = next(row for row in event.damage_components if row.source == "Surprise Attack")
    assert surprise.rolls == [1, 2, 3, 4]
    fresh, fresh_victim, fresh_attack = _combatants()
    assert fresh.feature_use_counts == {}
    new_event = _swing(fresh, fresh_victim, fresh_attack, [18, 2, 3, 4, 5])
    assert any(row.source == "Surprise Attack" for row in new_event.damage_components)
