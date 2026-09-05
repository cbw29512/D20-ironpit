from app.combat.attacks import resolve_attack
from app.combat.auras import roll_advantage_sources
from app.combat.concentration import start_concentration
from app.combat.death_saves import resolve_death_save
from app.combat.dice import FixedDiceProvider
from app.combat.encounter_attacks import resolve_encounter_attack
from app.combat.modifier_stack import add_modifier
from app.combat.saving_throws import resolve_save_action
from app.combat.state import build_combatant_state
from app.combat.zero_hp import apply_damage
from app.content.audited_fighter import build_karnok_stoneward
from app.content.demo import build_demo_fighter, build_goblin_warrior
from app.content.weapon_catalog import build_weapon
from app.domain.auras import RollAdvantageAura
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.modifiers import CombatModifier, ModifierKind
from app.domain.models import DamageType, RollMode, SavingThrowAction
from app.domain.traits import CombatTrait


def _member(combatant_id, side, position, template):
    return EncounterCombatant(
        combatant_id=combatant_id, side=side, position_ft=position,
        state=build_combatant_state(template),
    )


def _authority(template, *, radius=10):
    return template.model_copy(update={
        "roll_advantage_aura": RollAdvantageAura(
            name="Test Authority", radius_ft=radius,
            grants_attack_roll_advantage=True,
            grants_saving_throw_advantage=True,
            disabled_while_incapacitated=True,
        ),
    }, deep=True)


def _setup(heroes, monsters):
    return EncounterSetup(
        heroes=heroes, monsters=monsters,
        hero_total_levels=max(1, sum(member.state.template.level or 0 for member in heroes)),
        monster_total_cr="1/4",
    )


def test_roll_advantage_aura_is_same_side_range_bound_and_source_suppressed() -> None:
    source = _member("hero-source", "heroes", 0, _authority(build_demo_fighter()))
    source2 = _member("hero-source-2", "heroes", 5, _authority(build_demo_fighter()))
    ally = _member("hero-ally", "heroes", 10, build_demo_fighter())
    enemy = _member("monster-1", "monsters", 5, build_goblin_warrior())
    setup = _setup([source, source2, ally], [enemy])

    assert roll_advantage_sources(source, setup, "attack_roll") == 2
    assert roll_advantage_sources(ally, setup, "saving_throw") == 2
    assert roll_advantage_sources(enemy, setup, "saving_throw") == 0

    ally.position_ft = 16
    assert roll_advantage_sources(ally, setup, "saving_throw") == 0
    ally.position_ft = 10
    source.state.active_effect_ids.append("incapacitated")
    assert roll_advantage_sources(ally, setup, "saving_throw") == 1
    source2.state.current_hp = 0
    assert roll_advantage_sources(ally, setup, "saving_throw") == 0


def test_weapon_attack_and_save_action_consume_the_same_aura_source() -> None:
    source = _member("hero-source", "heroes", 0, _authority(build_demo_fighter()))
    attacker = _member("hero-attacker", "heroes", 10, build_demo_fighter())
    target = _member("monster-target", "monsters", 15, build_goblin_warrior())
    setup = _setup([source, attacker], [target])

    attack = resolve_encounter_attack(
        1, 1, attacker, target, attacker.state.template.weapon_attack, 5,
        FixedDiceProvider([2, 18, 4]), setup, spend_action=False,
    )
    assert attack.attack_roll is not None
    assert attack.attack_roll.mode is RollMode.ADVANTAGE
    assert attack.attack_roll.selected_roll == 18

    save_target = _member("hero-save-target", "heroes", 10, build_demo_fighter())
    save_actor = _member("monster-save-actor", "monsters", 15, build_goblin_warrior())
    save_setup = _setup([source, save_target], [save_actor])
    action = SavingThrowAction(
        id="test-save", name="Test Save", save_ability="dexterity", dc=15, range_ft=30,
    )
    event = resolve_save_action(
        1, 1, save_actor, save_target, action, 5, FixedDiceProvider([2, 18]),
        spend_action=False, spend_resource=False, setup=save_setup,
    )
    assert event.saving_throw_roll is not None
    assert event.saving_throw_roll.mode is RollMode.ADVANTAGE
    assert event.saving_throw_roll.selected_roll == 18
    assert event.save_succeeded is True


