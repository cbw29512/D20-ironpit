from app.content.monster_catalog import build_monster_catalog
from app.domain.catalog import CoverageStatus


def test_specter_and_stirge_are_raw_ready_from_universal_primitives() -> None:
    cards = {card.name: card for card in build_monster_catalog()}
    for name in ("Specter", "Stirge"):
        card = cards[name]
        assert card.coverage_status is CoverageStatus.RAW_READY
        assert card.runnable_template_id is not None
        assert card.blockers == []


def test_monster_certification_does_not_regress_below_157() -> None:
    ready = sum(
        card.coverage_status is CoverageStatus.RAW_READY
        for card in build_monster_catalog()
    )
    assert ready >= 157
