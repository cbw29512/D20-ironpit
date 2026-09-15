from app.combat.saving_throw_rolls import saving_throw_mode
from app.combat.state import build_combatant_state
from app.content.demo import build_goblin_warrior
from app.domain.models import RollMode
from app.domain.traits import CombatTrait


def test_brave_grants_advantage_only_against_frightened() -> None:
    template = build_goblin_warrior().model_copy(deep=True)
    template.combat_traits = [*template.combat_traits, CombatTrait.BRAVE]
    state = build_combatant_state(template)

    assert saving_throw_mode(state, "wisdom", against_condition="frightened") == RollMode.ADVANTAGE
    assert saving_throw_mode(state, "wisdom", against_condition="charmed") == RollMode.NORMAL
