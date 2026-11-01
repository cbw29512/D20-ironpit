"""Source-proven Light Sensitivity is arena-neutral in the standard Pit."""
import logging

from app.content.monster_basic_candidates_2014 import unsupported_traits_2014
from app.content.monster_source_2014 import load_monster_source_2014

logger = logging.getLogger(__name__)


def _cloaker():
    try:
        return next(row for row in load_monster_source_2014() if row.id == "cloaker")
    except Exception:
        logger.exception("Missing pinned Cloaker source.")
        raise


def test_light_sensitivity_cleared_from_unbound_traits():
    try:
        source = _cloaker()
        original = source.model_dump_json()
        traits = unsupported_traits_2014(source)
        assert "Light Sensitivity" not in traits
        assert "Damage Transfer" in traits
        assert source.model_dump_json() == original
    except Exception:
        logger.exception("Cloaker Light Sensitivity classification failed.")
        raise
