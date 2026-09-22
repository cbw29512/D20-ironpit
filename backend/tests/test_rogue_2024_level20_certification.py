from __future__ import annotations

from app.combat.attacks import resolve_attack
from app.combat.dice import FixedDiceProvider
from app.combat.saving_throw_rolls import resolve_saving_throw
from app.combat.state import build_combatant_state
from app.content.audited_rogue import build_mara_quickstep_level, unsupported_mara_rogue_features
from app.content.certified_heroes import build_certified_hero_registry
from app.content.fighter_progression import build_karnok_stoneward_level
from app.content.rogue_combat_fingerprint import build_mara_quickstep_level20_combat_profile
from app.content.rogue_final_progression_profile import build_mara_quickstep_level20_profile


def _resource(state, resource_id: str):
    return next(item for item in state.resources if item.id == resource_id)


def test_2024_rogue_level20_inherits_level19_and_adds_stroke_of_luck() -> None:
    level19 = build_mara_quickstep_level(19)
    template = build_mara_quickstep_level(20)

    assert unsupported_mara_rogue_features(20) == ()
    assert template.id == "mara-quickstep-l20"
    assert template.level == 20
    assert template.ability_scores is not None
    assert (
        template.ability_scores.strength,
        template.ability_scores.dexterity,
        template.ability_scores.constitution,
        template.ability_scores.wisdom,
    ) == (14, 20, 20, 12)
    assert (template.armor_class, template.max_hp, template.initiative_bonus) == (16, 203, 5)
    assert template.max_hp - level19.max_hp == 10
    assert (template.weapon_attack.attack_bonus, template.weapon_attack.damage_bonus) == (11, 5)
    assert template.progression_features.sneak_attack_d6 == 10
    assert template.progression_features.miss_to_hit_once_per_turn is True
    assert template.progression_features.failed_d20_to_natural_20_resource_id == "stroke-of-luck"
    resources = {item.id: item.max_uses for item in template.resources}
    assert resources["stroke-of-luck"] == 1
    assert resources["adrenaline-rush"] == 6
    assert "Rogue 20" in template.source


def test_level20_prefers_peerless_aim_before_spending_stroke_of_luck() -> None:
    attacker = build_combatant_state(build_mara_quickstep_level(20))
    defender = build_combatant_state(build_karnok_stoneward_level(18))

    event = resolve_attack(
        1, 1, attacker, defender, attacker.template.weapon_attack, 5,
        FixedDiceProvider([2, *([4] * 24)]),
        spend_action=False, turn_key="1:mara",
    )

    assert event.hit is True
    assert "miss-to-hit feature converts" in event.description
    assert "Stroke of Luck" not in event.description
    assert _resource(attacker, "stroke-of-luck").current_uses == 1


def test_level20_stroke_of_luck_turns_second_same_turn_miss_into_natural20_critical() -> None:
    attacker = build_combatant_state(build_mara_quickstep_level(20))
    defender = build_combatant_state(build_karnok_stoneward_level(18))

    resolve_attack(
        1, 1, attacker, defender, attacker.template.weapon_attack, 5,
        FixedDiceProvider([2, *([4] * 24)]),
        spend_action=False, turn_key="1:mara",
    )
    event = resolve_attack(
        2, 1, attacker, defender, attacker.template.weapon_attack, 5,
        FixedDiceProvider([2, *([4] * 40)]),
        spend_action=False, turn_key="1:mara",
    )

    assert event.hit is True
    assert event.critical is True
    assert event.attack_roll is not None
    assert event.attack_roll.selected_roll == 20
    assert event.turn_terminated is False
    assert "Stroke of Luck turns the failed d20 into a natural 20" in event.description
    assert _resource(attacker, "stroke-of-luck").current_uses == 0


def test_level20_stroke_of_luck_is_a_generic_failed_save_override() -> None:
    state = build_combatant_state(build_mara_quickstep_level(20))
    roll, succeeded = resolve_saving_throw(
        state, "wisdom", 25, FixedDiceProvider([1]),
    )

    assert succeeded is True
    assert roll is not None
    assert roll.selected_roll == 20
    assert roll.revisions[-1].source_effect_id == "stroke-of-luck"
    assert roll.revisions[-1].kind == "selected_result_override"
    assert roll.revisions[-1].original_rolls == [1]
    assert roll.revisions[-1].replacement_rolls == [1]
    assert _resource(state, "stroke-of-luck").current_uses == 0


def test_2024_rogue_level20_profile_fingerprint_and_registry_match() -> None:
    profile = build_mara_quickstep_level20_profile()
    audits = {item.feature_id: item for item in profile.feature_audits}
    assert profile.level == 20
    assert audits["stroke-of-luck"].combat_relevant is True
    assert audits["stroke-of-luck"].automated is True

    fingerprint = build_mara_quickstep_level20_combat_profile()
    assert (fingerprint.armor_class, fingerprint.max_hp, fingerprint.sneak_attack_d6) == (16, 203, 10)
    assert ("stroke-of-luck", 1) in fingerprint.resources

    registry = build_certified_hero_registry()
    assert registry[("rogue", 20, "canonical")] == ("Mara Quickstep", "mara-quickstep-l20")
