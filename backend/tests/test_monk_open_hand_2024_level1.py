from __future__ import annotations

from app.combat.bonus_attacks import resolve_bonus_attack_grant
from app.combat.dice import FixedDiceProvider
from app.combat.monk_bonus_attacks_2014 import resolve_monk_bonus_attacks
from app.combat.state import build_combatant_state
from app.content.fighter_progression import build_karnok_stoneward_level
from app.content.monk_open_hand_2014_runtime import build_kael_stillwater_2014
from app.content.monk_open_hand_2024_profile import build_kael_stillwater_2024_profile
from app.content.monk_open_hand_2024_runtime import build_kael_stillwater_2024
from app.domain.encounters import EncounterCombatant, EncounterSetup


def _member(template, combatant_id: str, side: str, position: int) -> EncounterCombatant:
    return EncounterCombatant(
        combatant_id=combatant_id,
        side=side,
        position_ft=position,
        state=build_combatant_state(template),
    )


def test_2024_monk_level_one_profile_and_runtime_are_raw_aligned() -> None:
    profile = build_kael_stillwater_2024_profile()
    monk = build_kael_stillwater_2024()

    assert profile.ruleset == monk.ruleset == "2024"
    assert profile.species_id == "human"
    assert profile.background_id == "criminal"
    assert profile.origin_feat_id == "alert"
    assert {"resourceful", "skillful", "versatile", "skilled"}.issubset(
        {item.feature_id for item in profile.feature_audits}
    )
    assert profile.base_ability_scores.model_dump() == {
        "strength": 13, "dexterity": 15, "constitution": 14,
        "intelligence": 10, "wisdom": 10, "charisma": 10,
    }
    assert monk.ability_scores.model_dump() == {
        "strength": 13, "dexterity": 17, "constitution": 15,
        "intelligence": 10, "wisdom": 10, "charisma": 10,
    }
    assert monk.max_hp == 10
    assert monk.armor_class == 13
    assert monk.initiative_bonus == 5
    assert monk.starts_with_heroic_inspiration is True
    assert build_combatant_state(monk).heroic_inspiration is True
    assert monk.saving_throw_bonuses["strength"] == 3
    assert monk.saving_throw_bonuses["dexterity"] == 5
    assert monk.weapon_attack.weapon.id == "unarmed-strike"
    assert monk.weapon_attack.weapon.dice_size == 6
    assert monk.weapon_attack.attack_bonus == 5
    assert monk.weapon_attack.damage_bonus == 3
    assert monk.resources == []
    assert len(monk.bonus_attack_grants) == 1
    assert monk.bonus_attack_grants[0].id == "martial-arts"
    assert monk.bonus_attack_grants[0].attack_ids == ["kael-2024-unarmed"]
    assert monk.bonus_attack_grants[0].resource_id is None


def test_2024_martial_arts_bonus_unarmed_strike_has_no_attack_action_prerequisite() -> None:
    monk = _member(build_kael_stillwater_2024(), "monk", "heroes", 0)
    target_template = build_karnok_stoneward_level(1).model_copy(update={"armor_class": 1})
    target = _member(target_template, "target", "monsters", 5)
    setup = EncounterSetup(
        heroes=[monk],
        monsters=[target],
        hero_total_levels=1,
        monster_total_cr="1",
        ruleset="2024",
    )

    events, sequence = resolve_bonus_attack_grant(
        1,
        1,
        monk,
        setup,
        FixedDiceProvider([10, 4]),
        "1:monk",
    )

    assert sequence == 2
    assert len(events) == 1
    assert events[0].event_type == "attack"
    assert events[0].feature_id == "martial-arts"
    assert events[0].weapon_id == "unarmed-strike"
    assert monk.state.bonus_action_available is False
    assert monk.state.action_available is True


def test_generic_bonus_attack_grant_does_not_replace_2014_monk_prerequisite_logic() -> None:
    monk = _member(build_kael_stillwater_2014(1), "legacy-monk", "heroes", 0)
    target = _member(
        build_karnok_stoneward_level(1).model_copy(update={"armor_class": 1}),
        "target",
        "monsters",
        5,
    )
    setup = EncounterSetup(
        heroes=[monk],
        monsters=[target],
        hero_total_levels=1,
        monster_total_cr="1",
        ruleset="2014",
    )

    generic_events, generic_sequence = resolve_bonus_attack_grant(
        1, 1, monk, setup, FixedDiceProvider([10, 4]), "1:legacy-monk",
    )
    legacy_events, legacy_sequence = resolve_monk_bonus_attacks(
        1, 1, monk, setup, FixedDiceProvider([10, 4]), "1:legacy-monk", [],
    )

    assert generic_events == []
    assert generic_sequence == 1
    assert legacy_events == []
    assert legacy_sequence == 1
    assert monk.state.bonus_action_available is True
