from __future__ import annotations

from app.combat.initiative_resource_refill import resolve_initiative_resource_refills
from app.combat.state import build_combatant_state
from app.content.bard_lore_2014_profile import build_lyra_silverstring_2014_profile
from app.content.bard_lore_2014_runtime import build_lyra_silverstring_2014
from app.domain.encounters import EncounterCombatant, EncounterSetup


def test_level_nineteen_asi_persists_into_runtime_math() -> None:
    profile = build_lyra_silverstring_2014_profile(19)
    hero = build_lyra_silverstring_2014(19)

    assert profile.final_ability_scores.constitution == 13
    assert hero.ability_scores == profile.final_ability_scores
    assert hero.max_hp > build_lyra_silverstring_2014(18).max_hp


def test_level_twenty_superior_inspiration_refills_one_empty_use() -> None:
    hero = build_lyra_silverstring_2014(20)
    member = EncounterCombatant(
        combatant_id="lyra",
        side="heroes",
        position_ft=0,
        state=build_combatant_state(hero),
    )
    resource = next(item for item in member.state.resources if item.id == "bardic-inspiration")
    resource.current_uses = 0
    setup = EncounterSetup(
        heroes=[member],
        monsters=[],
        hero_total_levels=20,
        monster_total_cr="0",
        ruleset="2014",
    )

    events, sequence = resolve_initiative_resource_refills(1, setup)

    assert sequence == 2
    assert resource.current_uses == 1
    assert len(events) == 1
    assert events[0].feature_id == "superior-inspiration"
    assert events[0].resource_remaining == 1


def test_level_twenty_superior_inspiration_does_not_refill_nonempty_resource() -> None:
    hero = build_lyra_silverstring_2014(20)
    member = EncounterCombatant(
        combatant_id="lyra",
        side="heroes",
        position_ft=0,
        state=build_combatant_state(hero),
    )
    resource = next(item for item in member.state.resources if item.id == "bardic-inspiration")
    resource.current_uses = 1
    setup = EncounterSetup(
        heroes=[member],
        monsters=[],
        hero_total_levels=20,
        monster_total_cr="0",
        ruleset="2014",
    )

    events, sequence = resolve_initiative_resource_refills(1, setup)

    assert sequence == 1
    assert resource.current_uses == 1
    assert events == []
