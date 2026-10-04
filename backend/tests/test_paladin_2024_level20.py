from __future__ import annotations

import logging

from app.content.build_audit import assert_character_build_raw_ready
from app.content.character_resource_audit import assert_character_resources_raw_ready
from app.content.paladin_devotion_2024_combat_profile import build_aurelia_2024_combat_profiles
from app.content.paladin_devotion_2024_profile import build_aurelia_brightshield_2024_profile
from app.content.paladin_devotion_2024_runtime import build_aurelia_brightshield_2024
from app.content.pregen_combat_audit import assert_pregen_combat_stats

logger = logging.getLogger(__name__)


def test_level_twenty_binds_2024_holy_nimbus() -> None:
    try:
        hero = build_aurelia_brightshield_2024(20)
        previous = build_aurelia_brightshield_2024(19)
        profile = build_aurelia_brightshield_2024_profile(20)

        assert hero.name == previous.name
        assert hero.level == 20
        assert profile.final_ability_scores is not None
        assert profile.final_ability_scores.charisma == 20
        assert profile.final_ability_scores.strength == 20
        assert hero.max_hp == 164
        assert hero.skill_bonuses["persuasion"] == 11

        protection = hero.progression_features.friendly_saving_throw_aura
        assert protection is not None
        assert protection.radius_ft == 30
        assert protection.flat_bonus == 5

        nimbus = next(item for item in hero.timed_self_buff_actions if item.id == "holy-nimbus")
        assert nimbus.action_cost == "bonus_action"
        assert nimbus.resource_id == "holy-nimbus"
        assert nimbus.duration_rounds == 100
        assert nimbus.start_turn_emanation_damage is not None
        assert nimbus.start_turn_emanation_damage.fixed_damage == 11
        assert nimbus.start_turn_emanation_damage.radius_ft == 30
        grant = nimbus.saving_throw_advantage_grants[0]
        assert grant.requires_spell_effect is False
        assert grant.source_creature_types == ["fiend", "undead"]

        restore = next(item for item in hero.resource_conversion_actions if item.id == "holy-nimbus-restore")
        assert restore.action_cost == "none"
        assert restore.source_resource_id == "spell-slot-5"
        assert restore.target_resource_id == "holy-nimbus"
        assert restore.requires_target_empty is True

        resources = {item.id: item.max_uses for item in hero.resources}
        assert resources["lay-on-hands"] == 100
        assert resources["spell-slot-5"] == 2
        assert resources["holy-nimbus"] == 1
        assert resources["boon-combat-prowess"] == 1

        audits = {item.feature_id: item for item in profile.feature_audits}
        assert audits["holy-nimbus"].combat_relevant is True
        assert audits["holy-nimbus"].automated is True

        fingerprint = next(item for item in build_aurelia_2024_combat_profiles() if item.level == 20)
        assert fingerprint.max_hp == 164
        assert ("lay-on-hands", 100) in fingerprint.resources
        assert ("holy-nimbus", 1) in fingerprint.resources

        assert_character_build_raw_ready(profile, hero)
        assert_pregen_combat_stats(hero, fingerprint)
        assert_character_resources_raw_ready(hero, profile, fingerprint)
    except Exception:
        logger.exception("Paladin 20 Holy Nimbus certification failed.")
        raise
