from app.combat.barbarian import enter_rage
from app.combat.dice import FixedDiceProvider
from app.combat.encounter_attacks import resolve_encounter_attack
from app.combat.state import begin_turn, build_combatant_state
from app.content.audited_fighter import build_karnok_stoneward
from app.content.barbarian_progression import build_rokhan_stonefury_level
from app.content.barbarian_progression_profile import build_rokhan_stonefury_level4_profile
from app.domain.encounters import EncounterCombatant, EncounterSetup


def _setup() -> tuple[EncounterCombatant, EncounterCombatant, EncounterSetup]:
    hero = EncounterCombatant(
        combatant_id="hero-1:rokhan-stonefury-l4", side="heroes", position_ft=5,
        state=build_combatant_state(build_rokhan_stonefury_level(4)),
    )
    enemy = EncounterCombatant(
        combatant_id="monster-1:test-fighter", side="monsters", position_ft=10,
        state=build_combatant_state(build_karnok_stoneward()),
    )
    return hero, enemy, EncounterSetup(heroes=[hero], monsters=[enemy], hero_total_levels=4, monster_total_cr="0")


def test_barbarian4_split_asi_updates_every_combat_derived_value() -> None:
    template = build_rokhan_stonefury_level(4)
    profile = build_rokhan_stonefury_level4_profile()
    rage = next(resource for resource in template.resources if resource.id == "rage")
    handaxe = template.alternate_weapon_attacks[0]

    assert (template.id, template.level, template.max_hp, template.armor_class) == ("rokhan-stonefury-l4", 4, 45, 14)
    assert (template.weapon_attack.attack_bonus, template.weapon_attack.damage_bonus) == (6, 4)
    assert (handaxe.attack_bonus, handaxe.damage_bonus) == (6, 4)
    assert template.saving_throw_bonuses["strength"] == 6
    assert template.saving_throw_bonuses["constitution"] == 5
    assert template.skill_bonuses["athletics"] == 6
    assert template.weapon_masteries == ["flail", "pike", "longsword"]
    assert rage.max_uses == 3
    assert template.progression_features.frenzy is True
    assert profile.final_ability_scores.strength == 18
    assert profile.final_ability_scores.constitution == 16
    assert [(item.ability, item.amount) for item in profile.advancement_increases] == [("strength", 1), ("constitution", 1)]
    assert "Nature" not in profile.skill_proficiencies


def test_barbarian4_frenzy_still_applies_two_d6_with_improved_strength_math() -> None:
    hero, enemy, setup = _setup()
    begin_turn(hero.state)
    assert enter_rage(1, 1, hero.state, hero.combatant_id) is not None
    event = resolve_encounter_attack(
        2, 1, hero, enemy, hero.state.template.weapon_attack, 5,
        FixedDiceProvider([2, 15, 4, 8, 3, 5]), setup,
        spend_action=False, allow_reckless=True, turn_key=f"1:{hero.combatant_id}",
    )
    frenzy = next(part for part in event.damage_components if part.source == "Frenzy")

    assert event.attack_roll.modifier == 6
    assert frenzy.notation == "2d6+0"
    assert frenzy.rolls == [3, 5]
