from __future__ import annotations

from app.content.monster_catalog import load_monster_rows
from app.content.monster_save_action_source_section import save_action_source
from app.content.monster_source_audit import audit_monster_source
from app.content.roster import build_arena_roster


def test_swallow_audit_uses_declared_action_cost_source_section(monkeypatch) -> None:
    """Bonus Action Swallow must reconcile against Bonus Actions, not Actions."""
    rows = {str(row["name"]): row for row in load_monster_rows()}
    source = next(template for template in build_arena_roster().monsters if template.name == "Giant Frog").model_copy(deep=True)
    assert source.swallow_actions

    swallow = source.swallow_actions[0].model_copy(update={"action_cost": "bonus_action"})
    source.swallow_actions = [swallow]
    row = dict(rows["Giant Frog"])
    row["bonusActions"] = row.get("actions", "")

    observed: list[str] = []

    def capture(_action, source_text: str) -> list[str]:
        observed.append(source_text)
        return []

    monkeypatch.setattr("app.content.monster_source_audit.swallow_action_issues", capture)
    audit_monster_source(source, row)

    assert observed == [save_action_source(row, "bonus_action")]
