from app.content.monster_catalog import load_monster_rows
from app.content.monster_source_audit import audit_monster_source
from app.content.roster import build_arena_roster


def _wolf():
    return next(monster for monster in build_arena_roster().monsters if monster.name == "Wolf")


def _wolf_row() -> dict[str, object]:
    return dict(next(row for row in load_monster_rows() if row["name"] == "Wolf"))


def test_unmodeled_hp_maximum_reduction_fails_closed() -> None:
    row = _wolf_row()
    row["actions"] = (
        str(row["actions"])
        + " The target's Hit Point maximum decreases by an amount equal to the damage taken."
    )

    issues = audit_monster_source(_wolf(), row)

    assert "unsupported-action-rider:hit-point-maximum-reduction" in issues
