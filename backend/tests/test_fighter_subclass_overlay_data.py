from app.content.canonical_class_combat_spines import canonical_combat_features
from app.content.fighter_subclass_overlay_data import FIGHTER_SUBCLASS_DELTA_DATA
from app.content.subclass_combat_overlays import subclass_combat_features


def test_fighter_subclasses_are_five_sparse_rows_not_copied_class_progressions() -> None:
    assert set(FIGHTER_SUBCLASS_DELTA_DATA) == {"battle-master", "eldritch-knight", "psi-warrior"}
    for rows in FIGHTER_SUBCLASS_DELTA_DATA.values():
        assert tuple(rows) == (3, 7, 10, 15, 18)


def test_battle_master_sparse_progression_accumulates_only_subclass_features() -> None:
    assert subclass_combat_features("battle-master", 3) == ("battle-master-combat-superiority",)
    assert subclass_combat_features("battle-master", 18) == (
        "battle-master-combat-superiority",
        "battle-master-know-your-enemy",
        "battle-master-improved-combat-superiority",
        "battle-master-relentless",
        "battle-master-ultimate-combat-superiority",
    )


def test_eldritch_knight_and_psi_warrior_reuse_the_same_fighter_class_spine() -> None:
    ek = canonical_combat_features("fighter", 11, "eldritch-knight")
    psi = canonical_combat_features("fighter", 11, "psi-warrior")
    assert "extra-attack" in ek and "extra-attack" in psi
    assert "eldritch-knight-war-magic" in ek
    assert "eldritch-knight-eldritch-strike" in ek
    assert "psi-warrior-telekinetic-adept" in psi
    assert "psi-warrior-guarded-mind" in psi
    assert "improved-critical" not in ek and "improved-critical" not in psi


def test_student_of_war_is_profile_truth_but_not_an_arena_runtime_feature() -> None:
    row = FIGHTER_SUBCLASS_DELTA_DATA["battle-master"][3]
    assert row["arena_ignored"] == ("battle-master-student-of-war",)
    assert "battle-master-student-of-war" not in subclass_combat_features("battle-master", 3)
