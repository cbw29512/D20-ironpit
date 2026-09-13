from app.content.pregen_blocker_yield import (
    build_pregen_blocker_bundle_yields,
    build_pregen_blocker_yields,
)


def test_blocker_yield_tracks_current_frontier_features() -> None:
    yields = {item.feature_id: item for item in build_pregen_blocker_yields()}

    assert "steady-aim" in yields
    assert "rogue" in yields["steady-aim"].frontier_classes
    assert "brutal-strike" in yields
    assert "barbarian" in yields["brutal-strike"].frontier_classes
    assert "sear-undead" in yields
    assert "cleric" in yields["sear-undead"].frontier_classes
    assert "boon-combat-prowess" in yields
    assert "fighter" in yields["boon-combat-prowess"].frontier_classes
    assert "survivor-defy-death" not in yields
    assert "survivor-heroic-rally" not in yields


def test_blocker_yield_is_sorted_for_work_ordering() -> None:
    yields = build_pregen_blocker_yields()
    sort_keys = [
        (-item.frontier_count, -item.remaining_snapshots, item.feature_id)
        for item in yields
    ]

    assert sort_keys == sorted(sort_keys)
    assert all(item.remaining_snapshots > 0 for item in yields)


def test_blocker_bundles_keep_multi_feature_frontiers_visible() -> None:
    bundles = build_pregen_blocker_bundle_yields()
    cleric_bundle = next(
        item for item in bundles
        if "sear-undead" in item.feature_ids
        and "cleric-combat-spells-3" in item.feature_ids
        and "cleric" in item.frontier_classes
    )

    assert cleric_bundle.frontier_count >= 1
    assert cleric_bundle.remaining_snapshots >= 1
