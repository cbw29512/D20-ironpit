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
    assert "survivor-defy-death" in yields
    assert "fighter" in yields["survivor-defy-death"].frontier_classes
    assert "survivor-heroic-rally" in yields
    assert "fighter" in yields["survivor-heroic-rally"].frontier_classes


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
    fighter_survivor = next(
        item for item in bundles
        if "survivor-defy-death" in item.feature_ids
        and "survivor-heroic-rally" in item.feature_ids
        and "fighter" in item.frontier_classes
    )

    assert fighter_survivor.frontier_count >= 1
    assert fighter_survivor.remaining_snapshots >= 1
