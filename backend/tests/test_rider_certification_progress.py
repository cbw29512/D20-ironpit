from app.content.monster_catalog import build_monster_catalog
from app.domain.catalog import CoverageStatus


def test_specter_and_stirge_are_raw_ready_from_universal_primitives() -> None:
    cards = {card.name: card for card in build_monster_catalog()}
    for name in ("Specter", "Stirge"):
        card = cards[name]
        assert card.coverage_status is CoverageStatus.RAW_READY
        assert card.runnable_template_id is not None
        assert card.blockers == []
