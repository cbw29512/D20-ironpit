from __future__ import annotations

from app.combat.cunning_strike import FEATURE_ID as CUNNING_TRIP_ID, resolve_trip
from app.combat.dice import FixedDiceProvider
from app.combat.sneak_attack import sneak_attack_bonus_damage
from app.combat.state import build_combatant_state
from app.content.audited_rogue import build_mara_quickstep_level, unsupported_mara_rogue_features
from app.content.certified_heroes import build_certified_hero_registry
from app.content.fighter_progression import build_karnok_stoneward_level
from app.content.rogue_combat_fingerprint import build_mara_quickstep_level5_combat_profile
from app.content.rogue_progression_profile import build_mara_quickstep_level5_profile
from app.domain.models import RollMode


def test_2024_rogue_level5_inherits_level4_and_applies_only_level5_delta() -> None:
    """Level 5 must be the level-4 Mara plus only the researched Rogue-5 delta."""
    template = build_mara_quickstep_level(5)
    assert unsupported_mara_rogue_features(5) == ()
    assert template.id == "mara-quickstep-l5"
    assert template.level == 5
    assert template.ability_scores is not None
    assert (template.ability_scores.dexterity, template.ability_scores.constitution) == (18, 16)
    assert (template.armor_class, template.max_hp, template.initiative_bonus) == (15, 43, 4)
    assert (template.weapon_attack.attack_bonus, template.weapon_attack.damage_bonus) == (7, 4)
    assert template.saving_throw_bonuses["dexterity"] == 7
    assert template.skill_bonuses == {"athletics": 4, "acrobatics": 7}
    assert template.progression_features.sneak_attack_d6 == 3
    assert template.progression_features.cunning_strike_trip_die_cost == 1
    assert template.progression_features.uncanny_dodge is True
    assert {item.id: item.max_uses for item in template.resources}["adrenaline-rush"] == 3


def test_cunning_strike_trip_trades_one_sneak_die_before_roll_and_uses_dex_save() -> None:
    attacker = build_combatant_state(build_mara_quickstep_level(5))
    defender = build_combatant_state(build_karnok_stoneward_level(5))
    spec = sneak_attack_bonus_damage(
        attacker,
        attacker.template.weapon_attack,
        RollMode.ADVANTAGE,
        "1:mara",
        False,
        defender,
    )
    assert spec is not None
    assert spec[1] == 2
    assert attacker.feature_last_turn_keys[CUNNING_TRIP_ID] == "1:mara"

    result = resolve_trip(attacker, defender, FixedDiceProvider([1]), "1:mara")
    assert result.save_dc == 15
    assert result.save_succeeded is False
    assert result.applied is True
    assert "prone" in defender.active_effect_ids


def test_2024_rogue_level5_profile_fingerprint_and_registry_match() -> None:
    profile = build_mara_quickstep_level5_profile()
    audits = {item.feature_id: item for item in profile.feature_audits}
    assert profile.level == 5
    assert audits["cunning-strike"].automated is True
    assert audits["uncanny-dodge"].automated is True

    fingerprint = build_mara_quickstep_level5_combat_profile()
    assert (fingerprint.armor_class, fingerprint.max_hp, fingerprint.sneak_attack_d6) == (15, 43, 3)
    assert ("adrenaline-rush", 3) in fingerprint.resources

    registry = build_certified_hero_registry()
    assert registry[("rogue", 5, "canonical")] == ("Mara Quickstep", "mara-quickstep-l5")
