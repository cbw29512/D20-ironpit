"""Either Iron Pit team accepts certified pregens and monsters without edition mixing."""

from app.combat.encounter_setup import build_encounter_setup
from app.combat.encounter_engine import run_encounter
from app.domain.encounters import EncounterSelection


class MaxDice:
    def roll(self, sides: int) -> int:
        return sides


def test_each_team_can_mix_pregens_and_monsters() -> None:
    setup = build_encounter_setup(EncounterSelection(
        ruleset="2024",
        hero_ids=["karnok-stoneward-l1", "srd-wolf"],
        monster_ids=["srd-commoner", "seraphine-dawnshield-l1"],
    ))
    assert [m.state.template.kind for m in setup.heroes] == ["character", "monster"]
    assert [m.state.template.kind for m in setup.monsters] == ["monster", "character"]
    assert setup.hero_total_levels == 1
    assert setup.monster_total_cr == "0"
    assert len({(m.state.position.x, m.state.position.y) for m in
        [*setup.heroes, *setup.monsters]}) == 4


def test_six_monsters_can_be_team_a_and_pregens_can_be_team_b() -> None:
    setup = build_encounter_setup(EncounterSelection(
        ruleset="2024",
        hero_ids=["srd-commoner"] * 6,
        monster_ids=["karnok-stoneward-l1"] * 6,
    ))
    assert setup.hero_total_levels == 0
    assert setup.monster_total_cr == "0"
    assert all(m.state.template.kind == "monster" for m in setup.heroes)
    assert all(m.state.template.kind == "character" for m in setup.monsters)


def test_monster_versus_monster_runs_real_combat() -> None:
    result = run_encounter(EncounterSelection(
        ruleset="2024", hero_ids=["srd-commoner"],
        monster_ids=["srd-commoner"],
    ), MaxDice())
    assert result.outcome in ("heroes_win", "monsters_win", "draw")
    assert any(event.event_type == "attack" for event in result.events)
    assert result.setup.hero_total_levels == 0
