from app.combat.dice import FixedDiceProvider
from app.combat.legendary_actions import choose_legendary_attack, resolve_legendary_actions_after_turn
from app.combat.state import begin_turn, build_combatant_state
from app.content.arena_map import build_standard_iron_pit_map
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.grid import GridPosition
from app.domain.legendary_actions import LegendaryActionOption
from app.domain.models import (
    CombatantTemplate,
    ResourceDefinition,
    VisualLoadout,
    Weapon,
    WeaponAttack,
    WeaponAttackKind,
)
from app.domain.progression import ProgressionCombatFeatures


def _weapon(attack_id: str, name: str, dice_count: int, dice_size: int, reach: int = 5) -> WeaponAttack:
    return WeaponAttack(
        id=attack_id,
        weapon=Weapon(
            id=attack_id, name=name, attack_kind=WeaponAttackKind.MELEE,
            dice_count=dice_count, dice_size=dice_size, damage_type="bludgeoning",
            animation="slash", reach_ft=reach,
        ),
        attack_bonus=6, damage_bonus=4,
    )


def _monster(combatant_id: str, x: int = 5, y: int = 5) -> EncounterCombatant:
    tail = _weapon("tail", "Tail", 2, 8, 15)
    template = CombatantTemplate(
        id="test-legend", name="Test Legend", archetype="Test", kind="monster",
        armor_class=16, max_hp=80, speed_ft=40, initiative_bonus=2,
        weapon_attack=_weapon("bite", "Bite", 2, 10),
        alternate_weapon_attacks=[tail],
        visual=VisualLoadout(armor="scales", main_hand="bite", body_style="dragon"),
        source="test",
        resources=[ResourceDefinition(id="legendary-actions", name="Legendary Actions", max_uses=3)],
        legendary_actions=[
            LegendaryActionOption(id="tail-attack", name="Tail Attack", cost=1, kind="attack", attack_id="tail"),
        ],
        progression_features=ProgressionCombatFeatures(start_turn_resource_refill_ids=["legendary-actions"]),
        saving_throw_bonuses={
            "strength": 6, "dexterity": 2, "constitution": 5,
            "intelligence": 1, "wisdom": 2, "charisma": 3,
        },
    )
    member = EncounterCombatant(
        combatant_id=combatant_id, side="monsters", position_ft=x * 5,
        state=build_combatant_state(template),
    )
    member.state.position = GridPosition(x=x, y=y)
    return member


def _hero(combatant_id: str, x: int = 6, y: int = 5) -> EncounterCombatant:
    template = CombatantTemplate(
        id="test-hero", name="Test Hero", archetype="Test", kind="character",
        armor_class=10, max_hp=30, speed_ft=30, initiative_bonus=0,
        weapon_attack=_weapon("club", "Club", 1, 4),
        visual=VisualLoadout(armor="clothes", main_hand="club", body_style="humanoid"),
        source="test",
        saving_throw_bonuses={
            "strength": 0, "dexterity": 0, "constitution": 0,
            "intelligence": 0, "wisdom": 0, "charisma": 0,
        },
    )
    member = EncounterCombatant(
        combatant_id=combatant_id, side="heroes", position_ft=x * 5,
        state=build_combatant_state(template),
    )
    member.state.position = GridPosition(x=x, y=y)
    return member


def _setup(legend: EncounterCombatant, hero: EncounterCombatant) -> EncounterSetup:
    return EncounterSetup(
        heroes=[hero], monsters=[legend], hero_total_levels=1, monster_total_cr="10",
        ruleset="2014", map_definition=build_standard_iron_pit_map(),
    )


def test_legendary_action_spends_one_option_after_another_turn() -> None:
    legend = _monster("legend")
    hero = _hero("hero")
    setup = _setup(legend, hero)
    chosen = choose_legendary_attack(legend, setup)
    assert chosen is not None
    assert chosen[0].id == "tail-attack"
    events, _ = resolve_legendary_actions_after_turn(1, 1, hero, setup, FixedDiceProvider([20, *[8] * 12]))
    assert events
    assert "Legendary Action: Tail Attack" in events[0].description
    assert legend.state.resources[0].current_uses == 2
    assert hero.state.current_hp < hero.state.template.max_hp


def test_legendary_action_does_not_spend_when_nobody_is_in_reach() -> None:
    legend = _monster("legend", 1, 1)
    hero = _hero("hero", 12, 12)
    setup = _setup(legend, hero)
    assert choose_legendary_attack(legend, setup) is None
    events, _ = resolve_legendary_actions_after_turn(1, 1, hero, setup, FixedDiceProvider([20]))
    assert events == []
    assert legend.state.resources[0].current_uses == 3


def test_legendary_actions_refill_at_start_of_own_turn() -> None:
    legend = _monster("legend")
    legend.state.resources[0].current_uses = 1
    begin_turn(legend.state)
    assert legend.state.resources[0].current_uses == 3
