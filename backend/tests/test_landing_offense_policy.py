from __future__ import annotations

from app.combat.action_economy import spend
from app.combat.dice import FixedDiceProvider
from app.combat.encounter_combat_turn import resolve_combat_turn
from app.combat.landing_offense_policy import decide_post_move_offense, melee_can_land_now, weapon_mean_damage
from app.combat.spell_policy import choose_spell
from app.combat.state import begin_turn, build_combatant_state
from app.content.arena_map import build_standard_iron_pit_map
from app.content.monsters import build_commoner
from app.content.sorcerer_draconic_2014_spell_support import magic_missile_2014
from app.domain.combatants import ResourceDefinition
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.grid import GridPosition
from app.domain.actions import AttackActionDefinition, AttackActionSlot
from app.domain.models import DamageType, SavingThrowAction, Weapon, WeaponAttack, WeaponAttackKind
from app.domain.spells import SpellSaveAction
from app.domain.targeting import AreaTargeting


def _bite() -> WeaponAttack:
    return WeaponAttack(
        id="test-bite",
        weapon=Weapon(
            id="test-bite",
            name="Bite",
            attack_kind=WeaponAttackKind.MELEE,
            dice_count=3,
            dice_size=10,
            damage_type=DamageType.PIERCING,
            animation="bite",
            reach_ft=5,
        ),
        attack_bonus=6,
        damage_bonus=3,
    )


def _claw() -> WeaponAttack:
    return WeaponAttack(
        id="test-claw",
        weapon=Weapon(
            id="test-claw",
            name="Claw",
            attack_kind=WeaponAttackKind.MELEE,
            dice_count=1,
            dice_size=8,
            damage_type=DamageType.SLASHING,
            animation="slash",
            reach_ft=5,
        ),
        attack_bonus=6,
        damage_bonus=3,
    )


def _caster_monster(*, extra_attacks: list[WeaponAttack] | None = None):
    template = build_commoner().model_copy(update={
        "max_hp": 40,
        "speed_ft": 30,
        "weapon_attack": _bite(),
        "alternate_weapon_attacks": extra_attacks or [],
        "auto_hit_spell_actions": [magic_missile_2014()],
        "resources": [ResourceDefinition(id="spell-slot-1", name="Level 1 Slot", max_uses=1)],
        "ruleset": "2014",
    })
    return template


def _member(template, combatant_id: str, side: str, position_ft: int = 0, *, x: int | None = None, y: int | None = None):
    state = build_combatant_state(template)
    if x is not None and y is not None:
        state.position = GridPosition(x=x, y=y)
    return EncounterCombatant(combatant_id=combatant_id, side=side, position_ft=position_ft, state=state)


def _setup(attacker, target, *, mapped: bool = False):
    return EncounterSetup(
        heroes=[target] if attacker.side == "monsters" else [attacker],
        monsters=[attacker] if attacker.side == "monsters" else [target],
        hero_total_levels=1,
        monster_total_cr="0",
        ruleset="2014",
        map_definition=build_standard_iron_pit_map() if mapped else None,
    )


def test_printed_bite_beats_magic_missile() -> None:
    assert weapon_mean_damage(_bite()) == 19.5
    assert 3 * ((4 + 1) / 2 + 1) == 10.5


def test_melee_choice_uses_bite_when_bite_can_reach() -> None:
    attacker = _member(_caster_monster(), "monster", "monsters", 0)
    target = _member(build_commoner(), "hero", "heroes", 5)
    begin_turn(attacker.state)
    pick = decide_post_move_offense(attacker, _setup(attacker, target), "1:monster")
    assert pick.family == "standard-attack"
    assert pick.payload[1].id == "test-bite"


