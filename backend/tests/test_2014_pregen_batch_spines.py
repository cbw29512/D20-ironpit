from app.content.bard_lore_2014_data import (
    CANTRIPS_KNOWN,
    FEATURE_LEVELS,
    SPELLS_KNOWN,
    SPELL_SLOTS,
    bardic_inspiration_die,
)
from app.content.druid_land_2014_progression import druid_land_2014_level
from app.content.ranger_hunter_2014_progression import ranger_hunter_2014_level
from app.content.sorcerer_draconic_2014_progression import sorcerer_draconic_2014_level
from app.content.warlock_fiend_2014_progression import warlock_fiend_2014_level
from app.content.wizard_evoker_2014_progression import wizard_evoker_2014_level


def test_2014_batch_spines_use_2014_breakpoints() -> None:
    assert FEATURE_LEVELS["cutting-words"] == 3
    assert FEATURE_LEVELS["additional-magical-secrets"] == 6
    assert FEATURE_LEVELS["peerless-skill"] == 14
    assert FEATURE_LEVELS["superior-inspiration"] == 20
    assert bardic_inspiration_die(5) == 8
    assert bardic_inspiration_die(10) == 10
    assert bardic_inspiration_die(15) == 12
    assert SPELL_SLOTS[20] == (4, 3, 3, 3, 3, 2, 2, 1, 1)
    assert SPELLS_KNOWN[19] == 22
    assert CANTRIPS_KNOWN[9] == 4

    assert ranger_hunter_2014_level(2).spells_known == 2
    assert ranger_hunter_2014_level(3).features_added[-1] == "hunter-colossus-slayer"
    assert ranger_hunter_2014_level(5).spell_slots == (4, 2, 0, 0, 0)
    assert ranger_hunter_2014_level(7).features_added == ("hunter-multiattack-defense",)
    assert ranger_hunter_2014_level(11).features_added == ("hunter-volley",)
    assert ranger_hunter_2014_level(15).features_added == ("hunter-evasion",)

    sorcerer = sorcerer_draconic_2014_level(14)
    assert sorcerer.sorcery_points == 14
    assert "dragon-wings" in sorcerer.features_added
    assert sorcerer_draconic_2014_level(2).sorcery_points == 2
    assert sorcerer_draconic_2014_level(20).sorcery_points == 20

    warlock = warlock_fiend_2014_level(11)
    assert warlock.pact_slots == 3
    assert warlock.pact_slot_level == 5
    assert warlock.mystic_arcanum_levels == (6,)
    assert warlock_fiend_2014_level(17).mystic_arcanum_levels == (6, 7, 8, 9)

    wizard = wizard_evoker_2014_level(14)
    assert "overchannel" in wizard.features_added
    assert wizard.spellbook_minimum == 32
    assert wizard_evoker_2014_level(20).spellbook_minimum == 44


def test_2014_land_druid_wild_shape_limits_progress_without_edition_leakage() -> None:
    level_one = druid_land_2014_level(1)
    assert level_one.wild_shape_uses == 0
    assert level_one.wild_shape_unlimited is False
    assert level_one.wild_shape_max_cr is None

    level_two = druid_land_2014_level(2)
    assert level_two.wild_shape_uses == 2
    assert level_two.wild_shape_max_cr == "1/4"
    assert level_two.wild_shape_allows_swim is False
    assert level_two.wild_shape_allows_fly is False

    level_four = druid_land_2014_level(4)
    assert level_four.wild_shape_max_cr == "1/2"
    assert level_four.wild_shape_allows_swim is True
    assert level_four.wild_shape_allows_fly is False

    level_eight = druid_land_2014_level(8)
    assert level_eight.wild_shape_max_cr == "1"
    assert level_eight.wild_shape_allows_fly is True

    level_twenty = druid_land_2014_level(20)
    assert level_twenty.wild_shape_uses == 2
    assert level_twenty.wild_shape_unlimited is True
