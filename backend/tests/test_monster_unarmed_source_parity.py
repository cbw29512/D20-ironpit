from app.content.capability_registry import build_monster_templates_from_capabilities
from app.content.monster_catalog import load_monster_rows
from app.content.unarmed_opportunity_profiles import monster_unarmed_profile


def test_every_compiled_monster_unarmed_opportunity_profile_matches_source() -> None:
    rows = {str(row["name"]): row for row in load_monster_rows()}
    monsters = build_monster_templates_from_capabilities()

    assert len(monsters) > 0
    assert len({monster.id for monster in monsters}) == len(monsters)

    mismatches: list[str] = []
    for monster in monsters:
        row = rows.get(monster.name)
        if row is None:
            mismatches.append(f"{monster.id}:missing-source-row")
            continue
        expected = monster_unarmed_profile(row)
        if monster.unarmed_opportunity_attack != expected:
            mismatches.append(
                f"{monster.id}:actual={monster.unarmed_opportunity_attack.model_dump()}:"
                f"expected={expected.model_dump()}"
            )

    assert mismatches == [], "\n".join(mismatches)
