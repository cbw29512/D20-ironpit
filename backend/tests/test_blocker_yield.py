from app.content.blocker_yield import build_blocker_signatures, removal_yields, single_family_yields


def test_blocker_signatures_normalize_duplicates_and_sort_names() -> None:
    signatures = build_blocker_signatures({
        "Beta": ["trait", "limited-use", "trait"],
        "Alpha": ["limited-use", "trait"],
        "Solo": ["reaction"],
    })
    assert signatures[("limited-use", "trait")] == ["Alpha", "Beta"]
    assert signatures[("reaction",)] == ["Solo"]


def test_single_family_yields_only_include_one_blocker_signatures() -> None:
    signatures = {
        ("unsupported-action-rider",): ["Cultist", "Goat"],
        ("reaction",): ["Shrieker Fungus"],
        ("limited-use", "trait"): ["Example"],
    }
    assert single_family_yields(signatures) == {
        "unsupported-action-rider": ["Cultist", "Goat"],
        "reaction": ["Shrieker Fungus"],
    }
    assert removal_yields(signatures) == {
        "unsupported-action-rider": ["Cultist", "Goat"],
        "reaction": ["Shrieker Fungus"],
    }
