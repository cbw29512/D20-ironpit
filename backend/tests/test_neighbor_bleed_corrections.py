from app.content.monster_catalog import load_monster_rows


def test_reviewed_neighbor_bleed_rows_end_at_their_real_stat_blocks() -> None:
    rows = {str(row["name"]): row for row in load_monster_rows()}
    expected = {
        "Awakened Tree": ("Bludgeoning damage.", "Axe Beak"),
        "Gargoyle": ("Slashing damage.", "Gelatinous Cube"),
        "Grimlock": ("Psychic damage.", "Guardian Naga"),
        "Guard Captain": ("Slashing damage.", "Half-Dragon"),
        "Violet Fungus": ("Necrotic damage.", "Gargoyle"),
    }
    for name, (real_ending, spillover) in expected.items():
        row = rows[name]
        assert str(row["actions"]).endswith(real_ending)
        assert str(row["rawText"]).endswith(real_ending)
        assert not str(row["actions"]).endswith(spillover)
        assert not str(row["rawText"]).endswith(spillover)