def test_unreachable_bite_uses_magic_missile() -> None:
    attacker = _member(_caster_monster(), "monster", "monsters", 0)
    target = _member(build_commoner(), "hero", "heroes", 80)
    begin_turn(attacker.state)
    setup = _setup(attacker, target)
    assert melee_can_land_now(attacker, setup) is False
    events, _ = resolve_combat_turn(1, 1, attacker, target, setup, FixedDiceProvider([4, 4, 4]))
    assert any(event.feature_id == "magic-missile" for event in events)
    assert not [event for event in events if event.event_type == "attack"]


def test_reachable_bite_is_used_instead_of_magic_missile() -> None:
    attacker = _member(_caster_monster(), "monster", "monsters", 0)
    target = _member(build_commoner(), "hero", "heroes", 5)
    begin_turn(attacker.state)
    events, _ = resolve_combat_turn(1, 1, attacker, target, _setup(attacker, target), FixedDiceProvider([15, 6, 6, 6, 6, 6, 6]))
    assert any(event.event_type == "attack" and event.attack_id == "test-bite" for event in events)
    assert not [event for event in events if event.feature_id == "magic-missile"]


def test_monster_closes_to_bite_when_melee_can_land_this_turn() -> None:
    attacker = _member(_caster_monster(), "monster", "monsters", x=0, y=7)
    target = _member(build_commoner(), "hero", "heroes", x=5, y=7)
    setup = _setup(attacker, target, mapped=True)
    events, _ = resolve_combat_turn(1, 1, attacker, target, setup, FixedDiceProvider([15, 6, 6, 6, 6, 6, 6]))
    assert any(event.event_type == "movement" for event in events)
    assert any(event.event_type == "attack" and event.attack_id == "test-bite" for event in events)
    assert not [event for event in events if event.feature_id == "magic-missile"]


def test_higher_damage_area_save_beats_reachable_melee() -> None:
    breath = SavingThrowAction(
        id="acid-line",
        name="Acid Line",
        save_ability="dexterity",
        dc=14,
        range_ft=30,
        area=AreaTargeting(shape="line", origin="self", length_ft=30, width_ft=5),
        damage_dice_count=11,
        damage_dice_size=8,
        damage_type="acid",
        success_damage="half",
    )
    attacker = _member(
        _caster_monster().model_copy(update={
            "saving_throw_actions": [breath],
            "auto_hit_spell_actions": [],
        }),
        "monster",
        "monsters",
        x=4,
        y=7,
    )
    target = _member(build_commoner(), "hero", "heroes", x=5, y=7)
    begin_turn(attacker.state)
    setup = _setup(attacker, target, mapped=True)
    assert melee_can_land_now(attacker, setup) is True
    pick = decide_post_move_offense(attacker, setup, "1:monster")
    assert pick.family == "area-save"
    assert pick.payload[0].id == "acid-line"
    events, _ = resolve_combat_turn(1, 1, attacker, target, setup, FixedDiceProvider([8] * 20))
    assert any(event.feature_id == "acid-line" for event in events)
    assert not [event for event in events if event.event_type == "attack"]


def test_mixed_multiattack_beats_weaker_standalone_save() -> None:
    constrict = SavingThrowAction(
        id="test-constrict",
        name="Constrict",
        save_ability="strength",
        dc=14,
        range_ft=10,
        target_max_size="large",
        damage_dice_count=2,
        damage_dice_size=8,
        damage_bonus=4,
        damage_type="bludgeoning",
        success_damage="none",
        grapple_escape_dc=14,
    )
    attacker = _member(
        _caster_monster().model_copy(update={
            "auto_hit_spell_actions": [],
            "saving_throw_actions": [constrict],
            "attack_action": AttackActionDefinition(
                id="test-multiattack",
                name="Multiattack",
                slots=[
                    AttackActionSlot(attack_ids=["test-bite"], save_action_ids=[]),
                    AttackActionSlot(attack_ids=[], save_action_ids=["test-constrict"]),
                ],
            ),
        }),
        "monster",
        "monsters",
        0,
    )
    target = _member(build_commoner().model_copy(update={"max_hp": 80}), "hero", "heroes", 5)
    begin_turn(attacker.state)
    setup = _setup(attacker, target)
    pick = decide_post_move_offense(attacker, setup, "1:monster")
    assert pick.family == "attack-action"
    events, _ = resolve_combat_turn(
        1, 1, attacker, target, setup, FixedDiceProvider([18, 6, 6, 6, 8, 6, 6]),
    )
    assert any(event.event_type == "attack" and event.attack_id == "test-bite" for event in events)
    assert any(event.feature_id == "test-constrict" for event in events)


