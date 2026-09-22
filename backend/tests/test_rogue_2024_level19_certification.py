from __future__ import annotations

from app.combat.dice import FixedDiceProvider
from app.combat.state import build_combatant_state
from app.combat.attacks import resolve_attack
from app.content.audited_rogue import build_mara_quickstep_level, unsupported_mara_rogue_features
from app.content.certified_heroes import build_certified_hero_registry
from app.content.fighter_progression import build_karnok_stoneward_level
from app.content.rogue_combat_fingerprint import build_mara_quickstep_level19_combat_profile
from app.content.rogue_final_progression_profile import build_mara_quickstep_level19_profile


def test_2024_rogue_level19_inherits_level18_and_adds_combat_prowess() -> None:
    level18 = build_mara_quickstep_level(18)
    template = build_mara_quickstep_level(19)

    assert unsupported_mara_rogue_features(19) == ()
    assert template.id == "mara-quickstep-l19"
    assert template.level == 19
    assert template.ability_scores is not None
    assert (
        template.ability_scores.strength,
        template.ability_scores.dexterity,
        template.ability_scores.constitution,
        template.ability_scores.wisdom,
    ) == (14, 20, 20, 12)
    assert (template.armor_class, template.max_hp, template.initiative_bonus) == (16, 193, 5)
    assert template.max_hp - level18.max_hp == 10
    assert (template.weapon_attack.attack_bonus, template.weapon_attack.damage_bonus) == (11, 5)
    assert template.saving_throw_bonuses == {
        "strength": 2, "dexterity": 11, "constitution": 5,
        "intelligence": 6, "wisdom": 7, "charisma": 6,
    }
    assert template.skill_bonuses == {"athletics": 8, "acrobatics": 11}
    assert template.progression_features.sneak_attack_d6 == 10
    assert template.progression_features.miss_to_hit_once_per_turn is True
    assert template.progression_features.attack_advantage_suppressed_unless_incapacitated is True
    assert {item.id: item.max_uses for item in template.resources}["adrenaline-rush"] == 6
    assert "Rogue 19" in template.source


def test_boon_of_combat_prowess_converts_one_miss_per_turn() -> None:
    attacker = build_combatant_state(build_mara_quickstep_level(19))
    defender = build_combatant_state(build_karnok_stoneward_level(18))

    first = resolve_attack(
        1, 1, attacker, defender, attacker.template.weapon_attack, 5,
        FixedDiceProvider([2, 4, 4, 4, 4, 4, 4, 4, 4, 4]),
        spend_action=False, turn_key="1:mara",
    )
    assert first.hit is True
    assert "miss-to-hit feature converts" in first.description

    second = resolve_attack(
        2, 1, attacker, defender, attacker.template.weapon_attack, 5,
        FixedDiceProvider([2]),
        spend_action=False, turn_key="1:mara",
    )
    assert second.hit is False


def test_2024_rogue_level19_profile_fingerprint_and_registry_match() -> None:
    profile = build_mara_quickstep_level19_profile()
    audits = {item.feature_id: item for item in profile.feature_audits}
    assert profile.level == 19
    assert profile.final_ability_scores.strength == 14
    assert audits["boon-combat-prowess"].combat_relevant is True
    assert audits["boon-combat-prowess"].automated is True

    fingerprint = build_mara_quickstep_level19_combat_profile()
    assert fingerprint.abilities.strength == 14
    assert (fingerprint.armor_class, fingerprint.max_hp, fingerprint.sneak_attack_d6) == (16, 193, 10)
    assert ("adrenaline-rush", 6) in fingerprint.resources

    registry = build_certified_hero_registry()
    assert registry[("rogue", 19, "canonical")] == ("Mara Quickstep", "mara-quickstep-l19")



def test_boon_of_combat_prowess_rescues_natural_one_before_turn_termination() -> None:
    attacker = build_combatant_state(build_mara_quickstep_level(19))
    defender = build_combatant_state(build_karnok_stoneward_level(18))

    event = resolve_attack(
        1, 1, attacker, defender, attacker.template.weapon_attack, 5,
        FixedDiceProvider([1, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4]),
        spend_action=False, turn_key="1:mara",
    )

    assert event.hit is True
    assert event.turn_terminated is False
    assert attacker.turn_terminated is False
    assert "miss-to-hit feature converts" in event.description
