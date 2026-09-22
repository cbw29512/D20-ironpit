from __future__ import annotations

from app.combat.cunning_strike import OBSCURE_FEATURE_ID, resolve_obscure
from app.combat.dice import FixedDiceProvider
from app.combat.sneak_attack import sneak_attack_bonus_damage
from app.combat.state import build_combatant_state
from app.content.audited_rogue import build_mara_quickstep_level, unsupported_mara_rogue_features
from app.content.certified_heroes import build_certified_hero_registry
from app.content.fighter_progression import build_karnok_stoneward_level
from app.content.rogue_combat_fingerprint import build_mara_quickstep_level14_combat_profile
from app.content.rogue_endgame_progression_profile import build_mara_quickstep_level14_profile
from app.domain.models import RollMode


def test_2024_rogue_level14_inherits_level13_and_adds_devious_strikes() -> None:
    level13 = build_mara_quickstep_level(13)
    template = build_mara_quickstep_level(14)

    assert unsupported_mara_rogue_features(14) == ()
    assert template.id == "mara-quickstep-l14"
    assert template.level == 14
    assert template.ability_scores is not None
    assert (template.ability_scores.dexterity, template.ability_scores.constitution) == (20, 20)
    assert (template.armor_class, template.max_hp, template.initiative_bonus) == (16, 143, 5)
    assert template.max_hp - level13.max_hp == 10
    assert (template.weapon_attack.attack_bonus, template.weapon_attack.damage_bonus) == (10, 5)
    assert template.saving_throw_bonuses["dexterity"] == 10
    assert template.saving_throw_bonuses["constitution"] == 5
    assert template.skill_bonuses == {"athletics": 6, "acrobatics": 10}
    assert template.progression_features.sneak_attack_d6 == 7
    assert template.progression_features.cunning_strike_max_effects == 2
    assert template.progression_features.cunning_strike_obscure_die_cost == 3
    assert template.progression_features.uncanny_dodge is True
    assert template.progression_features.evasion is True
    assert "Rogue 14" in template.source


def test_devious_strike_obscure_trades_three_dice_and_applies_timed_blinded() -> None:
    attacker = build_combatant_state(build_mara_quickstep_level(14))
    defender = build_combatant_state(build_karnok_stoneward_level(14))
    turn_key = "14:mara"

    spec = sneak_attack_bonus_damage(
        attacker, attacker.template.weapon_attack, RollMode.ADVANTAGE,
        turn_key, False, defender,
    )
    assert spec is not None
    assert spec[1] == 4
    assert attacker.feature_last_turn_keys[OBSCURE_FEATURE_ID] == turn_key

    result = resolve_obscure(attacker, defender, FixedDiceProvider([1]), turn_key)
    assert result.save_dc == 18
    assert result.save_succeeded is False
    assert result.applied is True
    assert "blinded" in defender.active_effect_ids
    effect = next(item for item in defender.timed_effects if item.source_effect_id == OBSCURE_FEATURE_ID)
    assert effect.effect_id == "blinded"
    assert effect.expiry_timing == "target_turn_end"


def test_2024_rogue_level14_profile_fingerprint_and_registry_match() -> None:
    profile = build_mara_quickstep_level14_profile()
    audits = {item.feature_id: item for item in profile.feature_audits}
    assert profile.level == 14
    assert audits["devious-strikes"].combat_relevant is True
    assert audits["devious-strikes"].automated is True
    assert "Obscure" in (audits["devious-strikes"].notes or "")

    fingerprint = build_mara_quickstep_level14_combat_profile()
    assert (fingerprint.armor_class, fingerprint.max_hp, fingerprint.sneak_attack_d6) == (16, 143, 7)
    assert ("adrenaline-rush", 5) in fingerprint.resources

    registry = build_certified_hero_registry()
    assert registry[("rogue", 14, "canonical")] == ("Mara Quickstep", "mara-quickstep-l14")
