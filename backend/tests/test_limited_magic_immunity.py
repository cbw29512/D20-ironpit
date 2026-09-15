from app.combat.saving_throw_rolls import saving_throw_mode
from app.combat.spell_immunity import spell_affects_target
from app.combat.state import build_combatant_state
from app.content.demo import build_goblin_warrior
from app.content.monster_catalog_2014_traits import combat_traits_2014
from app.domain.models import RollMode
from app.domain.traits import CombatTrait


def test_limited_magic_immunity_blocks_low_spells_and_grants_magic_resistance() -> None:
    traits = combat_traits_2014(["Limited Magic Immunity"])
    assert CombatTrait.LIMITED_MAGIC_IMMUNITY in traits
    assert CombatTrait.MAGIC_RESISTANCE in traits
    template = build_goblin_warrior().model_copy(deep=True)
    template.combat_traits = traits
    state = build_combatant_state(template)
    assert spell_affects_target(state, 6) is False
    assert spell_affects_target(state, 7) is True
    assert saving_throw_mode(state, "wisdom", magical_effect=True) is RollMode.ADVANTAGE
