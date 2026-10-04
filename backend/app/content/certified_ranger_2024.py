from __future__ import annotations

from app.content.certified_hero_progression_model import CertifiedHeroProgression
from app.content.ranger_hunter_2024_profile import build_rowan_ashtrail_2024_profile
from app.content.ranger_hunter_2024_runtime import build_rowan_ashtrail_2024

CERTIFIED_RANGER_2024 = CertifiedHeroProgression(
    class_id="ranger",
    ruleset="2024",
    template_builder=build_rowan_ashtrail_2024,
    profile_level_builder=build_rowan_ashtrail_2024_profile,
    max_level=1,
)
