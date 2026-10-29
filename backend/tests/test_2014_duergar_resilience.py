from __future__ import annotations

import logging

from app.content.monster_source_2014 import load_monster_source_2014
from app.content.monster_passive_grants_2014 import saving_throw_advantage_grants_2014, bound_passive_trait_names_2014

logger = logging.getLogger(__name__)


def test_duergar_resilience_bound_to_shared_save_advantage() -> None:
    try:
        source = {m.id: m for m in load_monster_source_2014()}
        duergar = source["duergar"]
        assert "Duergar Resilience" in duergar.trait_names
        assert "Duergar Resilience" in bound_passive_trait_names_2014(duergar)
        grants = saving_throw_advantage_grants_2014(duergar)
        tags = {tag for g in grants if g.source_name == "Duergar Resilience" for tag in g.required_effect_tags}
        assert {"poison", "spell", "illusion", "charmed", "paralyzed"} <= tags
    except Exception:
        logger.exception("Duergar Resilience binding regression failed.")
        raise
