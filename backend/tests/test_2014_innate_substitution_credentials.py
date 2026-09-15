from app.content.monster_catalog_2014 import load_catalog_2014, unsupported_mechanics_2014
from app.content.monster_innate_spell_actions_2014 import innate_spell_save_actions_2014
from app.content.monster_spell_substitutions_2014 import build_arena_damage_substitute


def _ice_mephit():
    try:
        return next(monster for monster in load_catalog_2014() if monster.name == "Ice Mephit")
    except StopIteration as exc:
        raise AssertionError("Missing 2014 Ice Mephit catalog fixture.") from exc


def test_innate_arena_substitution_without_source_save_dc_is_explicit_blocker() -> None:
    monster = _ice_mephit()
    assert monster.innate_spellcasting is not None
    assert monster.innate_spellcasting.save_dc is None

    blockers = unsupported_mechanics_2014(monster)
    assert "spell:fog cloud (arena substitution requires spell save DC)" in blockers
    assert "compile:universal-runtime" not in blockers


def test_innate_arena_substitution_never_invents_missing_save_dc() -> None:
    monster = _ice_mephit()
    actions = innate_spell_save_actions_2014(monster)

    assert all(action.id != "fog-cloud" for action in actions)


def test_sixth_level_arena_substitution_uses_disintegrate_no_damage_on_save() -> None:
    action = build_arena_damage_substitute("blade-barrier", "Blade Barrier", 6, 20)

    assert action.name == "Blade Barrier → Disintegrate"
    assert action.level == 6
    assert action.dc == 20
    assert action.save_ability == "dexterity"
    assert action.damage_dice_count == 10
    assert action.damage_dice_size == 6
    assert action.damage_bonus == 40
    assert action.damage_type == "force"
    assert action.success_damage == "none"
