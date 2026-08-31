from app.combat.dice import FixedDiceProvider
from app.combat.encounter_setup import build_encounter_setup
from app.combat.opportunity_attacks import resolve_opportunity_attack
from app.combat.state import begin_turn
from app.content.roster import build_arena_roster
from app.domain.models import EncounterSelection, WeaponAttackKind


def _setup(monster_id: str = "srd-commoner"):
    setup = build_encounter_setup(EncounterSelection(
        hero_ids=["karnok-stoneward-l1"], monster_ids=[monster_id], starting_distance_ft=5,
    ))
    return setup, setup.monsters[0], setup.heroes[0]


def test_opportunity_attack_spends_reaction_not_action_and_only_once() -> None:
    setup, reactor, mover = _setup()
    event = resolve_opportunity_attack(
        1, 1, reactor, mover, setup, 5, 10, "speed", FixedDiceProvider([19, 1]),
    )
    assert event is not None
    assert event.feature_id == "opportunity-attack"
    assert event.event_type == "attack"
    assert reactor.state.reaction_available is False
    assert reactor.state.action_available is True
    assert resolve_opportunity_attack(
        2, 1, reactor, mover, setup, 5, 10, "speed", FixedDiceProvider([19])
    ) is None

    begin_turn(reactor.state)
    assert reactor.state.reaction_available is True


def test_disengage_teleport_and_forced_movement_do_not_provoke() -> None:
    for source, disengaged in (("speed", True), ("teleport", False), ("forced", False)):
        setup, reactor, mover = _setup()
        event = resolve_opportunity_attack(
            1, 1, reactor, mover, setup, 5, 10, source, FixedDiceProvider([19]), disengaged=disengaged,
        )
        assert event is None
        assert reactor.state.reaction_available is True


def test_incapacitated_or_blinded_reactor_cannot_make_opportunity_attack() -> None:
    for condition in ("stunned", "blinded"):
        setup, reactor, mover = _setup()
        reactor.state.active_effect_ids.append(condition)
        assert resolve_opportunity_attack(
            1, 1, reactor, mover, setup, 5, 10, "speed", FixedDiceProvider([19])
        ) is None
        assert reactor.state.reaction_available is True


def test_reach_is_left_before_opportunity_attack_triggers() -> None:
    setup, reactor, mover = _setup("srd-plesiosaurus")
    assert reactor.state.template.weapon_attack.weapon.reach_ft == 10
    assert resolve_opportunity_attack(
        1, 1, reactor, mover, setup, 5, 10, "speed", FixedDiceProvider([19])
    ) is None
    event = resolve_opportunity_attack(
        1, 1, reactor, mover, setup, 10, 15, "speed", FixedDiceProvider([19, 1, 1]),
    )
    assert event is not None
    assert event.feature_id == "opportunity-attack"


def test_action_bonus_action_and_reaction_movement_sources_can_provoke() -> None:
    for source in ("action", "bonus_action", "reaction"):
        setup, reactor, mover = _setup()
        event = resolve_opportunity_attack(
            1, 1, reactor, mover, setup, 5, 10, source, FixedDiceProvider([19, 1]),
        )
        assert event is not None


def test_every_runtime_combatant_has_a_modeled_melee_opportunity_attack() -> None:
    roster = build_arena_roster()
    missing: list[str] = []
    for template in [*roster.characters, *roster.monsters]:
        attacks = [template.weapon_attack, *template.alternate_weapon_attacks]
        if not any(attack.weapon.attack_kind is WeaponAttackKind.MELEE for attack in attacks):
            missing.append(template.name)
    assert missing == [], f"Runtime combatants require Unarmed Strike OA support: {missing}"
