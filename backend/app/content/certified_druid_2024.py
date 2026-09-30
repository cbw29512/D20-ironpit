from __future__ import annotations

from app.content.audited_druid import build_thalen_greenbough_level
from app.content.audited_druid_profile import build_thalen_greenbough_profile
from app.content.certified_hero_progression_model import CertifiedHeroProgression


CERTIFIED_DRUID_2024 = CertifiedHeroProgression(
    class_id="druid",
    ruleset="2024",
    template_builder=build_thalen_greenbough_level,
    profile_level_builder=build_thalen_greenbough_profile,
    max_level=13,
)
