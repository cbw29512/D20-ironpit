"""Deep Gnome 2014 Gnome Cunning composes universal save Advantage."""
from app.combat.dice import FixedDiceProvider
from app.combat.opening_modifiers import opening_modifiers
from app.combat.saving_throw_rolls import resolve_saving_throw
from app.combat.state import build_combatant_state
from app.content.capability_compiler import compile_combatant
from app.content.monster_definition_adapter_2014 import adapt_basic_monster_2014
from app.content.monster_passive_grants_2014 import (
    saving_throw_advantage_grants_2014, bound_passive_trait_names_2014,
)
from app.content.monster_source_2014 import load_monster_source_2014
from app.domain.saving_throw_context import SavingThrowContext


def test_deep_gnome_cunning_is_universal_magic_save_advantage() -> None:
    sources = {item.id: item for item in load_monster_source_2014()}
    deep_gnome = sources["deep-gnome-svirfneblin"]
    assert "Gnome Cunning" in bound_passive_trait_names_2014(deep_gnome)
    grant = next(item for item in saving_throw_advantage_grants_2014(deep_gnome)
                 if item.source_name == "Gnome Cunning")
    assert grant.requires_magical_effect is True
    assert grant.abilities == ["intelligence", "wisdom", "charisma"]
    state = build_combatant_state(compile_combatant(adapt_basic_monster_2014(sources["satyr"])))
    state.template.progression_features.saving_throw_advantage_grants = [grant]
    state.active_modifiers = opening_modifiers(state.template)
    for ability in grant.abilities:
        roll, _ = resolve_saving_throw(
            state, ability, 99, FixedDiceProvider([3, 17]),
            SavingThrowContext(magical_effect=True),
        )
        assert roll.mode == "advantage"
        assert roll.rolls == [3, 17]
    for ability, magical in (("strength", True), ("wisdom", False)):
        roll, _ = resolve_saving_throw(
            state, ability, 99, FixedDiceProvider([11]),
            SavingThrowContext(magical_effect=magical),
        )
        assert roll.mode == "normal"
        assert roll.rolls == [11]
