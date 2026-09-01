from app.combat.attack_actions import resolve_attack_action
from app.combat.barbarian import enter_rage
from app.combat.dice import FixedDiceProvider
from app.combat.state import begin_turn, build_combatant_state
from app.content.audited_fighter import build_karnok_stoneward
from app.content.barbarian_progression import build_rokhan_stonefury_level
from app.content.barbarian_progression_profile import build_rokhan_stonefury_level5_profile
from app.domain.encounters import EncounterCombatant, EncounterSetup


def _setup() -> tuple[EncounterCombatant, EncounterCombatant, EncounterSetup]:
    hero = EncounterCombatant(
        combatant_id="hero-1:rokhan-stonefury-l5", side="heroes", position_ft=5,
        state=build_combatant_state(build_rokhan_stonefury_level(5)),
    )
    enemy = EncounterCombatant(
        combatant_id="monster-1:test-fighter", side="monsters", position_ft=10,
        state=build_combatant_state(build_karnok_stoneward()),
    )
    return hero, enemy, EncounterSetup(heroes=[hero], monsters=[enemy], hero_total_levels=5, monster_total_cr="0")


def test_barbarian5_snapshot_and_profile_are_exact() -> None:
    template = build_rokhan_stonefury_level(5)
    profile = build_rokhan_stonefury_level5_profile()
    resources = {item.id: item.max_uses for item in template.resources}
    greataxe, handaxe = template.weapon_attack, template.alternate_weapon_attacks[0]

    assert (template.id, template.level, template.armor_class, template.max_hp, template.speed_ft) == (
        "rokhan-stonefury-l5", 5, 14, 55, 40,
    )
    assert resources == {"rage": 3, "adrenaline-rush": 3, "relentless-endurance": 1}
    assert (greataxe.attack_bonus, greataxe.damage_bonus) == (7, 4)
    assert (handaxe.attack_bonus, handaxe.damage_bonus) == (7, 4)
    assert template.saving_throw_bonuses["strength"] == 7
    assert template.saving_throw_bonuses["constitution"] == 6
    assert template.skill_bonuses["athletics"] == 7
    assert template.wearing_heavy_armor is False
    assert template.progression_features.danger_sense is True
    assert template.progression_features.reckless_attack is True
    assert template.progression_features.frenzy is True
    assert template.attack_action is not None
    assert [slot.attack_ids for slot in template.attack_action.slots] == [
        ["rokhan-greataxe", "rokhan-handaxe-thrown"],
        ["rokhan-greataxe", "rokhan-handaxe-thrown"],
    ]
    assert profile.final_ability_scores.strength == 18
    assert profile.final_ability_scores.constitution == 16


def test_barbarian5_extra_attack_keeps_reckless_and_first_hit_frenzy_turn_context() -> None:
    hero, _enemy, setup = _setup()
    begin_turn(hero.state)
    assert enter_rage(1, 1, hero.state, hero.combatant_id) is not None
    events, _ = resolve_attack_action(
        2, 1, hero, setup,
        FixedDiceProvider([2, 15, 4, 8, 3, 5, 3, 14, 7]),
    )
    attacks = [event for event in events if event.event_type == "attack"]

    assert len(attacks) == 2
    assert all(event.hit for event in attacks)
    assert all(event.attack_roll is not None and event.attack_roll.mode == "advantage" for event in attacks)
    frenzy_parts = [
        part for event in attacks for part in event.damage_components if part.source == "Frenzy"
    ]
    assert len(frenzy_parts) == 1
    assert frenzy_parts[0].notation == "2d6+0"
    assert frenzy_parts[0].rolls == [3, 5]
    assert "uses Reckless Attack" in attacks[0].description
    assert "uses Reckless Attack" not in attacks[1].description
    assert hero.state.action_available is False
