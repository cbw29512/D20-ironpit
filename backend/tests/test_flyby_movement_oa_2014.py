from app.combat.dice import FixedDiceProvider
from app.combat.encounter_setup import build_encounter_setup
from app.combat.modifier_stack import effective_speed
from app.combat.opportunity_attacks import resolve_opportunity_attack
from app.combat.state import begin_turn, build_combatant_state
from app.content.capability_compiler import compile_combatant
from app.content.monster_definition_adapter_2014 import adapt_basic_monster_2014
from app.content.monster_source_2014 import load_monster_source_2014
from app.content.movement_mode_oa_exemption import exempt_movement_modes_from_trait_text
from app.domain.encounters import EncounterCombatant, EncounterSelection

FLYBY_IDS = ("flying-snake", "giant-owl", "owl", "pteranodon")
PRINTED_FLY_EXEMPTION_TEXTS = {
    "flying-snake": (
        "<p><em><strong>Flyby.</strong></em> The snake doesn't provoke opportunity "
        "attacks when it flies out of an enemy's reach.</p>"
    ),
    "giant-owl": (
        "<p><em><strong>Flyby.</strong></em> The owl doesn't provoke opportunity "
        "attacks when it flies out of an enemy's reach. </p>"
    ),
    "owl": (
        "<p><em><strong>Flyby.</strong></em> The owl doesn't provoke opportunity "
        "attacks when it flies out of an enemy's reach. </p>"
    ),
    "pteranodon": (
        "<div><p><em><strong>Flyby.</strong></em> The pteranodon doesn’t provoke an "
        "opportunity attack when it flies out of an enemy’s reach.</p></div>"
    ),
}


def _source(monster_id: str):
    return next(monster for monster in load_monster_source_2014() if monster.id == monster_id)


def _compiled(monster_id: str):
    return compile_combatant(adapt_basic_monster_2014(_source(monster_id)))


def _flyby_setup(monster_id: str, *, movement_mode: str):
    setup = build_encounter_setup(EncounterSelection(
        hero_ids=["karnok-stoneward-l1"], monster_ids=["srd-commoner"],
    ))
    reactor = setup.heroes[0]
    template = _compiled(monster_id)
    mover = EncounterCombatant(
        combatant_id=f"monster-1:{template.id}",
        side="monsters",
        position_ft=0,
        state=build_combatant_state(template),
    )
    setup.monsters[0] = mover
    begin_turn(mover.state)
    mover.state.active_movement_mode = movement_mode
    begin_turn(reactor.state)
    return setup, reactor, mover


def test_printed_2014_fly_out_of_reach_text_binds_fly_not_the_heading() -> None:
    for monster_id, text in PRINTED_FLY_EXEMPTION_TEXTS.items():
        source = _source(monster_id)
        assert source.source_traits is not None
        assert text[:40] in source.source_traits or text in source.source_traits
        assert exempt_movement_modes_from_trait_text(source.source_traits) == ("fly",)
        assert exempt_movement_modes_from_trait_text(text) == ("fly",)
    assert exempt_movement_modes_from_trait_text("<p><em><strong>Flyby.</strong></em></p>") == ()
    assert exempt_movement_modes_from_trait_text(
        "The creature doesn't provoke opportunity attacks when it swims out of an enemy's reach."
    ) == ("swim",)


def test_compiled_2014_flyby_creatures_bind_fly_exemption_from_source_text() -> None:
    for monster_id in FLYBY_IDS:
        template = _compiled(monster_id)
        assert template.opportunity_attack_exempt_movement_modes == ["fly"]
        assert template.movement_modes.fly_ft == 60
        assert template.speed_ft == template.movement_modes.walk_ft


def test_horizontal_fly_is_the_default_mode_and_uses_printed_fly_speed() -> None:
    expected_walk = {"flying-snake": 30, "giant-owl": 5, "owl": 5, "pteranodon": 10}
    for monster_id, walk_ft in expected_walk.items():
        state = build_combatant_state(_compiled(monster_id))
        begin_turn(state)
        assert state.active_movement_mode == "fly"
        assert effective_speed(state) == 60
        assert state.movement_remaining_ft == 60
        state.active_movement_mode = "walk"
        assert effective_speed(state) == walk_ft


def test_fly_movement_does_not_provoke_and_walk_still_does() -> None:
    for monster_id in FLYBY_IDS:
        setup, reactor, mover = _flyby_setup(monster_id, movement_mode="fly")
        assert resolve_opportunity_attack(
            1, 1, reactor, mover, setup, 5, 10, "speed", FixedDiceProvider([19]),
        ) is None
        assert reactor.state.reaction_available is True

        setup, reactor, mover = _flyby_setup(monster_id, movement_mode="walk")
        event = resolve_opportunity_attack(
            1, 1, reactor, mover, setup, 5, 10, "speed", FixedDiceProvider([19, 1]),
        )
        assert event is not None
        assert event.feature_id == "opportunity-attack"
        assert reactor.state.reaction_available is False
