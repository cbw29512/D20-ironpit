from app.content.pregen_certification_queue import (
    build_pregen_certification_frontier,
    certified_level_by_class,
)


def test_certified_level_by_class_includes_all_canonical_classes() -> None:
    levels = certified_level_by_class()

    assert len(levels) == 12
    assert levels["fighter"] == 17
    assert levels["barbarian"] == 8
    assert levels["cleric"] == 4
    assert levels["rogue"] == 2
    assert all(level == 0 for class_id, level in levels.items() if class_id not in {
        "fighter", "barbarian", "cleric", "rogue",
    })


def test_frontier_is_sequential_and_sorted_by_blocker_count() -> None:
    frontier = build_pregen_certification_frontier()
    levels = certified_level_by_class()

    assert len(frontier) == 12
    assert all(item.next_level == levels[item.class_id] + 1 for item in frontier)
    assert [item.blocker_count for item in frontier] == sorted(
        item.blocker_count for item in frontier
    )


def test_known_certified_frontiers_fail_closed_on_real_features() -> None:
    frontier = {item.class_id: item for item in build_pregen_certification_frontier()}

    assert frontier["rogue"].next_level == 3
    assert "steady-aim" in frontier["rogue"].unsupported_features

    assert frontier["barbarian"].next_level == 9
    assert "brutal-strike" in frontier["barbarian"].unsupported_features

    assert frontier["cleric"].next_level == 5
    assert "sear-undead" in frontier["cleric"].unsupported_features

    assert frontier["fighter"].next_level == 18
    assert "survivor" in frontier["fighter"].unsupported_features
