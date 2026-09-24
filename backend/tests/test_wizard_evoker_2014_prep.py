from app.content.certified_hero_progressions import CERTIFIED_HERO_PROGRESSIONS
from app.content.wizard_evoker_2014_combat_profile import build_elian_starweaver_2014_combat_profile
from app.content.wizard_evoker_2014_profile import build_elian_starweaver_2014_profile
from app.content.wizard_evoker_2014_runtime import build_elian_starweaver_2014


def test_elian_persistent_identity_and_asi_progression_are_prepared() -> None:
    one = build_elian_starweaver_2014_profile(1)
    twenty = build_elian_starweaver_2014_profile(20)
    assert one.character_name == twenty.character_name == "Elian Starweaver"
    assert one.species_id == twenty.species_id == "human"
    assert twenty.subclass_id == "evoker"
    assert one.class_equipment == twenty.class_equipment
    assert twenty.final_ability_scores.intelligence == 20
    assert twenty.final_ability_scores.constitution == 18


def test_elian_runtime_and_fingerprint_share_2014_slots() -> None:
    for level in (1, 2, 10, 18, 20):
        runtime = build_elian_starweaver_2014(level)
        fingerprint = build_elian_starweaver_2014_combat_profile(level)
        assert {item.id: item.max_uses for item in runtime.resources} == dict(fingerprint.resources)
        assert runtime.ruleset == "2014"
        assert runtime.weapon_attack.weapon.mastery_property is None


def test_evoker_missing_mechanics_remain_explicitly_blocked_and_uncertified() -> None:
    profile = build_elian_starweaver_2014_profile(20)
    audits = {item.feature_id: item for item in profile.feature_audits}
    assert audits["wizard-spellcasting"].automated is False
    assert audits["potent-cantrip"].automated is False
    assert audits["empowered-evocation"].automated is True
    assert audits["overchannel"].automated is False
    assert audits["spell-mastery"].automated is False
    assert audits["signature-spells"].automated is False
    assert all(item.class_id != "wizard" for item in CERTIFIED_HERO_PROGRESSIONS)


def test_empowered_evocation_uses_generic_spell_id_damage_bonus_grant() -> None:
    nine = build_elian_starweaver_2014(9)
    ten = build_elian_starweaver_2014(10)
    assert nine.progression_features.spell_damage_bonus_grants == []
    assert len(ten.progression_features.spell_damage_bonus_grants) == 1
    grant = ten.progression_features.spell_damage_bonus_grants[0]
    assert grant.source_name == "Empowered Evocation"
    assert grant.ability == "intelligence"
    assert grant.eligible_spell_ids == ["fire-bolt", "fireball"]
    assert "disintegrate" not in grant.eligible_spell_ids


def test_potent_cantrip_reuses_generic_half_damage_on_success() -> None:
    five = build_elian_starweaver_2014(5)
    six = build_elian_starweaver_2014(6)

    five_poison = next(item for item in five.spell_save_actions if item.id == "poison-spray")
    six_poison = next(item for item in six.spell_save_actions if item.id == "poison-spray")

    assert five_poison.level == 0
    assert five_poison.success_damage == "none"
    assert six_poison.level == 0
    assert six_poison.success_damage == "half"

    audits = {item.feature_id: item for item in build_elian_starweaver_2014_profile(6).feature_audits}
    assert audits["potent-cantrip"].automated is True
