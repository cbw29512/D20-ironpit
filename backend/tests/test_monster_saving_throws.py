from app.content.monster_catalog import load_monster_rows
from app.content.monster_saving_throws import parse_saving_throw_bonuses
from app.content.roster import build_arena_roster

ABILITIES = {"strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"}


def test_every_srd_monster_has_parseable_six_save_table() -> None:
    failures = []
    for row in load_monster_rows():
        try:
            bonuses = parse_saving_throw_bonuses(row)
        except ValueError as exc:
            failures.append(f"{row.get('name')}: {exc}")
            continue
        if set(bonuses) != ABILITIES:
            failures.append(f"{row.get('name')}: incomplete save map {bonuses}")
    assert failures == [], "SRD monster save parsing failures:\n" + "\n".join(failures)


def test_white_dragon_vending_defects_resolve_to_srd_saves() -> None:
    rows = {str(row["name"]): row for row in load_monster_rows()}
    assert parse_saving_throw_bonuses(rows["Adult White Dragon"])["constitution"] == 6
    assert parse_saving_throw_bonuses(rows["Young White Dragon"])["intelligence"] == -2


def test_every_certified_runtime_monster_has_all_six_source_saves() -> None:
    rows = {str(row["name"]): row for row in load_monster_rows()}
    failures = []
    for monster in build_arena_roster().monsters:
        expected = parse_saving_throw_bonuses(rows[monster.name])
        if monster.saving_throw_bonuses != expected:
            failures.append(f"{monster.name}: runtime={monster.saving_throw_bonuses} source={expected}")
    assert failures == [], "Certified runtime save mismatches:\n" + "\n".join(failures)
