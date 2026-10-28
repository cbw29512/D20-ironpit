from __future__ import annotations

import logging

from app.content.monster_source_2014 import load_monster_source_2014
from app.content.monster_source_duergar_resilience_2014 import source_duergar_resilience_2014
from app.content.monster_passive_grants_2014 import saving_throw_advantage_grants_2014, bound_passive_trait_names_2014
from app.content.monster_basic_candidates_2014 import unsupported_traits_2014

logger = logging.getLogger(__name__)


def _duergar():
    try:
        return next(m for m in load_monster_source_2014() if m.name == "Duergar")
    except Exception:
        logger.exception("Failed to load 2014 Duergar source.")
        raise


def test_duergar_resilience_source_proof_and_binding() -> None:
    try:
        source = _duergar()
        profile = source_duergar_resilience_2014(source)
        assert profile is not None
        assert profile.source_name == "Duergar Resilience"
        assert profile.magical_effect_advantage is True
        assert set(profile.effect_tags) == {"poison", "charmed", "paralyzed"}

        grants = saving_throw_advantage_grants_2014(source)
        magical = [g for g in grants if g.requires_magical_effect]
        tagged = [g for g in grants if g.required_effect_tags]
        assert any(g.source_name == "Duergar Resilience" and g.requires_magical_effect for g in magical)
        assert {tuple(g.required_effect_tags) for g in tagged if g.source_name == "Duergar Resilience"} == {
            ("poison",), ("charmed",), ("paralyzed",),
        }
        assert "Duergar Resilience" in bound_passive_trait_names_2014(source)
        # Trait is now bound; other blockers remain.
        assert "Duergar Resilience" not in unsupported_traits_2014(source)
    except Exception:
        logger.exception("2014 Duergar Resilience binding regression failed.")
        raise
