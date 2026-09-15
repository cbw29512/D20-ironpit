from app.combat.berserk import resolve_start_turn_berserk
from app.combat.dice import FixedDiceProvider
from app.combat.encounter_targeting import select_nearest_target
from app.content.monster_catalog_2014 import compile_monster_2014, load_catalog_2014
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.runtime import CombatantState


def _source(monster_id: str):
    return next(item for item in load_catalog_2014() if item.id == monster_id)


def _member(combatant_id: str, side: str, template, position_ft: int) -> EncounterCombatant:
    return EncounterCombatant(
        combatant_id=combatant_id,
        side=side,
        position_ft=position_ft,
        state=CombatantState(template=template, current_hp=template.max_hp),
    )


def test_2014_berserk_profiles_bind_source_thresholds() -> None:
    flesh = compile_monster_2014(_source("flesh-golem"))
    clay_source = _source("clay-golem")
    assert flesh.berserk is not None and flesh.berserk.hp_threshold == 40
    assert clay_source.source_traits is not None and "60 hit points or fewer" in clay_source.source_traits


def test_berserk_activates_on_declared_roll_and_targets_nearest_creature() -> None:
    template = compile_monster_2014(_source("flesh-golem"))
    attacker = _member("golem", "monsters", template, 10)
    ally = _member("ally", "monsters", template, 5)
    enemy = _member("enemy", "heroes", template, 20)
    attacker.state.current_hp = 40
    event = resolve_start_turn_berserk(1, 1, attacker.combatant_id, attacker.state, FixedDiceProvider([6]))
    assert event is not None and event.feature_id == "berserk"
    setup = EncounterSetup(
        heroes=[enemy], monsters=[attacker, ally], hero_total_levels=1, monster_total_cr="10",
    )
    assert select_nearest_target(attacker, setup) is ally
