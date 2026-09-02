from app.combat.barbarian import enter_rage
from app.combat.dice import FixedDiceProvider
from app.combat.encounter_attacks import resolve_encounter_attack
from app.combat.state import begin_turn, build_combatant_state
from app.content.audited_fighter import build_karnok_stoneward
from app.content.barbarian_progression import build_rokhan_stonefury_level
from app.content.barbarian_progression_profile import build_rokhan_stonefury_level3_profile
from app.domain.encounters import EncounterCombatant, EncounterSetup


def _setup() -> tuple[EncounterCombatant, EncounterCombatant, EncounterSetup]:
    hero = EncounterCombatant(
        combatant_id="hero-1:rokhan-stonefury-l3", side="heroes", position_ft=5,
        state=build_combatant_state(build_rokhan_stonefury_level(3)),
    )
    enemy = EncounterCombatant(
        combatant_id="monster-1:test-fighter", side="monsters", position_ft=10,
        state=build_combatant_state(build_karnok_stoneward()),
    )
    return hero, enemy, EncounterSetup(heroes=[hero], monsters=[enemy], hero_total_levels=3, monster_total_cr="0")


def _enter_rage(hero: EncounterCombatant) -> None:
    begin_turn(hero.state)
    assert enter_rage(1, 1, hero.state, hero.combatant_id) is not None


def test_barbarian3_snapshot_keeps_noncombat_primal_knowledge_out_of_combat_progression() -> None:
    template = build_rokhan_stonefury_level(3)
    profile = build_rokhan_stonefury_level3_profile()
    rage = next(resource for resource in template.resources if resource.id == "rage")

    assert (template.id, template.level, template.max_hp) == ("rokhan-stonefury-l3", 3, 32)
    assert rage.max_uses == 3
    assert template.rage_damage_bonus == 2
    assert template.progression_features.danger_sense is True
    assert template.progression_features.reckless_attack is True
    assert template.progression_features.frenzy is True
    assert template.weapon_attack.attack_ability == "strength"
    assert template.alternate_weapon_attacks[0].attack_ability == "strength"
    assert "Nature" not in profile.skill_proficiencies
    assert "Animal Handling" not in profile.skill_proficiencies


def test_frenzy_adds_two_d6_to_first_raging_reckless_strength_hit() -> None:
    hero, enemy, setup = _setup()
    _enter_rage(hero)
    turn_key = f"1:{hero.combatant_id}"
    event = resolve_encounter_attack(
        2, 1, hero, enemy, hero.state.template.weapon_attack, 5,
        FixedDiceProvider([2, 15, 4, 8, 3, 5]), setup,
        spend_action=False, allow_reckless=True, turn_key=turn_key,
    )
    frenzy = next(part for part in event.damage_components if part.source == "Frenzy")
    assert event.hit is True
    assert frenzy.notation == "2d6+0"
    assert frenzy.rolls == [3, 5]
    assert frenzy.damage_type == "slashing"


def test_frenzy_miss_does_not_consume_first_hit() -> None:
    hero, enemy, setup = _setup()
    _enter_rage(hero)
    turn_key = f"1:{hero.combatant_id}"
    enemy.state.template.armor_class = 99
    miss = resolve_encounter_attack(
        2, 1, hero, enemy, hero.state.template.weapon_attack, 5,
        FixedDiceProvider([2, 3]), setup,
        spend_action=False, allow_reckless=True, turn_key=turn_key,
    )
    assert miss.hit is False
    assert not miss.damage_components

    enemy.state.template.armor_class = 10
    hit = resolve_encounter_attack(
        3, 1, hero, enemy, hero.state.template.weapon_attack, 5,
        FixedDiceProvider([15, 4, 8, 2, 6, 5]), setup,
        spend_action=False, allow_reckless=True, turn_key=turn_key,
    )
    assert hit.hit is True
    assert [part.source for part in hit.damage_components].count("Frenzy") == 1


def test_frenzy_is_first_hit_only_per_turn() -> None:
    hero, enemy, setup = _setup()
    _enter_rage(hero)
    turn_key = f"1:{hero.combatant_id}"
    first = resolve_encounter_attack(
        2, 1, hero, enemy, hero.state.template.weapon_attack, 5,
        FixedDiceProvider([15, 4, 8, 2, 6, 5]), setup,
        spend_action=False, allow_reckless=True, turn_key=turn_key,
    )
    second = resolve_encounter_attack(
        3, 1, hero, enemy, hero.state.template.weapon_attack, 5,
        FixedDiceProvider([15, 7, 5]), setup,
        spend_action=False, allow_reckless=True, turn_key=turn_key,
    )
    assert any(part.source == "Frenzy" for part in first.damage_components)
    assert all(part.source != "Frenzy" for part in second.damage_components)


def test_frenzy_requires_rage_reckless_strength_and_turn_identity() -> None:
    hero, enemy, setup = _setup()
    turn_key = f"1:{hero.combatant_id}"
    no_rage = resolve_encounter_attack(
        1, 1, hero, enemy, hero.state.template.weapon_attack, 5,
        FixedDiceProvider([15, 4, 8, 2]), setup,
        spend_action=False, allow_reckless=True, turn_key=turn_key,
    )
    assert all(part.source != "Frenzy" for part in no_rage.damage_components)

    hero, enemy, setup = _setup()
    _enter_rage(hero)
    no_reckless = resolve_encounter_attack(
        2, 1, hero, enemy, hero.state.template.weapon_attack, 5,
        FixedDiceProvider([15, 4, 8]), setup,
        spend_action=False, allow_reckless=False, turn_key=turn_key,
    )
    assert all(part.source != "Frenzy" for part in no_reckless.damage_components)

    hero, enemy, setup = _setup()
    _enter_rage(hero)
    dex_attack = hero.state.template.weapon_attack.model_copy(update={"attack_ability": "dexterity"})
    wrong_ability = resolve_encounter_attack(
        2, 1, hero, enemy, dex_attack, 5,
        FixedDiceProvider([15, 4, 8]), setup,
        spend_action=False, allow_reckless=True, turn_key=turn_key,
    )
    assert all(part.source != "Frenzy" for part in wrong_ability.damage_components)


def test_frenzy_critical_doubles_extra_damage_dice() -> None:
    hero, enemy, setup = _setup()
    _enter_rage(hero)
    turn_key = f"1:{hero.combatant_id}"
    event = resolve_encounter_attack(
        2, 1, hero, enemy, hero.state.template.weapon_attack, 5,
        FixedDiceProvider([1, 20, 1, 2, 5, 6, 1, 2, 3, 4]), setup,
        spend_action=False, allow_reckless=True, turn_key=turn_key,
    )
    frenzy = next(part for part in event.damage_components if part.source == "Frenzy")
    assert event.critical is True
    assert frenzy.notation == "4d6+0"
    assert frenzy.rolls == [1, 2, 3, 4]


def test_frenzy_works_with_strength_based_thrown_handaxe_and_matches_damage_type() -> None:
    hero, enemy, setup = _setup()
    _enter_rage(hero)
    handaxe = hero.state.template.alternate_weapon_attacks[0]
    event = resolve_encounter_attack(
        2, 1, hero, enemy, handaxe, 20,
        FixedDiceProvider([2, 15, 4, 6, 2, 5]), setup,
        spend_action=False, allow_reckless=True, turn_key=f"1:{hero.combatant_id}",
        close_enemy_active=False,
    )
    frenzy = next(part for part in event.damage_components if part.source == "Frenzy")
    assert event.hit is True
    assert frenzy.damage_type == handaxe.weapon.damage_type
