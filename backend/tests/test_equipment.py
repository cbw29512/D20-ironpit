from app.content.demo import build_demo_fighter, build_goblin_warrior
from app.content.equipment import (
    build_fighter_visual_loadout,
    build_goblin_visual_loadout,
    build_longsword,
    build_scimitar,
)


def test_reusable_weapon_records_match_mvp_combatants() -> None:
    try:
        fighter = build_demo_fighter()
        goblin = build_goblin_warrior()

        assert fighter.weapon == build_longsword()
        assert goblin.weapon == build_scimitar()
    except Exception as exc:
        raise AssertionError("Reusable weapon records should build valid MVP combatants.") from exc


def test_visual_loadouts_preserve_current_mvp_gear() -> None:
    try:
        fighter = build_fighter_visual_loadout()
        goblin = build_goblin_visual_loadout()

        assert fighter.armor == "chain-mail"
        assert fighter.main_hand == "longsword"
        assert fighter.off_hand == "shield"
        assert goblin.armor == "leather"
        assert goblin.main_hand == "scimitar"
        assert goblin.off_hand == "shield"
    except Exception as exc:
        raise AssertionError("Visual loadout records should preserve the MVP presentation.") from exc