def test_highest_damage_melee_wins_among_melee_options() -> None:
    attacker = _member(_caster_monster(extra_attacks=[_claw()]), "monster", "monsters", 0)
    target = _member(build_commoner(), "hero", "heroes", 5)
    begin_turn(attacker.state)
    pick = decide_post_move_offense(attacker, _setup(attacker, target), "1:monster")
    assert pick.family == "standard-attack"
    assert pick.payload[1].id == "test-bite"


def test_multiattack_beats_equal_damage_standalone_when_only_one_slot_can_land() -> None:
    bite = _bite()
    bite.weapon.reach_ft = 10
    claw = _claw()
    attacker = _member(
        _caster_monster(extra_attacks=[claw]).model_copy(update={
            "weapon_attack": bite,
            "auto_hit_spell_actions": [],
            "attack_action": AttackActionDefinition(
                id="test-multiattack",
                name="Multiattack",
                slots=[
                    AttackActionSlot(attack_ids=["test-bite"], save_action_ids=[]),
                    AttackActionSlot(attack_ids=["test-claw"], save_action_ids=[]),
                ],
            ),
        }),
        "monster",
        "monsters",
        0,
    )
    target = _member(build_commoner(), "hero", "heroes", 10)
    begin_turn(attacker.state)
    pick = decide_post_move_offense(attacker, _setup(attacker, target), "1:monster")
    assert pick.family == "attack-action"


def test_spent_action_does_not_choose_another_attack() -> None:
    attacker = _member(_caster_monster(), "monster", "monsters", 0)
    target = _member(build_commoner(), "hero", "heroes", 5)
    begin_turn(attacker.state)
    spend(attacker.state, "action")
    setup = _setup(attacker, target)
    assert melee_can_land_now(attacker, setup) is True
    pick = decide_post_move_offense(attacker, setup, "1:monster")
    assert pick.family == "dodge"


def test_no_landable_option_defaults_to_dodge() -> None:
    template = build_commoner().model_copy(update={"auto_hit_spell_actions": [], "spell_save_actions": []})
    attacker = _member(template, "monster", "monsters", 0)
    target = _member(build_commoner(), "hero", "heroes", 80)
    begin_turn(attacker.state)
    pick = decide_post_move_offense(attacker, _setup(attacker, target), "1:monster")
    assert pick.family == "dodge"
    events, _ = resolve_combat_turn(1, 1, attacker, target, _setup(attacker, target), FixedDiceProvider([1]))
    assert any(event.feature_id == "dodge" for event in events)


def test_damage_spell_beats_higher_level_control_spell() -> None:
    control = SpellSaveAction(
        id="hold-person", name="Hold Person", level=2, range_ft=60,
        save_ability="wisdom", dc=13, concentration=True, duration_minutes=1,
    )
    damage = SpellSaveAction(
        id="magic-bolt", name="Magic Bolt", level=0, range_ft=60,
        save_ability="dexterity", dc=12, damage_dice_count=1, damage_dice_size=10,
        damage_type="force", success_damage="none",
    )
    base = build_commoner()
    caster = _member(
        base.model_copy(update={
            "spell_save_actions": [control, damage],
            "resources": [ResourceDefinition(id="spell-slot-2", name="Level 2 Slot", max_uses=1)],
        }),
        "caster",
        "heroes",
        0,
    )
    target = _member(build_commoner(), "monster", "monsters", 30)
    choice = choose_spell(caster, _setup(caster, target), "1:caster")
    assert choice is not None
    assert choice.action.id == "magic-bolt"
