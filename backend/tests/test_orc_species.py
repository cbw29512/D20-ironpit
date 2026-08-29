from app.combat.dice import FixedDiceProvider
from app.combat.encounter_combat_turn import resolve_combat_turn
from app.combat.orc import (
    ADRENALINE_RESOURCE_ID,
    RELENTLESS_RESOURCE_ID,
    grant_temporary_hit_points,
    use_adrenaline_rush,
)
from app.combat.state import begin_turn, build_combatant_state
from app.combat.zero_hp import apply_damage
from app.content.demo import build_goblin_warrior
from app.content.pregens import build_brom_ironmark
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import ResourceDefinition
from app.domain.traits import CombatTrait


def _orc_fighter_state():
    template = build_brom_ironmark().model_copy(deep=True)
    template.combat_traits.extend([
        CombatTrait.ADRENALINE_RUSH,
        CombatTrait.RELENTLESS_ENDURANCE,
    ])
    template.resources.extend([
        ResourceDefinition(id=ADRENALINE_RESOURCE_ID, name="Adrenaline Rush", max_uses=2),
        ResourceDefinition(id=RELENTLESS_RESOURCE_ID, name="Relentless Endurance", max_uses=1),
    ])
    return build_combatant_state(template)


def test_adrenaline_rush_uses_bonus_action_dashes_and_grants_proficiency_temp_hp() -> None:
    state = _orc_fighter_state()
    begin_turn(state)

    event = use_adrenaline_rush(1, 1, state, "hero-1")

    assert event is not None
    assert state.bonus_action_available is False
    assert state.movement_remaining_ft == 60
    assert state.temporary_hp == 2
    resource = next(item for item in state.resources if item.id == ADRENALINE_RESOURCE_ID)
    assert resource.current_uses == 1


def test_adrenaline_rush_has_two_level_one_uses_and_does_not_stack_temp_hp() -> None:
    state = _orc_fighter_state()
    grant_temporary_hit_points(state, 5)

    for round_number in (1, 2):
        begin_turn(state)
        assert use_adrenaline_rush(round_number, round_number, state, "hero-1") is not None
        assert state.temporary_hp == 5

    begin_turn(state)
    assert use_adrenaline_rush(3, 3, state, "hero-1") is None


def test_temporary_hp_absorbs_damage_before_real_hp() -> None:
    state = _orc_fighter_state()
    grant_temporary_hit_points(state, 2)
    before = state.current_hp

    assert apply_damage(state, 5) == "damaged"
    assert state.temporary_hp == 0
    assert state.current_hp == before - 3


def test_relentless_endurance_drops_to_one_hp_once() -> None:
    state = _orc_fighter_state()

    assert apply_damage(state, state.current_hp) == "relentless_endurance"
    assert state.current_hp == 1
    assert state.is_unconscious is False
    resource = next(item for item in state.resources if item.id == RELENTLESS_RESOURCE_ID)
    assert resource.current_uses == 0

    assert apply_damage(state, 1) == "unconscious"
    assert state.current_hp == 0


def test_relentless_endurance_does_not_prevent_instant_death() -> None:
    state = _orc_fighter_state()
    damage = state.current_hp + state.template.max_hp

    assert apply_damage(state, damage) == "dead"
    resource = next(item for item in state.resources if item.id == RELENTLESS_RESOURCE_ID)
    assert resource.current_uses == 1


def test_canonical_turn_uses_adrenaline_rush_then_dodges_while_closing() -> None:
    hero = EncounterCombatant(
        combatant_id="hero-1:orc-fighter",
        side="heroes",
        position_ft=0,
        state=_orc_fighter_state(),
    )
    monster = EncounterCombatant(
        combatant_id="monster-1:goblin",
        side="monsters",
        position_ft=60,
        state=build_combatant_state(build_goblin_warrior()),
    )
    setup = EncounterSetup(
        heroes=[hero],
        monsters=[monster],
        hero_total_levels=1,
        monster_total_cr="1/4",
        starting_distance_ft=60,
    )

    events, _ = resolve_combat_turn(
        1, 1, hero, monster, setup, FixedDiceProvider([15, 6])
    )

    assert any(event.feature_id == ADRENALINE_RESOURCE_ID for event in events)
    assert any(event.feature_id == "dodge" for event in events)
    assert not any(event.event_type == "attack" for event in events)
    assert hero.position_ft == 55
    assert hero.state.temporary_hp == 2
