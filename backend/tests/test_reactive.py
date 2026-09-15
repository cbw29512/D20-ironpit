from app.combat.reactive import refresh_reactive_reactions
from app.combat.state import build_combatant_state
from app.content.demo import build_goblin_warrior
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.traits import CombatTrait


def _member(combatant_id: str, side: str, reactive: bool) -> EncounterCombatant:
    template = build_goblin_warrior().model_copy(deep=True)
    if reactive:
        template.combat_traits.append(CombatTrait.REACTIVE)
    state = build_combatant_state(template)
    state.reaction_available = False
    return EncounterCombatant(combatant_id=combatant_id, side=side, position_ft=0, state=state)


def test_reactive_refreshes_only_reactive_creatures_each_turn() -> None:
    hero = _member("hero", "heroes", False)
    reactive = _member("marilith", "monsters", True)
    ordinary = _member("ordinary", "monsters", False)
    setup = EncounterSetup(
        heroes=[hero], monsters=[reactive, ordinary], hero_total_levels=1, monster_total_cr="1",
    )

    assert refresh_reactive_reactions(setup) == 1
    assert reactive.state.reaction_available is True
    assert hero.state.reaction_available is False
    assert ordinary.state.reaction_available is False

    reactive.state.reaction_available = False
    assert refresh_reactive_reactions(setup) == 1
    assert reactive.state.reaction_available is True
