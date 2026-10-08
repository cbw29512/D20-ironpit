"""2014 Drow/Drider Fey Ancestry reuses universal tagged save Advantage."""
from __future__ import annotations

import logging

from app.content.monster_passive_grants_2014 import (
    bound_passive_trait_names_2014,
    saving_throw_advantage_grants_2014,
)
from app.content.monster_source_2014 import load_monster_source_2014

logger = logging.getLogger(__name__)


def test_fey_ancestry_is_source_tagged_charm_save_advantage() -> None:
    try:
        sources = {item.id: item for item in load_monster_source_2014()}
        for monster_id in ("drow", "drider"):
            monster = sources[monster_id]
            assert "Fey Ancestry" in monster.trait_names
            assert "Fey Ancestry" in bound_passive_trait_names_2014(monster)
            grants = [
                grant for grant in saving_throw_advantage_grants_2014(monster)
                if grant.source_name == "Fey Ancestry"
            ]
            assert len(grants) == 1
            assert grants[0].required_effect_tags == ["charm"]
            assert set(grants[0].abilities) == {
                "strength", "dexterity", "constitution",
                "intelligence", "wisdom", "charisma",
            }
            assert grants[0].requires_magical_effect is False
    except Exception:
        logger.exception("2014 Fey Ancestry source binding certification failed")
        raise


def test_fey_ancestry_grants_advantage_only_for_charm_tag() -> None:
    from app.combat.dice import FixedDiceProvider
    from app.combat.opening_modifiers import opening_modifiers
    from app.combat.saving_throw_rolls import resolve_saving_throw
    from app.combat.state import build_combatant_state
    from app.content.capability_compiler import compile_combatant
    from app.content.monster_definition_adapter_2014 import adapt_basic_monster_2014
    from app.domain.saving_throw_context import SavingThrowContext

    try:
        sources = {item.id: item for item in load_monster_source_2014()}
        base = compile_combatant(adapt_basic_monster_2014(sources["satyr"]))
        for monster_id in ("drow", "drider"):
            state = build_combatant_state(base)
            state.template.progression_features.saving_throw_advantage_grants = [
                grant for grant in saving_throw_advantage_grants_2014(sources[monster_id])
                if grant.source_name == "Fey Ancestry"
            ]
            state.active_modifiers = opening_modifiers(state.template)
            charm, _ = resolve_saving_throw(
                state, "wisdom", 99, FixedDiceProvider([3, 18]),
                SavingThrowContext(effect_tags=frozenset({"charm"})),
            )
            assert charm.mode == "advantage"
            assert charm.rolls == [3, 18]
            ordinary, _ = resolve_saving_throw(
                state, "wisdom", 99, FixedDiceProvider([11]),
                SavingThrowContext(effect_tags=frozenset({"frightened"})),
            )
            assert ordinary.mode == "normal"
            assert ordinary.rolls == [11]
    except Exception:
        logger.exception("2014 Fey Ancestry save Advantage behavior failed")
        raise
