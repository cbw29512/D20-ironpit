from __future__ import annotations

from app.content.certified_hero_progression_model import CertifiedHeroProgression
from app.content.warlock_fiend_2024_profile import build_varek_ashenmark_2024_profile
from app.content.warlock_fiend_2024_runtime import build_varek_ashenmark_2024

CERTIFIED_WARLOCK_2024 = CertifiedHeroProgression(
    class_id="warlock",
    ruleset="2024",
    template_builder=build_varek_ashenmark_2024,
    profile_level_builder=build_varek_ashenmark_2024_profile,
    max_level=20,
)
