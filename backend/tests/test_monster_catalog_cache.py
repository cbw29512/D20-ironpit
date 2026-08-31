from app.content.monster_catalog import load_monster_rows


def test_cached_monster_catalog_returns_mutation_safe_copies() -> None:
    first = load_monster_rows()
    second = load_monster_rows()

    assert len(first) == len(second) == 330
    original_name = str(second[0]["name"])
    first[0]["name"] = "MUTATED"

    third = load_monster_rows()
    assert str(second[0]["name"]) == original_name
    assert str(third[0]["name"]) == original_name
    assert first is not second
    assert first[0] is not second[0]
