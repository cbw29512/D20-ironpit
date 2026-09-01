from app.combat.barbarian import end_rage, enter_rage
from app.combat.state import begin_turn, build_combatant_state
from app.combat.timed_conditions import apply_timed_condition
from app.content.barbarian_berserker_progression_profile import build_rokhan_stonefury_level6_profile
from app.content.barbarian_progression import build_rokhan_stonefury_level


def test_barbarian6_snapshot_and_profile_are_exact() -> None:
    template = build_rokhan_stonefury_level(6)
    profile = build_rokhan_stonefury_level6_profile()
    resources = {item.id: item.max_uses for item in template.resources}
    greataxe, handaxe = template.weapon_attack, template.alternate_weapon_attacks[0]

    assert (template.id, template.level, template.armor_class, template.max_hp, template.speed_ft) == (
        "rokhan-stonefury-l6", 6, 14, 65, 40,
    )
    assert resources == {"rage": 4, "adrenaline-rush": 3, "relentless-endurance": 1}
    assert (greataxe.attack_bonus, greataxe.damage_bonus) == (7, 4)
    assert (handaxe.attack_bonus, handaxe.damage_bonus) == (7, 4)
    assert template.saving_throw_bonuses["strength"] == 7
    assert template.saving_throw_bonuses["constitution"] == 6
    assert template.skill_bonuses["athletics"] == 7
    assert template.progression_features.fast_movement_bonus_ft == 10
    assert template.progression_features.mindless_rage is True
    assert template.progression_features.frenzy is True
    assert template.progression_features.reckless_attack is True
    assert template.progression_features.danger_sense is True
    assert template.attack_action is not None and len(template.attack_action.slots) == 2
    assert profile.level == 6


def test_mindless_rage_ends_existing_charmed_and_frightened_and_blocks_reapplication() -> None:
    state = build_combatant_state(build_rokhan_stonefury_level(6))
    assert apply_timed_condition(state, "charmed", "source-1", source_effect_id="charm-test") == "charmed"
    assert apply_timed_condition(state, "frightened", "source-2", source_effect_id="fear-test") == "frightened"
    assert apply_timed_condition(state, "poisoned", "source-3", source_effect_id="poison-test") == "poisoned"
    begin_turn(state)

    event = enter_rage(1, 1, state, "hero-1:rokhan-stonefury-l6")

    assert event is not None
    assert event.removed_condition_ids == ["charmed", "frightened"]
    assert "Mindless Rage ends charmed, frightened" in event.description
    assert "rage" in state.active_effect_ids
    assert "poisoned" in state.active_effect_ids
    assert "charmed" not in state.active_effect_ids
    assert "frightened" not in state.active_effect_ids
    assert {effect.effect_id for effect in state.timed_effects} == {"poisoned"}
    assert apply_timed_condition(state, "charmed", "source-4") is None
    assert apply_timed_condition(state, "frightened", "source-5") is None
    assert apply_timed_condition(state, "poisoned", "source-6") == "poisoned"

    end_rage(state)
    assert "rage" not in state.active_effect_ids
    assert apply_timed_condition(state, "charmed", "source-7") == "charmed"
    assert apply_timed_condition(state, "frightened", "source-8") == "frightened"
