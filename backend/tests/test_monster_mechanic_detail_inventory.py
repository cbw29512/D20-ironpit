from app.content.monster_mechanic_detail_inventory import complex_action_incidence, control_effect_incidence


def test_complex_action_inventory_classifies_save_branch_labels() -> None:
    rows = {"Example": {"actions": "Ruin. Saving Throw: DC 15 Wisdom. Failure: 10 damage. Success: Half damage."}}
    incidence = complex_action_incidence(rows, ["Example"])
    assert incidence["save-branch"] == ["Example"]


def test_control_inventory_normalizes_push_pull_and_swallow() -> None:
    rows = {"Example": {"actions": "The target is pushed 10 feet, then pulled 5 feet and swallowed."}}
    incidence = control_effect_incidence(rows, ["Example"])
    assert incidence["forced-push"] == ["Example"]
    assert incidence["forced-pull"] == ["Example"]
    assert incidence["swallow"] == ["Example"]
