from app.content.certified_hero_progressions import CERTIFIED_HERO_PROGRESSIONS
from app.content.paladin_devotion_2014_combat_profile import build_aurelia_brightshield_2014_combat_profile
from app.content.paladin_devotion_2014_profile import build_aurelia_brightshield_2014_profile
from app.content.paladin_devotion_2014_runtime import build_aurelia_brightshield_2014
from app.domain.size import CreatureSize


def test_level_thirteen_is_prepared_without_advancing_certification_boundary() -> None:
    level_twelve = build_aurelia_brightshield_2014_profile(12)
    level_thirteen = build_aurelia_brightshield_2014_profile(13)
    runtime = build_aurelia_brightshield_2014(13)
    fingerprint = build_aurelia_brightshield_2014_combat_profile(13)

    assert level_thirteen.character_name == level_twelve.character_name == "Aurelia Brightshield"
    assert level_thirteen.species_id == level_twelve.species_id == "human"
    assert level_thirteen.background_id == level_twelve.background_id == "noble"
    assert level_thirteen.subclass_id == level_twelve.subclass_id == "oath-devotion"
    assert level_thirteen.class_equipment == level_twelve.class_equipment
    assert level_thirteen.advancement_increases == level_twelve.advancement_increases
    assert level_thirteen.final_ability_scores == level_twelve.final_ability_scores

    expected_resources = {
        "lay-on-hands": 65,
        "spell-slot-1": 4,
        "spell-slot-2": 3,
        "spell-slot-3": 3,
        "spell-slot-4": 1,
        "channel-divinity": 1,
    }
    assert {item.id: item.max_uses for item in runtime.resources} == expected_resources
    assert dict(fingerprint.resources) == expected_resources

    audit = next(item for item in level_thirteen.feature_audits if item.feature_id == "devotion-oath-spells-4")
    assert audit.automated is False

    certified = next(
        item for item in CERTIFIED_HERO_PROGRESSIONS
        if item.class_id == "paladin" and item.template_builder is build_aurelia_brightshield_2014
    )
    assert certified.max_level == 12


def test_level_thirteen_guardian_of_faith_reuses_persistent_hazard_schema() -> None:
    runtime = build_aurelia_brightshield_2014(13)
    assert len(runtime.persistent_hazard_actions) == 1
    guardian = runtime.persistent_hazard_actions[0]

    assert guardian.id == "guardian-of-faith"
    assert guardian.name == "Guardian of Faith"
    assert guardian.level == 4
    assert guardian.action_cost == "action"
    assert guardian.cast_range_ft == 30
    assert guardian.duration_rounds == 4800
    assert guardian.footprint_size == CreatureSize.LARGE
    assert guardian.trigger_radius_ft == 10
    assert guardian.save_ability == "dexterity"
    assert guardian.dc == 16
    assert guardian.failure_damage == 20
    assert guardian.success_damage == 10
    assert guardian.damage_type == "radiant"
    assert guardian.max_total_damage == 60
