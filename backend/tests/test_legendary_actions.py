from app.combat.dice import FixedDiceProvider
from app.combat.legendary_action_choice import choose_legendary_action, choose_legendary_attack
from app.combat.legendary_actions import resolve_legendary_actions_after_turn
from app.combat.state import begin_turn, build_combatant_state
from app.content.arena_map import build_standard_iron_pit_map
from app.domain.actions import SavingThrowAction
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.grid import GridPosition
from app.domain.legendary_actions import LegendaryAcBuffSpec, LegendaryActionOption, LegendaryHealSpec
from app.domain.models import (
    CombatantTemplate,
    ResourceDefinition,
    VisualLoadout,
    Weapon,
    WeaponAttack,
    WeaponAttackKind,
)
from app.domain.progression import ProgressionCombatFeatures
from app.domain.save_effects import FailedSaveTimedEffect
from app.domain.targeting import AreaTargeting


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


def _wing_save(*, dc: int = 19, bonus: int = 6, push_ft: int = 0) -> SavingThrowAction:
    return SavingThrowAction(
        id="legendary-wing-attack",
        name="Wing Attack",
        save_ability="dexterity",
        dc=dc,
        range_ft=10,
        max_targets=20,
        area=AreaTargeting(shape="emanation", origin="self", radius_ft=10),
        damage_dice_count=2,
        damage_dice_size=6,
        damage_bonus=bonus,
        damage_type="bludgeoning",
        success_damage="none",
        failed_save_timed_effect=FailedSaveTimedEffect(effect_id="prone"),
        failed_save_push_ft=push_ft,
        animation="wing-attack",
    )


def _monster(combatant_id: str, x: int = 5, y: int = 5, *, with_wing: bool = False, push_ft: int = 0) -> EncounterCombatant:
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
            *(
                [LegendaryActionOption(
                    id="wing-attack", name="Wing Attack", cost=2, kind="save",
                    save_action=_wing_save(push_ft=push_ft),
                )]
                if with_wing else []
            ),
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


def test_wing_attack_save_knocks_prone_without_flying() -> None:
    legend = _monster("legend", with_wing=True)
    legend.state.template.legendary_actions = [
        item for item in legend.state.template.legendary_actions if item.kind == "save"
    ]
    hero = _hero("hero")
    setup = _setup(legend, hero)
    start = (legend.state.position.x, legend.state.position.y)
    choice = choose_legendary_action(legend, setup)
    assert choice is not None and choice[0] == "save"
    assert choice[1][0].id == "wing-attack"
    events, _ = resolve_legendary_actions_after_turn(
        1, 1, hero, setup, FixedDiceProvider([6, 6, 1]),
    )
    assert events
    assert "Legendary Action: Wing Attack" in events[0].description
    assert events[0].save_succeeded is False
    assert "prone" in hero.state.active_effect_ids
    assert hero.state.current_hp < hero.state.template.max_hp
    assert (legend.state.position.x, legend.state.position.y) == start
    assert legend.state.resources[0].current_uses == 1


def test_wing_attack_success_deals_no_damage_and_no_prone() -> None:
    legend = _monster("legend", 5, 5, with_wing=True)
    legend.state.template.legendary_actions = [
        item for item in legend.state.template.legendary_actions if item.kind == "save"
    ]
    hero = _hero("hero")
    setup = _setup(legend, hero)
    events, _ = resolve_legendary_actions_after_turn(
        1, 1, hero, setup, FixedDiceProvider([6, 6, 20]),
    )
    assert events
    assert events[0].save_succeeded is True
    assert "prone" not in hero.state.active_effect_ids
    assert hero.state.current_hp == hero.state.template.max_hp


def test_wing_attack_push_applies_when_printed() -> None:
    legend = _monster("legend", 5, 5, with_wing=True, push_ft=10)
    legend.state.template.legendary_actions = [
        item for item in legend.state.template.legendary_actions if item.kind == "save"
    ]
    hero = _hero("hero", 6, 5)
    setup = _setup(legend, hero)
    start = hero.state.position.x
    events, _ = resolve_legendary_actions_after_turn(
        1, 1, hero, setup, FixedDiceProvider([6, 6, 1]),
    )
    assert events
    assert events[0].save_succeeded is False
    assert hero.state.position.x != start or hero.state.position.y != 5
    assert "prone" in hero.state.active_effect_ids


def test_legendary_save_loses_to_higher_damage_attack() -> None:
    legend = _monster("legend", with_wing=True)
    hero = _hero("hero")
    setup = _setup(legend, hero)
    choice = choose_legendary_action(legend, setup)
    assert choice is not None and choice[0] == "attack"
    assert choice[1][0].id == "tail-attack"


def test_legendary_ac_buff_fires_when_no_attack_is_in_reach() -> None:
    legend = _monster("legend")
    legend.state.template.legendary_actions = [
        LegendaryActionOption(
            id="shimmering-shield", name="Shimmering Shield", cost=2, kind="ac_buff",
            ac_buff=LegendaryAcBuffSpec(ac_bonus=2, range_ft=60),
        ),
    ]
    hero = _hero("hero", x=12)
    setup = _setup(legend, hero)
    events, _ = resolve_legendary_actions_after_turn(1, 1, hero, setup, FixedDiceProvider([20]))
    assert events
    assert "Legendary Action: Shimmering Shield" in events[0].description
    assert legend.state.resources[0].current_uses == 1
    assert any(item.kind.value == "armor-class" and item.flat_bonus == 2 for item in legend.state.active_modifiers)


def test_legendary_heal_fires_when_damaged_and_no_attack_is_in_reach() -> None:
    legend = _monster("legend")
    legend.state.current_hp = 40
    legend.state.template.legendary_actions = [
        LegendaryActionOption(
            id="heal-self", name="Heal Self", cost=3, kind="heal",
            heal=LegendaryHealSpec(dice_count=2, dice_size=8, healing_bonus=2),
        ),
    ]
    hero = _hero("hero", x=12)
    setup = _setup(legend, hero)
    events, _ = resolve_legendary_actions_after_turn(1, 1, hero, setup, FixedDiceProvider([6, 6]))
    assert events
    assert "Legendary Action: Heal Self" in events[0].description
    assert legend.state.current_hp == 54
    assert legend.state.resources[0].current_uses == 0

