import pytest

from app.combat.attacks import resolve_attack
from app.combat.dice import FixedDiceProvider
from app.combat.initiative import roll_initiative_order
from app.combat.targeting import select_nearest_enemy
from app.domain.encounters import EncounterParticipantRequest, EncounterRequest, distance_between
from app.services.encounters import EncounterValidationError, build_encounter_state


def _party_vs_boss_request() -> EncounterRequest:
    return EncounterRequest(participants=[
        EncounterParticipantRequest(
            instance_id="aldric-1",
            combatant_id="aldric-vane-l1",
            side_id="party",
            starting_position_ft=0,
        ),
        EncounterParticipantRequest(
            instance_id="aldric-2",
            combatant_id="aldric-vane-l1",
            side_id="party",
            starting_position_ft=5,
        ),
        EncounterParticipantRequest(
            instance_id="ogre-1",
            combatant_id="srd-ogre",
            side_id="monsters",
            starting_position_ft=40,
        ),
    ])


def test_encounter_allows_duplicate_templates_with_unique_instances() -> None:
    encounter = build_encounter_state(_party_vs_boss_request())

    assert [item.combatant.instance_id for item in encounter.participants] == [
        "aldric-1", "aldric-2", "ogre-1"
    ]
    assert encounter.participants[0].combatant.template.id == "aldric-vane-l1"
    assert encounter.participants[1].combatant.template.id == "aldric-vane-l1"
    assert distance_between(encounter.participants[0], encounter.participants[2]) == 40
    assert len(encounter.enemies_of(encounter.participants[0])) == 1


def test_encounter_rejects_duplicate_runtime_instance_ids() -> None:
    request = _party_vs_boss_request()
    request.participants[1].instance_id = "aldric-1"

    with pytest.raises(EncounterValidationError, match="unique"):
        build_encounter_state(request)


def test_encounter_requires_opposing_sides() -> None:
    request = _party_vs_boss_request()
    request.participants[2].side_id = "party"

    with pytest.raises(EncounterValidationError, match="two opposing sides"):
        build_encounter_state(request)


def test_initiative_orders_arbitrary_roster_and_keeps_instance_ids() -> None:
    encounter = build_encounter_state(_party_vs_boss_request())
    states = [item.combatant for item in encounter.participants]

    events, order, sequence = roll_initiative_order(
        7, states, FixedDiceProvider([10, 14, 12])
    )

    assert [event.actor_id for event in events] == ["aldric-1", "aldric-2", "ogre-1"]
    assert [state.instance_id for state in order] == ["aldric-2", "aldric-1", "ogre-1"]
    assert sequence == 10


def test_exact_initiative_tie_uses_stable_instance_id_policy() -> None:
    encounter = build_encounter_state(_party_vs_boss_request())
    states = [item.combatant for item in encounter.participants[:2]]

    _, order, _ = roll_initiative_order(1, states, FixedDiceProvider([10, 10]))

    assert [state.instance_id for state in order] == ["aldric-1", "aldric-2"]


def test_target_policy_selects_nearest_living_enemy() -> None:
    encounter = build_encounter_state(_party_vs_boss_request())
    actor = encounter.participants[2]

    target = select_nearest_enemy(encounter, actor)

    assert target is not None
    assert target.combatant.instance_id == "aldric-2"
    target.combatant.is_alive = False
    assert select_nearest_enemy(encounter, actor).combatant.instance_id == "aldric-1"


def test_attack_events_identify_runtime_instances_not_templates() -> None:
    encounter = build_encounter_state(_party_vs_boss_request())
    attacker = encounter.participants[0].combatant
    defender = encounter.participants[2].combatant

    event = resolve_attack(
        1,
        1,
        attacker,
        defender,
        attacker.template.weapon_attack,
        5,
        FixedDiceProvider([15, 1]),
    )

    assert event.actor_id == "aldric-1"
    assert event.target_id == "ogre-1"
    assert attacker.template.id == "aldric-vane-l1"
    assert defender.template.id == "srd-ogre"