def test_damage_triggered_saves_use_generic_advantage_sources() -> None:
    concentrating = build_combatant_state(build_demo_fighter())
    start_concentration(concentrating, "hero-1", "test-spell", 1)
    apply_damage(
        concentrating, 1, dice=FixedDiceProvider([2, 18]),
        saving_throw_advantage_sources=1,
    )
    assert concentrating.concentration is not None

    zombie_template = build_goblin_warrior().model_copy(update={
        "combat_traits": [CombatTrait.UNDEAD_FORTITUDE],
        "saving_throw_bonuses": {
            "strength": 1, "dexterity": -2, "constitution": 4,
            "intelligence": -4, "wisdom": -2, "charisma": -3,
        },
    }, deep=True)
    zombie = build_combatant_state(zombie_template)
    outcome = apply_damage(
        zombie, zombie.current_hp, damage_types={DamageType.BLUDGEONING},
        dice=FixedDiceProvider([2, 20]), saving_throw_advantage_sources=1,
    )
    assert outcome == "undead_fortitude"
    assert zombie.current_hp == 1


def test_topple_uses_the_same_target_save_advantage_source() -> None:
    attacker_template = build_karnok_stoneward().model_copy(
        update={"level": 1, "weapon_masteries": ["battleaxe"], "combat_traits": []}, deep=True,
    )
    attacker = build_combatant_state(attacker_template)
    attack = attacker.template.weapon_attack.model_copy(update={
        "id": "topple-battleaxe", "weapon": build_weapon("battleaxe"),
        "attack_ability_modifier": 3,
    }, deep=True)
    target_template = build_goblin_warrior().model_copy(update={
        "armor_class": 10, "max_hp": 40,
        "saving_throw_bonuses": {**build_goblin_warrior().saving_throw_bonuses, "constitution": 0},
    }, deep=True)
    target = build_combatant_state(target_template)

    event = resolve_attack(
        1, 1, attacker, target, attack, 5, FixedDiceProvider([15, 4, 2, 18]),
        spend_action=False, target_save_advantage_sources=1,
    )
    assert event.saving_throw_roll is not None
    assert event.saving_throw_roll.mode is RollMode.ADVANTAGE
    assert event.saving_throw_roll.selected_roll == 18
    assert event.save_succeeded is True


def test_death_saves_use_generic_advantage_and_saving_throw_bonus_dice() -> None:
    advantaged = build_combatant_state(build_demo_fighter())
    apply_damage(advantaged, advantaged.current_hp)
    event = resolve_death_save(
        1, 1, "hero-1", advantaged, FixedDiceProvider([1, 12]), advantage_sources=1,
    )
    assert event.death_save_roll is not None
    assert event.death_save_roll.mode is RollMode.ADVANTAGE
    assert event.death_save_roll.selected_roll == 12
    assert advantaged.death_save_successes == 1
    assert advantaged.death_save_failures == 0

    blessed = build_combatant_state(build_demo_fighter())
    apply_damage(blessed, blessed.current_hp)
    add_modifier(blessed, CombatModifier(
        id="bless-death", source_id="hero-2", source_effect_id="bless",
        kind=ModifierKind.SAVING_THROW_BONUS_DIE, dice_count=1, dice_size=4,
    ))
    blessed_event = resolve_death_save(1, 1, "hero-1", blessed, FixedDiceProvider([8, 2]))
    assert blessed_event.death_save_roll is not None
    assert blessed_event.death_save_roll.selected_roll == 8
    assert blessed_event.death_save_roll.total == 10
    assert blessed.death_save_successes == 1
