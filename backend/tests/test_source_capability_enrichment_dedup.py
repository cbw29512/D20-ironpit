from types import SimpleNamespace

from app.content.source_capability_enrichment import _merge_save_actions


def _save(action_id: str):
    return SimpleNamespace(
        id=action_id,
        name="Constrict",
        action_cost="action",
        resource_id=None,
    )


def test_existing_semantic_save_duplicates_collapse_to_canonical_action() -> None:
    canonical = _save("giant-constrictor-snake-constrict")
    stale_source_copy = _save("srd-giant-constrictor-snake-constrict")
    source = _save("srd-giant-constrictor-snake-constrict")

    merged = _merge_save_actions([canonical, stale_source_copy], [source], {})

    assert [action.id for action in merged] == [canonical.id]
