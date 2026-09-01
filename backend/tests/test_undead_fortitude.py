from app.combat.attacks import resolve_attack
from app.combat.dice import FixedDiceProvider
from app.combat.saving_throws import resolve_save_action
from app.combat.state import build_combatant_state
from app.combat.zero_hp import apply_damage
from app.content.demo import build_goblin_warrior
from app.domain.models import DamageType, EncounterCombatant, OnHitDamage, SavingThrowAction
from app.domain.traits import CombatTrait


def _zombie_state():
    template = build_goblin_warrior().model_copy(update={
        "id": "test-zombie",
        "name": "Test Zombie",
        "armor_class": 8,
        "combat_traits": [CombatTrait.UNDEAD_FORTITUDE],
        "saving_throw_bonuses": {
            "strength": 1, "dexterity": -2, "constitution": 4,
            "intelligence": -4, "wisdom": -2, "charisma": -3,
        },
    })
    return build_combatant_state(template)


def test_undead_fortitude_success_leaves_monster_at_one_hp() -> None:
    state = _zombie_state()
    outcome = apply_damage(
        state, state.current_hp, damage_types={DamageType.BLUDGEONING}, dice=FixedDiceProvider([20]),
    )
    assert outcome == "undead_fortitude"
    assert state.current_hp == 1
    assert state.is_alive is True
    assert state.is_dead is False


def test_undead_fortitude_failure_kills_monster() -> None:
    state = _zombie_state()
    outcome = apply_damage(
        state, state.current_hp, damage_types={DamageType.BLUDGEONING}, dice=FixedDiceProvider([1]),
    )
    assert outcome == "dead"
    assert state.current_hp == 0
    assert state.is_dead is True


def test_radiant_and_critical_damage_bypass_undead_fortitude_without_dice() -> None:
    radiant = _zombie_state()
    assert apply_damage(radiant, radiant.current_hp, damage_types={DamageType.RADIANT}) == "dead"
    critical = _zombie_state()
    assert apply_damage(
        critical, critical.current_hp, critical=True, damage_types={DamageType.BLUDGEONING},
    ) == "dead"


def test_any_applied_radiant_component_bypasses_undead_fortitude() -> None:
    attacker = build_combatant_state(build_goblin_warrior())
    defender = _zombie_state()
    defender.current_hp = 4
    attack = attacker.template.weapon_attack.model_copy(update={
        "on_hit_damage": [OnHitDamage(
            source="Radiant rider", dice_count=1, dice_size=4,
            damage_bonus=0, damage_type=DamageType.RADIANT,
        )],
    })
    event = resolve_attack(
        1, 1, attacker, defender, attack, 5, FixedDiceProvider([15, 1, 1]),
    )
    assert event.hit is True
    assert event.critical is False
    assert defender.is_dead is True
    assert defender.current_hp == 0


def test_temporary_hp_does_not_lower_undead_fortitude_dc() -> None:
    state = _zombie_state()
    state.current_hp = 5
    state.temporary_hp = 5
    outcome = apply_damage(
        state, 10, damage_types={DamageType.BLUDGEONING}, dice=FixedDiceProvider([10]),
    )
    assert outcome == "dead"


def test_save_action_damage_can_trigger_undead_fortitude() -> None:
    actor = EncounterCombatant(
        combatant_id="monster-1:goblin", side="monsters", position_ft=0,
        state=build_combatant_state(build_goblin_warrior()),
    )
    target_state = _zombie_state()
    target_state.current_hp = 3
    target = EncounterCombatant(
        combatant_id="monster-2:zombie", side="monsters", position_ft=10, state=target_state,
    )
    action = SavingThrowAction(
        id="test-blast", name="Test Blast", save_ability="dexterity", dc=20, range_ft=30,
        damage_dice_count=1, damage_dice_size=6, damage_type="bludgeoning", success_damage="none",
    )
    event = resolve_save_action(
        1, 1, actor, target, action, 10, FixedDiceProvider([1, 6, 20]),
    )
    assert event.save_succeeded is False
    assert target.state.current_hp == 1
    assert target.state.is_dead is False
    assert "Undead Fortitude" in event.description
