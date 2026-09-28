from __future__ import annotations

from app.content.wizard_2014_progression import wizard_2014_level
from app.content.wizard_2014_spell_package import build_wizard_2014_spell_package
from app.content.wizard_evoker_2014_profile import build_elian_starweaver_2014_profile
from app.content.wizard_evoker_2014_runtime import build_elian_starweaver_2014


def _resource_map(level: int) -> dict[str, int]:
    hero = build_elian_starweaver_2014(level)
    return {item.id: item.max_uses for item in hero.resources}


def test_wizard_2014_progression_uses_full_caster_slots_and_correct_evoker_levels() -> None:
    assert wizard_2014_level(1).spell_slots[:3] == (2, 0, 0)
    assert wizard_2014_level(5).spell_slots[:5] == (4, 3, 2, 0, 0)
    assert wizard_2014_level(20).spell_slots == (4, 3, 3, 3, 3, 2, 2, 1, 1)
    assert "sculpt-spells" in wizard_2014_level(2).features_added
    assert "potent-cantrip" in wizard_2014_level(6).features_added
    assert "empowered-evocation" in wizard_2014_level(10).features_added
    assert "overchannel" in wizard_2014_level(14).features_added
    assert "spell-mastery" in wizard_2014_level(18).features_added
    assert "signature-spells" in wizard_2014_level(20).features_added


def test_elian_2014_persistent_profile_advances_intelligence_then_constitution() -> None:
    level_one = build_elian_starweaver_2014_profile(1)
    level_four = build_elian_starweaver_2014_profile(4)
    level_eight = build_elian_starweaver_2014_profile(8)
    level_nineteen = build_elian_starweaver_2014_profile(19)

    assert level_one.final_ability_scores.intelligence == 16
    assert level_four.final_ability_scores.intelligence == 18
    assert level_eight.final_ability_scores.intelligence == 20
    assert level_nineteen.final_ability_scores.constitution == 16
    assert level_nineteen.final_ability_scores.wisdom == 16
    assert level_one.subclass_id is None
    assert build_elian_starweaver_2014_profile(2).subclass_id == "evoker"


def test_wizard_2014_prepared_package_tracks_intelligence_modifier() -> None:
    level_one = build_wizard_2014_spell_package(1, 3)
    level_eight = build_wizard_2014_spell_package(8, 5)
    level_twenty = build_wizard_2014_spell_package(20, 5)

    assert len(level_one.cantrips) == 3
    assert len(level_one.spells) == 4
    assert len(level_eight.cantrips) == 4
    assert len(level_eight.spells) == 13
    assert len(level_twenty.cantrips) == 5
    assert len(level_twenty.spells) == 25


def test_level_two_sculpt_spells_binds_to_generic_ally_protection() -> None:
    hero = build_elian_starweaver_2014(2)
    grant = hero.progression_features.area_spell_ally_protection

    assert grant is not None
    assert grant.source_id == "sculpt-spells"
    assert grant.base_protected_allies == 1
    assert grant.protected_allies_per_slot_level == 1
    assert set(grant.eligible_spell_ids) == {
        "burning-hands", "shatter", "fireball", "lightning-bolt", "cone-of-cold",
    }


def test_level_six_potent_cantrip_reuses_half_damage_on_success() -> None:
    level_five = build_elian_starweaver_2014(5)
    level_six = build_elian_starweaver_2014(6)

    before = next(item for item in level_five.spell_save_actions if item.id == "poison-spray")
    after = next(item for item in level_six.spell_save_actions if item.id == "poison-spray")
    assert before.success_damage == "none"
    assert after.success_damage == "half"


def test_level_ten_empowered_evocation_adds_intelligence_to_evocation_damage() -> None:
    hero = build_elian_starweaver_2014(10)
    intelligence = hero.ability_scores.modifier("intelligence")

    fire_bolt = next(item for item in hero.spell_attack_actions if item.id == "fire-bolt")
    fireball = next(item for item in hero.spell_save_actions if item.id == "fireball")
    missile = next(item for item in hero.auto_hit_spell_actions if item.id == "magic-missile")

    assert intelligence == 5
    assert fire_bolt.damage_bonus == intelligence
    assert fireball.damage_bonus == intelligence
    assert missile.damage_bonus == 1 + intelligence


def test_high_level_wizard_spells_consume_normal_wizard_slots() -> None:
    level_eleven = build_elian_starweaver_2014(11)
    circle = next(item for item in level_eleven.saving_throw_actions if item.id == "circle-of-death")
    assert circle.resource_id == "spell-slot-6"

    level_thirteen = build_elian_starweaver_2014(13)
    finger = next(item for item in level_thirteen.saving_throw_actions if item.id == "finger-of-death")
    assert finger.resource_id == "spell-slot-7"

    level_fifteen = build_elian_starweaver_2014(15)
    stun = next(item for item in level_fifteen.hp_threshold_condition_actions if item.id == "power-word-stun")
    assert stun.resource_id == "spell-slot-8"

    level_seventeen = build_elian_starweaver_2014(17)
    kill = next(item for item in level_seventeen.hp_threshold_instant_death_actions if item.id == "power-word-kill")
    assert kill.resource_id == "spell-slot-9"


def test_spell_mastery_uses_real_spell_levels_without_slot_resources() -> None:
    hero = build_elian_starweaver_2014(18)
    grants = {item.spell_id: item for item in hero.progression_features.alternate_spell_cast_grants}

    assert grants["burning-hands"].cast_level == 1
    assert grants["burning-hands"].resource_id is None
    assert grants["shatter"].cast_level == 2
    assert grants["shatter"].resource_id is None


def test_signature_spells_have_independent_free_cast_resources() -> None:
    hero = build_elian_starweaver_2014(20)
    grants = {item.spell_id: item for item in hero.progression_features.alternate_spell_cast_grants}
    resources = _resource_map(20)

    assert grants["fireball"].cast_level == 3
    assert grants["fireball"].resource_id == "signature-spell-fireball"
    assert grants["lightning-bolt"].cast_level == 3
    assert grants["lightning-bolt"].resource_id == "signature-spell-lightning-bolt"
    assert resources["signature-spell-fireball"] == 1
    assert resources["signature-spell-lightning-bolt"] == 1
    assert next(item for item in hero.spell_save_actions if item.id == "lightning-bolt").level == 3


def test_level_twenty_keeps_raw_full_caster_spell_slots() -> None:
    resources = _resource_map(20)
    assert {key: value for key, value in resources.items() if key.startswith("spell-slot-")} == {
        "spell-slot-1": 4,
        "spell-slot-2": 3,
        "spell-slot-3": 3,
        "spell-slot-4": 3,
        "spell-slot-5": 3,
        "spell-slot-6": 2,
        "spell-slot-7": 2,
        "spell-slot-8": 1,
        "spell-slot-9": 1,
    }
