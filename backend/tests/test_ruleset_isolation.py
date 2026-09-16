import pytest

from app.combat.encounter_ruleset import resolve_encounter_ruleset
from app.combat.encounter_setup import build_encounter_setup
from app.content.audited_fighter import build_karnok_stoneward
from app.content.demo import build_goblin_warrior
from app.content.roster import build_arena_roster
from app.domain.encounters import EncounterSelection


def test_current_canonical_encounter_is_explicitly_2024() -> None:
    setup = build_encounter_setup(EncounterSelection(
        hero_ids=["karnok-stoneward-l1"],
        monster_ids=["srd-commoner"],
    ))
    assert setup.ruleset == "2024"
    assert setup.heroes[0].state.template.ruleset == "2024"
    assert setup.monsters[0].state.template.ruleset == "2024"


def test_current_canonical_roster_is_entirely_2024() -> None:
    roster = build_arena_roster()
    templates = [*roster.characters, *roster.monsters]
    assert templates
    assert {template.ruleset for template in templates} == {"2024"}


def test_mixed_rulesets_fail_closed_before_combat() -> None:
    hero = build_karnok_stoneward()
    monster_2014 = build_goblin_warrior().model_copy(update={"ruleset": "2014"})
    with pytest.raises(ValueError, match="Mixed rulesets are not allowed"):
        resolve_encounter_ruleset([hero, monster_2014])


def test_single_2014_ruleset_resolves_without_cross_edition_data() -> None:
    hero_2014 = build_karnok_stoneward().model_copy(update={"ruleset": "2014"})
    monster_2014 = build_goblin_warrior().model_copy(update={"ruleset": "2014"})
    assert resolve_encounter_ruleset([hero_2014, monster_2014]) == "2014"
