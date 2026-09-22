from __future__ import annotations

from app.combat.dice import FixedDiceProvider
from app.combat.grapple import apply_grapple, resolve_escape_grapple
from app.combat.rogue_defenses import evasion_damage
from app.combat.state import begin_turn, build_combatant_state
from app.content.audited_rogue import build_mara_quickstep_level, unsupported_mara_rogue_features
from app.content.certified_heroes import build_certified_hero_registry
from app.content.rogue_combat_fingerprint import build_mara_quickstep_level7_combat_profile
from app.content.rogue_mid_progression_profile import build_mara_quickstep_level7_profile


def test_2024_rogue_level7_inherits_level6_and_adds_real_defensive_features() -> None:
    template = build_mara_quickstep_level(7)
    assert unsupported_mara_rogue_features(7) == ()
    assert template.id == "mara-quickstep-l7"
    assert (template.armor_class, template.max_hp, template.initiative_bonus) == (15, 59, 4)
    assert (template.weapon_attack.attack_bonus, template.weapon_attack.damage_bonus) == (7, 4)
    assert template.progression_features.sneak_attack_d6 == 4
    assert template.progression_features.cunning_strike_trip_die_cost == 1
    assert template.progression_features.uncanny_dodge is True
    assert template.progression_features.evasion is True
    rules = template.progression_features.skill_check_d20_minimums
    assert len(rules) == 1
    assert rules[0].source_id == "reliable-talent"
    assert rules[0].minimum_roll == 10
    assert {"athletics", "acrobatics"}.issubset(set(rules[0].skill_ids))


def test_reliable_talent_floors_proficient_grapple_escape_d20_at_ten() -> None:
    state = build_combatant_state(build_mara_quickstep_level(7))
    begin_turn(state)
    state.movement_remaining_ft = 0
    apply_grapple(state, "grappler", 15, 5, restrains=True)

    event = resolve_escape_grapple(1, 1, "mara", state, FixedDiceProvider([1]))

    assert event.check_ability == "dexterity (acrobatics)"
    assert event.ability_check_roll is not None
    assert event.ability_check_roll.selected_roll == 10
    assert event.ability_check_roll.total == 17
    assert event.ability_check_roll.revisions[-1].source_effect_id == "reliable-talent"
    assert event.check_succeeded is True
    assert state.grapple_sources == []


def test_level7_evasion_reuses_shared_damage_rule() -> None:
    state = build_combatant_state(build_mara_quickstep_level(7))
    assert evasion_damage(state, "dexterity", True, "half", 20) == 0
    assert evasion_damage(state, "dexterity", False, "half", 20) == 10


def test_2024_rogue_level7_profile_fingerprint_and_registry_match() -> None:
    profile = build_mara_quickstep_level7_profile()
    audits = {item.feature_id: item for item in profile.feature_audits}
    assert audits["evasion"].automated is True
    assert audits["reliable-talent"].combat_relevant is True
    assert audits["reliable-talent"].automated is True

    fingerprint = build_mara_quickstep_level7_combat_profile()
    assert (fingerprint.armor_class, fingerprint.max_hp, fingerprint.sneak_attack_d6) == (15, 59, 4)
    assert ("adrenaline-rush", 3) in fingerprint.resources

    registry = build_certified_hero_registry()
    assert registry[("rogue", 7, "canonical")] == ("Mara Quickstep", "mara-quickstep-l7")
