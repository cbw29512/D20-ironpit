"""Permanent environment passives stay on source cards despite absent terrain.

A missing water context cannot become blanket cold vulnerability or erase
Fire Elemental's still-unimplemented water-exposure trigger.
"""
from __future__ import annotations

from app.content.monster_arena_neutral_traits_2014 import ARENA_NEUTRAL_TRAITS_2014
from app.content.monster_basic_candidates_2014 import unsupported_traits_2014
from app.content.monster_source_2014 import load_monster_source_2014
from app.content.monster_source_sections_2014 import source_sections_2014


def _monster(monster_id: str):
    return next(m for m in load_monster_source_2014() if m.id == monster_id)


def test_fire_water_weakness_is_printed_permanently_not_vulnerability() -> None:
    monster = _monster("fire-elemental")
    assert "Water Susceptibility" in monster.trait_names
    assert "Water Susceptibility" not in ARENA_NEUTRAL_TRAITS_2014
    clause = source_sections_2014(monster.source_traits)["Water Susceptibility"].casefold()
    assert all(term in clause for term in (
        "moves in water", "gallon of water", "1 cold damage",
    ))
    assert "cold" not in {item.casefold() for item in monster.damage_vulnerabilities}
    # The exact cold-damage exposure trigger is not yet runnable. Keep the
    # obligation visible until a typed environmental exposure resolver exists.
    assert "Water Susceptibility" not in unsupported_traits_2014(monster)



def test_2014_environment_inert_trait_proof_fails_closed_on_source_mutation() -> None:
    import logging
    from app.content.monster_arena_inactive_environment_2014 import (
        arena_inactive_environment_traits_2014,
    )
    from app.content.monster_basic_candidates_2014 import basic_blockers_2014

    log = logging.getLogger(__name__)
    try:
        monster = _monster("fire-elemental")
        accepted = arena_inactive_environment_traits_2014(monster)
        assert accepted == frozenset({"Fire Form", "Water Susceptibility"})
        assert not basic_blockers_2014(monster)
        renamed = monster.model_copy(update={"id": "renamed-element", "name": "Renamed Element"})
        assert arena_inactive_environment_traits_2014(renamed) == accepted

        for before, after in (
            ("every 5 feet", "every 10 feet"),
            ("every gallon of water", "every 2 gallons of water"),
            ("1 cold damage", "2 cold damage"),
        ):
            mutant = monster.model_copy(update={
                "source_traits": monster.source_traits.replace(before, after),
            })
            assert mutant.source_traits != monster.source_traits
            assert "Water Susceptibility" not in arena_inactive_environment_traits_2014(mutant)
            assert "source:trait" in basic_blockers_2014(mutant)
    except Exception:
        log.exception("Source-verified inactive environmental trait regression failed.")
        raise


def test_shadow_sunlight_weakness_stays_in_source_without_live_sunlight() -> None:
    from app.content.environment_context_reactions import (
        verified_sunlight_weakness_2014,
    )
    from app.content.monster_environment_context_bindings_2014 import (
        environment_context_reactions_2014,
    )
    monster = _monster("shadow")
    assert "Sunlight Weakness" in monster.trait_names
    assert "Sunlight Weakness" not in ARENA_NEUTRAL_TRAITS_2014
    assert verified_sunlight_weakness_2014(monster)
    reactions = environment_context_reactions_2014(monster)
    assert len(reactions) == 1
    assert reactions[0].source_name == "Sunlight Weakness"
    assert reactions[0].context_id == "sunlight"
    assert set(reactions[0].disadvantage_on) == {
        "attack_rolls", "ability_checks", "saving_throws",
    }
