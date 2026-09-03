from app.content.legacy_monster_roster import build_legacy_monster_templates
from app.content.monster_catalog import build_monster_catalog
from app.domain.catalog import CoverageStatus


def test_aquatic_only_killer_whale_is_deferred_from_standard_arena() -> None:
    templates = build_legacy_monster_templates()
    assert all(template.name != "Killer Whale" for template in templates)

    card = next(card for card in build_monster_catalog() if card.name == "Killer Whale")
    assert card.coverage_status is CoverageStatus.BLOCKED
    assert card.runnable_template_id is None
    assert card.blockers == ["deferred-environment:aquatic-only"]


def test_land_arena_grapple_batch_remains_eligible() -> None:
    names = {template.name for template in build_legacy_monster_templates()}
    assert {"Giant Scorpion", "Grick", "Griffon"} <= names
