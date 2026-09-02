from app.combat.attacks import resolve_attack
from app.combat.dice import FixedDiceProvider
from app.combat.indomitable import use_indomitable
from app.combat.saving_throw_rolls import resolve_saving_throw
from app.combat.state import build_combatant_state
from app.content.build_audit import assert_character_build_raw_ready, audit_character_build
from app.content.canonical_hero_policy import assert_canonical_profile_policy
from app.content.character_resource_audit import assert_character_resources_raw_ready
from app.content.certified_heroes import build_certified_hero_registry
from app.content.fighter_level9_combat_profile import build_karnok_stoneward_level9_combat_profile
from app.content.fighter_level9_profile import build_karnok_stoneward_level9_profile
from app.content.fighter_progression import build_karnok_stoneward_level
from app.content.pregen_combat_audit import assert_pregen_combat_stats, audit_pregen_combat_stats
from app.domain.models import RollMode


def _indomitable_uses(state) -> int:
    return next(item for item in state.resources if item.id == "indomitable").current_uses


def test_fighter_level_nine_snapshot_is_derived_from_level_eight() -> None:
    karnok = build_karnok_stoneward_level(9)
    greatsword = karnok.weapon_attack
    shortbow = karnok.alternate_weapon_attacks[0]
    resources = {item.id: item.max_uses for item in karnok.resources}

    assert (karnok.id, karnok.level, karnok.max_hp, karnok.armor_class, karnok.speed_ft) == (
        "karnok-stoneward-l9", 9, 94, 17, 30,
    )
    assert (greatsword.attack_bonus, greatsword.damage_bonus, greatsword.damage_die_minimum) == (9, 5, 3)
    assert (shortbow.attack_bonus, shortbow.damage_bonus) == (5, 1)
    assert karnok.saving_throw_bonuses["strength"] == 9
    assert karnok.saving_throw_bonuses["constitution"] == 8
    assert karnok.skill_bonuses["athletics"] == 9
    assert karnok.weapon_masteries == ["flail", "javelin", "spear", "greatsword"]
    assert resources == {
        "second-wind": 3, "action-surge": 1, "indomitable": 1,
        "adrenaline-rush": 4, "relentless-endurance": 1,
    }
    assert karnok.progression_features.indomitable_bonus == 9
    assert karnok.progression_features.tactical_master_sap_weapon_ids == ["greatsword"]
    assert karnok.attack_action is not None and len(karnok.attack_action.slots) == 2


def test_fighter_level_nine_candidate_passes_build_fingerprint_and_resource_gates_but_is_not_public_ready() -> None:
    template = build_karnok_stoneward_level(9)
    profile = build_karnok_stoneward_level9_profile()
    combat_profile = build_karnok_stoneward_level9_combat_profile()

    assert_canonical_profile_policy(profile)
    assert audit_character_build(profile, template) == []
    assert_character_build_raw_ready(profile, template)
    assert audit_pregen_combat_stats(template, combat_profile) == []
    assert_pregen_combat_stats(template, combat_profile)
    assert_character_resources_raw_ready(template, profile, combat_profile)
    assert ("fighter", 9, "canonical") not in build_certified_hero_registry()


def test_indomitable_raw_reroll_adds_fighter_level_and_spends_exactly_one_use() -> None:
    state = build_combatant_state(build_karnok_stoneward_level(9))
    roll = use_indomitable(state, "wisdom", FixedDiceProvider([10]))

    assert roll is not None
    assert roll.selected_roll == 10
    assert roll.total == 19
    assert "Indomitable +9" in roll.notation
    assert _indomitable_uses(state) == 0
    assert use_indomitable(state, "wisdom", FixedDiceProvider([10])) is None


def test_failed_save_automatically_uses_indomitable_but_success_does_not() -> None:
    failed_state = build_combatant_state(build_karnok_stoneward_level(9))
    roll, succeeded = resolve_saving_throw(failed_state, "wisdom", 15, FixedDiceProvider([2, 10]))
    assert succeeded is True
    assert roll is not None and roll.selected_roll == 10 and roll.total == 19
    assert "Indomitable +9" in roll.notation
    assert _indomitable_uses(failed_state) == 0

    successful_state = build_combatant_state(build_karnok_stoneward_level(9))
    roll, succeeded = resolve_saving_throw(successful_state, "wisdom", 15, FixedDiceProvider([15]))
    assert succeeded is True
    assert roll is not None and roll.total == 15
    assert _indomitable_uses(successful_state) == 1


def test_tactical_master_sap_replaces_graze_on_selected_greatsword() -> None:
    first = build_combatant_state(build_karnok_stoneward_level(9))
    second = build_combatant_state(build_karnok_stoneward_level(9))
    first.feature_last_turn_keys["savage-attacker"] = "1:first"
    second.feature_last_turn_keys["savage-attacker"] = "2:second"

    hit = resolve_attack(
        1, 1, first, second, first.template.weapon_attack, 5,
        FixedDiceProvider([10, 3, 3]), actor_event_id="first", target_event_id="second",
        spend_action=False, turn_key="1:first",
    )
    assert hit.hit is True
    assert any(effect.effect_id == "tactical-master-sap" for effect in second.timed_effects)

    reply = resolve_attack(
        2, 1, second, first, second.template.weapon_attack, 5,
        FixedDiceProvider([18, 2]), actor_event_id="second", target_event_id="first",
        spend_action=False, turn_key="2:second",
    )
    assert reply.attack_roll.mode is RollMode.DISADVANTAGE
    assert reply.attack_roll.rolls == [18, 2]
    assert reply.hit is False
    assert not any(effect.effect_id == "tactical-master-sap" for effect in second.timed_effects)

    miss_attacker = build_combatant_state(build_karnok_stoneward_level(9))
    miss_target = build_combatant_state(build_karnok_stoneward_level(9))
    hp_before = miss_target.current_hp
    miss = resolve_attack(
        3, 2, miss_attacker, miss_target, miss_attacker.template.weapon_attack, 5,
        FixedDiceProvider([1]), actor_event_id="miss-attacker", target_event_id="miss-target",
        spend_action=False, turn_key="2:miss-attacker",
    )
    assert miss.hit is False
    assert miss.damage_roll is None
    assert miss_target.current_hp == hp_before


def test_tactical_master_does_not_apply_sap_to_unselected_shortbow() -> None:
    first = build_combatant_state(build_karnok_stoneward_level(9))
    second = build_combatant_state(build_karnok_stoneward_level(9))
    first.feature_last_turn_keys["savage-attacker"] = "1:first"
    shortbow = first.template.alternate_weapon_attacks[0]

    hit = resolve_attack(
        1, 1, first, second, shortbow, 30,
        FixedDiceProvider([15, 4]), actor_event_id="first", target_event_id="second",
        spend_action=False, turn_key="1:first", close_enemy_active=False,
    )
    assert hit.hit is True
    assert not any(effect.effect_id == "tactical-master-sap" for effect in second.timed_effects)
