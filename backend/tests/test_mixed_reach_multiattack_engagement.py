from __future__ import annotations

from app.combat.dice import FixedDiceProvider
from app.combat.encounter_combat_turn import resolve_combat_turn
from app.combat.encounter_targeting import combatant_distance
from app.combat.landing_offense_policy import decide_post_move_offense
from app.combat.offensive_movement_policy import choose_offensive_movement_intent
from app.combat.offensive_ranges import tightest_usable_melee_reach_ft
from app.combat.state import begin_turn, build_combatant_state
from app.content.arena_map import build_standard_iron_pit_map
from app.content.capability_compiler import compile_combatant
from app.content.fighter_champion_2014_runtime import build_karnok_stoneward_2014
from app.content.monster_definition_adapter_2014 import adapt_basic_monster_2014
from app.content.monster_source_2014 import load_monster_source_2014
from app.content.monsters import build_commoner
from app.domain.actions import AttackActionDefinition, AttackActionSlot
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.grid import GridPosition
from app.domain.models import DamageType, Weapon, WeaponAttack, WeaponAttackKind


def _member(template, combatant_id: str, side: str, x: int, y: int) -> EncounterCombatant:
    state = build_combatant_state(template)
    state.position = GridPosition(x=x, y=y)
    return EncounterCombatant(combatant_id=combatant_id, side=side, position_ft=0, state=state)


def _mapped_setup(attacker: EncounterCombatant, target: EncounterCombatant) -> EncounterSetup:
    return EncounterSetup(
        heroes=[target] if attacker.side == "monsters" else [attacker],
        monsters=[attacker] if attacker.side == "monsters" else [target],
        hero_total_levels=1,
        monster_total_cr="0",
        ruleset="2014",
        map_definition=build_standard_iron_pit_map(),
    )


def _mixed_reach_template():
    bite = WeaponAttack(
        id="test-beak",
        weapon=Weapon(
            id="test-beak", name="Beak", attack_kind=WeaponAttackKind.MELEE,
            dice_count=1, dice_size=8, damage_type=DamageType.PIERCING, animation="bite", reach_ft=10,
        ),
        attack_bonus=8,
        damage_bonus=4,
    )
    talons = WeaponAttack(
        id="test-talons",
        weapon=Weapon(
            id="test-talons", name="Talons", attack_kind=WeaponAttackKind.MELEE,
            dice_count=1, dice_size=6, damage_type=DamageType.SLASHING, animation="slash", reach_ft=5,
        ),
        attack_bonus=8,
        damage_bonus=4,
    )
    return build_commoner().model_copy(update={
        "max_hp": 80,
        "speed_ft": 40,
        "weapon_attack": bite,
        "alternate_weapon_attacks": [talons],
        "attack_action": AttackActionDefinition(
            id="test-multiattack",
            name="Multiattack",
            slots=[
                AttackActionSlot(attack_ids=["test-beak"], save_action_ids=[]),
                AttackActionSlot(attack_ids=["test-talons"], save_action_ids=[]),
            ],
        ),
    })


def test_tightest_multiattack_reach_is_the_shortest_still_legal_slot() -> None:
    attacker = _member(_mixed_reach_template(), "monster", "monsters", 0, 7)
    target = _member(build_commoner(), "hero", "heroes", 2, 7)
    assert tightest_usable_melee_reach_ft(attacker, target) == 5


def test_longer_reach_slot_does_not_stop_closing_to_remaining_multiattack_slot() -> None:
    attacker = _member(_mixed_reach_template(), "monster", "monsters", 0, 7)
    target = _member(build_commoner(), "hero", "heroes", 2, 7)
    begin_turn(attacker.state)
    setup = _mapped_setup(attacker, target)
    assert combatant_distance(attacker, target) == 10
    intent = choose_offensive_movement_intent(attacker, setup, "1:monster")
    assert intent is not None
    assert intent.desired_distance_ft == 5
    pick = decide_post_move_offense(attacker, setup, "1:monster")
    assert pick.family == "attack-action"


def test_2014_roc_uses_fly_speed_and_fires_both_multiattack_slots_in_reach() -> None:
    source = next(item for item in load_monster_source_2014() if item.id == "roc")
    roc = compile_combatant(adapt_basic_monster_2014(source))
    assert roc.speed_ft == 120
    assert roc.movement_modes.walk_ft == 20
    assert roc.movement_modes.fly_ft == 120
    attacker = _member(roc, "monster", "monsters", 0, 6)
    target = _member(
        build_karnok_stoneward_2014(1).model_copy(update={"max_hp": 80}),
        "hero",
        "heroes",
        5,
        7,
    )
    target.state.resources = [
        item for item in target.state.resources if item.id != "relentless-endurance"
    ]
    begin_turn(attacker.state)
    setup = _mapped_setup(attacker, target)
    assert tightest_usable_melee_reach_ft(attacker, target) == 5
    events, _ = resolve_combat_turn(
        1, 1, attacker, target, setup, FixedDiceProvider([6] * 80),
    )
    attacks = [event for event in events if event.event_type == "attack"]
    names = [event.attack_name for event in attacks]
    assert "Beak" in names
    assert "Talons" in names
    assert not [event for event in events if event.feature_id == "dodge"]
