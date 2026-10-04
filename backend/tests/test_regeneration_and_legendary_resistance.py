from app.combat.dice import FixedDiceProvider
from app.combat.regeneration import apply_start_of_turn_regeneration, resolve_start_of_turn_regeneration
from app.combat.saving_throw_rolls import resolve_saving_throw
from app.combat.state import build_combatant_state
from app.combat.zero_hp import apply_damage
from app.content.monster_basic_candidates_2014 import basic_blockers_2014
from app.content.monster_source_2014 import load_monster_source_2014
from app.domain.encounters import EncounterCombatant
from app.domain.grid import GridPosition
from app.domain.models import (
    CombatantTemplate,
    ResourceDefinition,
    VisualLoadout,
    Weapon,
    WeaponAttack,
    WeaponAttackKind,
)
from app.domain.regeneration import RegenerationTrait
from app.domain.save_success_overrides import FailedSaveSuccessOverride
from app.domain.weapons_base import DamageType


def _template(**kwargs) -> CombatantTemplate:
    weapon = Weapon(
        id="test-claw",
        name="Claw",
        attack_kind=WeaponAttackKind.MELEE,
        dice_count=1,
        dice_size=6,
        damage_type="slashing",
        animation="slash",
    )
    return CombatantTemplate(
        id="test-regenerator",
        name="Test Regenerator",
        archetype="Test",
        kind="monster",
        armor_class=13,
        max_hp=40,
        speed_ft=30,
        initiative_bonus=0,
        weapon_attack=WeaponAttack(id="test-claw", weapon=weapon, attack_bonus=4, damage_bonus=2),
        visual=VisualLoadout(armor="none", main_hand="claw", body_style="troll"),
        source="test",
        saving_throw_bonuses={
            "strength": 2, "dexterity": 0, "constitution": 2,
            "intelligence": -1, "wisdom": 0, "charisma": -1,
        },
        **kwargs,
    )


def _member(template: CombatantTemplate) -> EncounterCombatant:
    member = EncounterCombatant(
        combatant_id="regen",
        side="monsters",
        position_ft=20,
        state=build_combatant_state(template),
    )
    member.state.position = GridPosition(x=4, y=4)
    return member


def test_start_of_turn_regeneration_restores_printed_amount() -> None:
    member = _member(_template(regeneration=RegenerationTrait(amount=10, requires_positive_hp=True)))
    member.state.current_hp = 7
    healed, died, suppressed = apply_start_of_turn_regeneration(member.state)
    assert (healed, died, suppressed) == (10, False, False)
    assert member.state.current_hp == 17


def test_regeneration_suppressed_by_printed_damage_types() -> None:
    member = _member(_template(regeneration=RegenerationTrait(
        amount=10, suppressed_by_damage_types=[DamageType.ACID, DamageType.FIRE],
    )))
    member.state.current_hp = 20
    apply_damage(member.state, 4, damage_types={DamageType.FIRE})
    assert member.state.current_hp == 16
    events, _ = resolve_start_of_turn_regeneration(1, 2, member)
    assert member.state.current_hp == 16
    assert "does not function" in events[0].description
    apply_damage(member.state, 4, damage_types={DamageType.SLASHING})
    apply_start_of_turn_regeneration(member.state)
    assert member.state.current_hp == 22


def test_troll_style_regeneration_delays_death_until_suppressed_turn() -> None:
    member = _member(_template(regeneration=RegenerationTrait(
        amount=10,
        requires_positive_hp=False,
        suppressed_by_damage_types=[DamageType.ACID, DamageType.FIRE],
        survives_zero_until_turn=True,
    )))
    outcome = apply_damage(member.state, 80, damage_types={DamageType.SLASHING})
    assert outcome == "unconscious"
    assert member.state.current_hp == 0
    assert member.state.is_alive is True
    assert member.state.is_dead is False
    apply_start_of_turn_regeneration(member.state)
    assert member.state.current_hp == 10
    assert member.state.is_unconscious is False
    apply_damage(member.state, 20, damage_types={DamageType.FIRE})
    assert member.state.current_hp == 0
    assert member.state.is_dead is False
    apply_start_of_turn_regeneration(member.state)
    assert member.state.is_dead is True
    assert member.state.current_hp == 0


def test_positive_hp_regeneration_does_not_revive_the_dead() -> None:
    member = _member(_template(regeneration=RegenerationTrait(amount=10, requires_positive_hp=True)))
    apply_damage(member.state, 80, damage_types={DamageType.SLASHING})
    assert member.state.is_dead is True
    healed, died, suppressed = apply_start_of_turn_regeneration(member.state)
    assert (healed, died, suppressed) == (0, False, False)
    assert member.state.is_dead is True


def test_legendary_resistance_turns_a_failed_save_into_success() -> None:
    template = _template(
        resources=[ResourceDefinition(id="legendary-resistance", name="Legendary Resistance", max_uses=3)],
        save_success_overrides=[FailedSaveSuccessOverride(
            source_id="legendary-resistance",
            source_name="Legendary Resistance",
            resource_id="legendary-resistance",
        )],
    )
    state = build_combatant_state(template)
    roll, succeeded = resolve_saving_throw(state, "wisdom", 20, FixedDiceProvider([1]))
    assert succeeded is True
    assert roll is not None and roll.total < 20
    assert state.resources[0].current_uses == 2
    state.resources[0].current_uses = 0
    _, failed = resolve_saving_throw(state, "wisdom", 20, FixedDiceProvider([1]))
    assert failed is False


def test_2014_troll_is_no_longer_blocked_only_by_regeneration() -> None:
    troll = next(item for item in load_monster_source_2014() if item.id == "troll")
    assert "mechanic:regeneration" not in basic_blockers_2014(troll)
    assert "source:trait" not in basic_blockers_2014(troll)
    assert basic_blockers_2014(troll) == ()
