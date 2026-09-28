from __future__ import annotations

from app.combat.dice import FixedDiceProvider
from app.combat.spell_damage_maximizers import (
    maximized_save_damage_rolls,
    resolve_maximizer_after_cast,
    safe_maximizer_for_spell,
)
from app.combat.state import build_combatant_state
from app.content.wizard_evoker_2014_runtime import build_elian_starweaver_2014
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import DamageType


def _setup() -> tuple[EncounterCombatant, EncounterSetup]:
    hero = EncounterCombatant(
        combatant_id="hero-1:elian-starweaver-2014-l14",
        side="heroes",
        position_ft=0,
        state=build_combatant_state(build_elian_starweaver_2014(14)),
    )
    enemy = EncounterCombatant(
        combatant_id="monster-1:test-target",
        side="monsters",
        position_ft=30,
        state=build_combatant_state(build_elian_starweaver_2014(1)),
    )
    setup = EncounterSetup(
        heroes=[hero], monsters=[enemy],
        hero_total_levels=14, monster_total_cr="0", ruleset="2014",
    )
    return hero, setup


def test_overchannel_maximizes_damage_then_escalates_unresistable_self_damage() -> None:
    hero, setup = _setup()
    grant = hero.state.template.progression_features.spell_damage_maximizer
    assert grant is not None
    fireball = next(item for item in hero.state.template.spell_save_actions if item.id == "fireball")

    assert maximized_save_damage_rolls(fireball) == [6] * 8
    assert safe_maximizer_for_spell(hero, "fireball", 3) == grant

    events, sequence = resolve_maximizer_after_cast(
        10, 1, hero, setup, grant, 3, FixedDiceProvider([1]),
    )
    assert events == []
    assert sequence == 10
    assert hero.state.feature_use_counts["overchannel"] == 1
    assert safe_maximizer_for_spell(hero, "fireball", 3) is None

    hero.state.template = hero.state.template.model_copy(
        update={"damage_immunities": [DamageType.NECROTIC]},
    )
    hp_before = hero.state.current_hp
    events, sequence = resolve_maximizer_after_cast(
        10, 1, hero, setup, grant, 3, FixedDiceProvider([1] * 6),
    )
    assert sequence == 11
    assert events[0].damage_roll is not None
    assert events[0].damage_roll.notation == "6d12"
    assert hero.state.current_hp == hp_before - 6
    assert hero.state.feature_use_counts["overchannel"] == 2

    hp_before = hero.state.current_hp
    events, _ = resolve_maximizer_after_cast(
        11, 1, hero, setup, grant, 3, FixedDiceProvider([1] * 9),
    )
    assert events[0].damage_roll is not None
    assert events[0].damage_roll.notation == "9d12"
    assert hero.state.current_hp == hp_before - 9
    assert hero.state.feature_use_counts["overchannel"] == 3
