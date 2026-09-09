from app.content.monster_blocker_inventory import blocker_family_incidence, build_monster_blocker_inventory
from app.content.monster_mechanic_family_registry import MONSTER_MECHANIC_FAMILIES


def test_every_active_monster_blocker_family_is_classified() -> None:
    _, _, blockers_by_name = build_monster_blocker_inventory()
    active = set(blocker_family_incidence(blockers_by_name))
    assert active <= set(MONSTER_MECHANIC_FAMILIES)


def test_active_family_entries_name_the_next_reusable_primitive() -> None:
    _, _, blockers_by_name = build_monster_blocker_inventory()
    active = set(blocker_family_incidence(blockers_by_name))
    for family in active:
        entry = MONSTER_MECHANIC_FAMILIES[family]
        assert entry["next_primitive"].strip()
        assert entry["status"] in {"supported", "partial", "missing", "source_defect"}
