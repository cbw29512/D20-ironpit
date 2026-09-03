import json
from pathlib import Path

from app.content.hero_variant_policy import TARGET_SUBCLASSES
from app.content.roster_mechanic_requirements import derive_roster_mechanic_requirements


ROOT = Path(__file__).resolve().parents[2]


def _statuses() -> dict[str, str]:
    payload = json.loads((ROOT / "data/combat_engine_coverage_v1.json").read_text(encoding="utf-8"))
    return {item["id"]: item["status"] for item in payload["capabilities"]}


def test_checklist_is_derived_from_all_37_subclass_specializations() -> None:
    requirements = derive_roster_mechanic_requirements(_statuses())
    owners = {owner for item in requirements for owner in item.owners if not owner.endswith("/base")}
    expected = {
        f"{class_id}/{subclass_id}"
        for class_id, subclass_ids in TARGET_SUBCLASSES.items()
        for subclass_id in subclass_ids
    }
    assert owners == expected
    assert len(expected) == 37


def test_weapon_rules_remain_generic_deduplicated_capabilities() -> None:
    by_id = {item.id: item for item in derive_roster_mechanic_requirements(_statuses())}
    assert by_id["nick-mastery"].status == "supported"
    assert {"barbarian/path-zealot", "fighter/battle-master", "ranger/beastmaster"} <= set(
        by_id["nick-mastery"].owners
    )
    assert by_id["vex-mastery"].demand_count > 1
    assert not any("battlemaster-nick" in mechanic_id or "fighter-vex" in mechanic_id for mechanic_id in by_id)


def test_spell_packages_and_outcome_changing_choices_stay_planned_until_compiled() -> None:
    by_id = {item.id: item for item in derive_roster_mechanic_requirements(_statuses())}
    assert by_id["spell-package:circle-sea"].status == "planned"
    assert by_id["feature-choice:moon-beast-form-package"].status == "planned"
    assert by_id["feature-choice:blessed-strikes-divine-strike-radiant"].status == "planned"
    assert by_id["disciple-of-life"].status == "supported"


def test_committed_checklist_matches_current_roster() -> None:
    payload = json.loads((ROOT / "data/roster_combat_mechanics_v1.json").read_text(encoding="utf-8"))
    requirements = derive_roster_mechanic_requirements(_statuses())
    assert payload["roster"] == {"classes": 12, "subclasses": 37}
    assert [item["id"] for item in payload["mechanics"]] == [item.id for item in requirements]
