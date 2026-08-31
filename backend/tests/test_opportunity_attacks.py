from app.combat.dice import FixedDiceProvider
from app.combat.encounter_setup import build_encounter_setup
from app.combat.opportunity_attacks import resolve_opportunity_attack
from app.combat.state import begin_turn
from app.content.roster import build_arena_roster
from app.domain.models import EncounterSelection


def _setup(monster_id: str = "srd-commoner", hero_id: str = "karnok-stoneward-l1"):
    setup = build_encounter_setup(EncounterSelection(
        hero_ids=[hero_id], monster_ids=[monster_id],
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


def test_reach_weapon_and_unarmed_strike_use_their_actual_boundaries() -> None:
    setup, reactor, mover = _setup("srd-plesiosaurus")
    assert reactor.state.template.weapon_attack.weapon.reach_ft == 10
    unarmed = resolve_opportunity_attack(
        1, 1, reactor, mover, setup, 5, 10, "speed", FixedDiceProvider([19]),
    )
    assert unarmed is not None and unarmed.weapon_id == "unarmed-strike"

    begin_turn(reactor.state)
    weapon = resolve_opportunity_attack(
        2, 1, reactor, mover, setup, 10, 15, "speed", FixedDiceProvider([19, 1, 1]),
    )
    assert weapon is not None and weapon.weapon_id == reactor.state.template.weapon_attack.weapon.id


def test_selene_uses_certified_unarmed_strike_for_opportunity_attack() -> None:
    setup, mover, selene = _setup(hero_id="selene-asharrow-l1")
    profile = selene.state.template.unarmed_opportunity_attack
    assert profile is not None and (profile.attack_bonus, profile.damage) == (3, 2)
    hp_before = mover.state.current_hp
    event = resolve_opportunity_attack(
        1, 1, selene, mover, setup, 5, 10, "speed", FixedDiceProvider([19]),
    )
    assert event is not None
    assert event.weapon_id == "unarmed-strike"
    assert event.hit is True and event.damage_roll is not None and event.damage_roll.total == 2
    assert mover.state.current_hp == hp_before - 2


def test_action_bonus_action_and_reaction_movement_sources_can_provoke() -> None:
    for source in ("action", "bonus_action", "reaction"):
        setup, reactor, mover = _setup()
        event = resolve_opportunity_attack(
            1, 1, reactor, mover, setup, 5, 10, source, FixedDiceProvider([19, 1]),
        )
        assert event is not None


def test_every_runtime_combatant_has_certified_unarmed_opportunity_profile() -> None:
    roster = build_arena_roster()
    missing = [
        template.name for template in [*roster.characters, *roster.monsters]
        if template.unarmed_opportunity_attack is None
    ]
    assert missing == []
