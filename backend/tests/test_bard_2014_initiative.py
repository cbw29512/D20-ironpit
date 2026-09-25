from __future__ import annotations

from app.content.bard_2014_initiative import build_bard_2014_initiative_refills


def test_superior_inspiration_reuses_universal_zero_resource_refill() -> None:
    assert build_bard_2014_initiative_refills(19) == []
    grants = build_bard_2014_initiative_refills(20)
    assert len(grants) == 1
    grant = grants[0]
    assert grant.source_id == "superior-inspiration"
    assert grant.source_name == "Superior Inspiration"
    assert grant.resource_id == "bardic-inspiration"
    assert grant.when_at_or_below == 0
    assert grant.restore_amount == 1
