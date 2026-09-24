from app.content.bard_lore_2014_runtime import build_lyra_silverstring_2014
from app.content.druid_land_2014_runtime import build_thalen_greenbough_2014
from app.content.ranger_hunter_2014_runtime import build_rowan_ashtrail_2014
from app.content.sorcerer_draconic_2014_runtime import build_nyra_emberveil_2014
from app.content.warlock_fiend_2014_runtime import build_varek_ashenmark_2014
from app.content.wizard_evoker_2014_runtime import build_elian_starweaver_2014


def test_shared_2014_cantrip_scaling_and_healing_bindings() -> None:
    bard = build_lyra_silverstring_2014(6)
    assert [item.id for item in bard.healing_actions] == ["healing-word"]
    assert {item.id for item in bard.spell_attack_actions} == {"fire-bolt"}
    assert {item.id for item in bard.spell_save_actions} == {"shatter", "fireball"}
    assert next(item for item in bard.spell_attack_actions if item.id == "fire-bolt").damage_dice_count == 2

    druid = build_thalen_greenbough_2014(11)
    assert [item.id for item in druid.healing_actions] == ["cure-wounds"]
    assert druid.spell_attack_actions[0].id == "produce-flame"
    assert druid.spell_attack_actions[0].damage_dice_count == 3
    assert druid.spell_save_actions[0].id == "poison-spray"
    assert druid.spell_save_actions[0].damage_dice_count == 3

    ranger_one = build_rowan_ashtrail_2014(1)
    ranger_two = build_rowan_ashtrail_2014(2)
    assert ranger_one.healing_actions == []
    assert [item.id for item in ranger_two.healing_actions] == ["cure-wounds"]


def test_sorcerer_and_wizard_use_supported_attack_and_save_spell_primitives() -> None:
    sorcerer = build_nyra_emberveil_2014(11)
    assert [item.id for item in sorcerer.spell_attack_actions] == ["fire-bolt"]
    assert sorcerer.spell_attack_actions[0].damage_dice_count == 3
    assert {item.id for item in sorcerer.spell_save_actions} == {"fireball", "disintegrate"}

    wizard = build_elian_starweaver_2014(17)
    assert [item.id for item in wizard.spell_attack_actions] == ["fire-bolt"]
    assert wizard.spell_attack_actions[0].damage_dice_count == 4
    assert {item.id for item in wizard.spell_save_actions} == {"poison-spray", "fireball", "disintegrate"}
    assert next(item for item in wizard.spell_save_actions if item.id == "poison-spray").success_damage == "half"


def test_fiend_warlock_fireball_tracks_current_pact_slot_level() -> None:
    expected = {
        5: ("fireball", 3, 8),
        7: ("fireball-l4", 4, 9),
        9: ("fireball-l5", 5, 10),
        17: ("fireball-l5", 5, 10),
    }
    for level, (spell_id, spell_level, dice_count) in expected.items():
        warlock = build_varek_ashenmark_2014(level)
        fireball = warlock.spell_save_actions[1]
        assert fireball.id == spell_id
        assert fireball.level == spell_level
        assert fireball.damage_dice_count == dice_count
        resources = {item.id: item.max_uses for item in warlock.resources}
        assert resources[f"spell-slot-{spell_level}"] > 0

    low = build_varek_ashenmark_2014(4)
    assert [item.id for item in low.spell_save_actions] == ["poison-spray"]
