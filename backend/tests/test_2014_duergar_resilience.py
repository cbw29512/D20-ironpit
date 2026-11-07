from __future__ import annotations

import logging

from app.combat.dice import FixedDiceProvider
from app.combat.saving_throw_rolls import resolve_saving_throw
from app.combat.state import build_combatant_state
from app.content.capability_compiler import compile_combatant
from app.content.monster_basic_candidates_2014 import unsupported_traits_2014
from app.content.monster_definition_adapter_2014 import adapt_basic_monster_2014
from app.content.monster_source_2014 import load_monster_source_2014
from app.domain.saving_throw_context import SavingThrowContext

logger = logging.getLogger(__name__)


def _duergar():
    try:
        return next(m for m in load_monster_source_2014() if m.id == "duergar")
    except Exception:
        logger.exception("Failed to load 2014 Duergar source.")
        raise


def _state():
    try:
        source = _duergar()
        return build_combatant_state(compile_combatant(adapt_basic_monster_2014(source)))
    except Exception:
        logger.exception("Failed to build Duergar state.")
        raise


def test_duergar_resilience_source_binds_and_clears_trait_blocker() -> None:
    try:
        source = _duergar()
        assert "Duergar Resilience" in source.trait_names
        assert "advantage on saving throws against poison, spells, and illusions" in (
            source.source_traits or ""
        )
        assert "Duergar Resilience" not in unsupported_traits_2014(source)
        template = compile_combatant(adapt_basic_monster_2014(source))
        grants = template.progression_features.saving_throw_advantage_grants
        names = {g.source_name for g in grants}
        assert "Duergar Resilience" in names
        magical = [g for g in grants if g.requires_magical_effect]
        assert any(g.source_name == "Duergar Resilience" for g in magical)
        tags = {tag for g in grants if g.source_name == "Duergar Resilience" for tag in g.required_effect_tags}
        assert {"poison", "charm", "paralyzed"} <= tags
    except Exception:
        logger.exception("Duergar Resilience binding regression failed.")
        raise


def test_duergar_resilience_fails_closed_on_source_mutation() -> None:
    try:
        source = _duergar()
        mutated = source.model_copy(update={
            "source_traits": (source.source_traits or "").replace(
                "advantage on saving throws against poison", "advantage on nothing"
            )
        })
        assert "Duergar Resilience" in unsupported_traits_2014(mutated)
        template = compile_combatant(adapt_basic_monster_2014(mutated))
        assert not any(
            g.source_name == "Duergar Resilience"
            for g in template.progression_features.saving_throw_advantage_grants
        )
    except Exception:
        logger.exception("Duergar Resilience mutation fail-closed failed.")
        raise


def test_duergar_resilience_applies_to_poison_and_magical_not_ordinary() -> None:
    try:
        state = _state()
        # ordinary non-tagged non-magical
        roll, _ = resolve_saving_throw(
            state, "wisdom", 99, FixedDiceProvider([8]), SavingThrowContext(),
        )
        assert roll is not None
        assert roll.mode == "normal"
        # poison tag
        roll_p, _ = resolve_saving_throw(
            state, "constitution", 99, FixedDiceProvider([8, 15]),
            SavingThrowContext(effect_tags=frozenset(["poison"])),
        )
        assert roll_p is not None
        assert roll_p.mode == "advantage"
        # magical
        roll_m, _ = resolve_saving_throw(
            state, "wisdom", 99, FixedDiceProvider([8, 15]),
            SavingThrowContext(magical_effect=True),
        )
        assert roll_m is not None
        assert roll_m.mode == "advantage"
    except Exception:
        logger.exception("Duergar Resilience runtime application failed.")
        raise
