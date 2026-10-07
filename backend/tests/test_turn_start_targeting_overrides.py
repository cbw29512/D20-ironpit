from app.combat.dice import FixedDiceProvider
from app.combat.encounter_targeting import select_nearest_target
from app.combat.start_turn import begin_turn_with_events
from app.combat.state import build_combatant_state
from app.combat.zero_hp import restore_hit_points
from app.content.monster_source_2014 import load_monster_source_2014
from app.content.monster_targeting_overrides_2014 import turn_start_targeting_overrides_2014
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import CombatantTemplate, VisualLoadout, Weapon, WeaponAttack, WeaponAttackKind
from app.domain.targeting_overrides import TurnStartTargetingOverrideRule


def _template(name: str = "Test Golem") -> CombatantTemplate:
    weapon = Weapon(
        id="slam", name="Slam", attack_kind=WeaponAttackKind.MELEE,
        dice_count=1, dice_size=6, damage_type="bludgeoning", animation="melee",
    )
    return CombatantTemplate(
        id=name.casefold().replace(" ", "-"), name=name, archetype="Test",
        kind="monster", armor_class=10, max_hp=100, speed_ft=30, initiative_bonus=0,
        weapon_attack=WeaponAttack(id="slam", weapon=weapon, attack_bonus=5, damage_bonus=3),
        turn_start_targeting_overrides=[TurnStartTargetingOverrideRule(
            source_id="test-berserk", source_name="Berserk", max_current_hp=40,
            die_size=6, minimum_roll=6, target_mode="nearest_visible_creature",
        )],
        visual=VisualLoadout(armor="none", main_hand="slam"), source="test",
    )


def _member(combatant_id: str, side: str, position_ft: int, template=None) -> EncounterCombatant:
    state = build_combatant_state(template or _template(combatant_id))
    return EncounterCombatant(
        combatant_id=combatant_id, side=side, position_ft=position_ft, state=state,
    )


def test_2014_golem_berserk_core_extracts_source_thresholds() -> None:
    monsters = {monster.id: monster for monster in load_monster_source_2014()}
    flesh = turn_start_targeting_overrides_2014(monsters["flesh-golem"])[0]
    clay = turn_start_targeting_overrides_2014(monsters["clay-golem"])[0]

    assert flesh.source_name == clay.source_name == "Berserk"
    assert flesh.max_current_hp == 40
    assert clay.max_current_hp == 60
    assert flesh.minimum_roll == clay.minimum_roll == 6
    assert flesh.target_mode == clay.target_mode == "nearest_visible_creature"


def test_turn_start_roll_activates_once_and_full_hp_healing_ends_override() -> None:
    state = build_combatant_state(_template())
    state.current_hp = 40

    events, sequence = begin_turn_with_events(3, 2, "golem", state, FixedDiceProvider([6]))
    assert sequence == 4
    assert events[0].feature_id == "test-berserk"
    assert events[0].feature_roll.total == 6
    assert state.active_targeting_override_ids == ["test-berserk"]

    events, sequence = begin_turn_with_events(4, 3, "golem", state, FixedDiceProvider([1]))
    assert events == []
    assert sequence == 4

    state.current_hp = 99
    assert restore_hit_points(state, 1) == 1
    assert state.active_targeting_override_ids == []


def test_failed_turn_start_roll_does_not_activate_override() -> None:
    state = build_combatant_state(_template())
    state.current_hp = 40
    events, _ = begin_turn_with_events(1, 1, "golem", state, FixedDiceProvider([5]))

    assert events[0].feature_roll.total == 5
    assert state.active_targeting_override_ids == []


def test_active_override_targets_nearest_visible_creature_even_when_ally() -> None:
    golem = _member("golem", "monsters", 0)
    ally = _member("ally", "monsters", 5)
    enemy = _member("enemy", "heroes", 20)
    setup = EncounterSetup(heroes=[enemy], monsters=[golem, ally])
    golem.state.active_targeting_override_ids = ["test-berserk"]

    assert select_nearest_target(golem, setup) is ally

    ally.state.active_effect_ids.append("invisible")
    assert select_nearest_target(golem, setup) is enemy
