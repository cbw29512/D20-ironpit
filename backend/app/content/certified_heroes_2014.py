from __future__ import annotations

import logging

from app.content.build_audit import assert_character_build_raw_ready
from app.content.character_resource_audit import assert_character_resources_raw_ready
from app.content.fighter_2014 import build_karnok_stoneward_2014
from app.content.fighter_2014_policy import assert_karnok_2014_profile_policy
from app.content.fighter_2014_profile import build_karnok_stoneward_2014_profile
from app.content.pregen_combat_audit import assert_pregen_combat_stats
from app.content.pregen_combat_profiles import build_pregen_combat_profiles
from app.content.unarmed_opportunity_profiles import complete_unarmed_opportunity_profiles
from app.domain.models import CombatantTemplate

logger = logging.getLogger(__name__)

Hero2014BuildKey = tuple[str, str, int, str]
BUILD_ID_2014 = "canonical-2014"


def _validated(level: int) -> tuple[Hero2014BuildKey, CombatantTemplate]:
    try:
        profile = build_karnok_stoneward_2014_profile(level)
        template = build_karnok_stoneward_2014(level)
        assert_karnok_2014_profile_policy(profile)
        assert_character_build_raw_ready(profile, template)
        combat_profile = build_pregen_combat_profiles().get(template.id)
        if combat_profile is None:
            raise ValueError(f"Certified 2014 hero {template.id} lacks a combat fingerprint.")
        assert_pregen_combat_stats(template, combat_profile)
        assert_character_resources_raw_ready(template, profile, combat_profile)
        template = complete_unarmed_opportunity_profiles([template])[0]
        return ("2014", profile.class_id, level, BUILD_ID_2014), template
    except Exception:
        logger.exception("2014 Karnok certification failed at level %s.", level)
        raise


def build_certified_hero_entries_2014() -> list[tuple[Hero2014BuildKey, CombatantTemplate]]:
    """Certify every 2014 Karnok level independently from 1 through 10."""
    try:
        return [_validated(level) for level in range(1, 11)]
    except Exception:
        logger.exception("2014 Fighter progression certification failed.")
        raise


def build_certified_hero_templates_2014() -> list[CombatantTemplate]:
    return [template for _, template in build_certified_hero_entries_2014()]
