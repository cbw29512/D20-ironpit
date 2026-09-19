from app.content.monster_catalog import load_monster_rows
from app.content.monster_source_audit import audit_monster_source
from app.content.roster import build_arena_roster


def _wolf():
    return next(monster for monster in build_arena_roster().monsters if monster.name == "Wolf")


def _rows() -> dict[str, dict[str, object]]:
    return {str(row["name"]): dict(row) for row in load_monster_rows()}


def test_immediate_dynamic_combatant_creation_fails_closed() -> None:
    rows = _rows()

    for name in ("Treant", "Wraith", "Black Pudding", "Ochre Jelly"):
        issues = audit_monster_source(_wolf(), rows[name])
        assert "unsupported-dynamic-combatant-lifecycle" in issues, name


def test_delayed_post_combat_spawn_text_is_not_misclassified() -> None:
    rows = _rows()

    for name in ("Shadow", "Wight", "Troll Limb"):
        issues = audit_monster_source(_wolf(), rows[name])
        assert "unsupported-dynamic-combatant-lifecycle" not in issues, name
