from app.content.figure_profiles import MONSTER_FIGURE_PROFILES
from app.content.monster_catalog import build_monster_catalog
from app.domain.catalog import CoverageStatus


def test_reviewed_figure_registry_matches_raw_ready_monster_set_exactly() -> None:
    ready_names = {
        card.name
        for card in build_monster_catalog()
        if card.coverage_status is CoverageStatus.RAW_READY
    }
    assert len(ready_names) == 68
    assert set(MONSTER_FIGURE_PROFILES) == ready_names


def test_reviewed_profiles_are_explicit_and_nonempty() -> None:
    for name, profile in MONSTER_FIGURE_PROFILES.items():
        assert profile["form"]
        assert profile["detail"]
        assert profile["form"] != "unknown", f"{name} cannot be certified with an unknown silhouette"


def test_anatomically_distinct_monsters_do_not_share_humanoid_fallbacks() -> None:
    expected = {
        "Axe Beak": "bird",
        "Baboon": "primate",
        "Giant Constrictor Snake": "snake",
        "Giant Wolf Spider": "spider",
        "Hippogriff": "hippogriff",
        "Owlbear": "bear",
        "Plesiosaurus": "aquatic-reptile",
        "Pteranodon": "pterosaur",
        "Rhinoceros": "hoofed",
        "Tyrannosaurus Rex": "reptile",
    }
    for name, form in expected.items():
        assert MONSTER_FIGURE_PROFILES[name]["form"] == form
