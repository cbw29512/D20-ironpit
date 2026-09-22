from __future__ import annotations

from app.combat.dice import FixedDiceProvider
from app.combat.state import build_combatant_state
from app.combat.targeting_wards import check_targeting_ward
from app.content.certified_heroes import build_certified_hero_entries_for_ruleset
from app.content.fighter_champion_2014_runtime import build_karnok_stoneward_2014
from app.content.monk_open_hand_2014_combat_profile import build_kael_2014_combat_profile
from app.content.monk_open_hand_2014_profile import build_kael_stillwater_2014_profile
from app.content.monk_open_hand_2014_runtime import build_kael_stillwater_2014
from app.domain.encounters import EncounterCombatant


def _member(template, combatant_id: str, side: str) -> EncounterCombatant:
    return EncounterCombatant(
        combatant_id=combatant_id,
        side=side,
        position_ft=0 if side == "heroes" else 5,
        state=build_combatant_state(template),
    )


def test_level11_tranquility_reuses_opening_targeting_gate() -> None:
    monk = _member(build_kael_stillwater_2014(11), "kael11", "heroes")
    attacker = _member(build_karnok_stoneward_2014(8), "attacker", "monsters")

    assert monk.state.template.weapon_attack.weapon.dice_size == 8
    assert next(item for item in monk.state.resources if item.id == "ki").max_uses == 11

    ward = monk.state.template.progression_features.opening_targeting_ward
    assert ward is not None
    assert (ward.source_id, ward.save_ability, ward.save_dc, ward.ends_on_owner_attack) == (
        "tranquility", "wisdom", 14, True,
    )
    assert [item.source_effect_id for item in monk.state.active_modifiers] == ["tranquility"]

    blocked = check_targeting_ward(attacker, monk, FixedDiceProvider([1]))
    assert blocked is not None
    assert blocked.succeeded is False
    assert blocked.gate.source_effect_id == "tranquility"

    # A hostile attack by the ward owner ends the same generic targeting gate.
    assert check_targeting_ward(monk, attacker, FixedDiceProvider([20])) is None
    assert monk.state.active_modifiers == []


def test_levels12_and13_are_incremental_2014_monk_progression() -> None:
    level11 = build_kael_stillwater_2014(11)
    level12 = build_kael_stillwater_2014(12)
    level13 = build_kael_stillwater_2014(13)

    assert level12.ability_scores is not None
    assert level13.ability_scores is not None
    assert level12.ability_scores.wisdom == 17
    assert level13.ability_scores.wisdom == 17
    assert level12.armor_class == 18
    assert level13.armor_class == 18
    assert level12.max_hp == level11.max_hp + 7
    assert level13.max_hp == level12.max_hp + 7
    assert next(item for item in level13.resources if item.id == "ki").max_uses == 13
    assert level13.progression_features.opening_targeting_ward is not None
    assert level13.progression_features.opening_targeting_ward.save_dc == 16

    profile12 = build_kael_stillwater_2014_profile(12)
    profile13 = build_kael_stillwater_2014_profile(13)
    assert profile12.final_ability_scores.wisdom == 17
    assert any(item.feature_id == "ability-score-improvement-l12" for item in profile12.feature_audits)
    tongue = next(item for item in profile13.feature_audits if item.feature_id == "tongue-of-the-sun-and-moon")
    assert tongue.combat_relevant is False
    assert tongue.automated is False

    fingerprint = build_kael_2014_combat_profile(13)
    assert fingerprint.abilities.wisdom == 17
    assert fingerprint.attacks[0].dice_size == 8
    assert fingerprint.speed_ft == 50


def test_2014_monk_registry_now_reaches_level13() -> None:
    registry = {
        key: (template.name, template.id)
        for key, template in build_certified_hero_entries_for_ruleset("2014")
    }
    for level in range(1, 14):
        assert registry[("monk", level, "canonical-2014")] == (
            "Kael Stillwater",
            f"kael-stillwater-2014-l{level}",
        )
