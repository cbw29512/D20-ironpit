from __future__ import annotations

from app.content.certified_hero_progression_model import CertifiedHeroProgression
from app.content.wizard_evoker_2024_profile import build_elian_starweaver_2024_profile
from app.content.wizard_evoker_2024_runtime import build_elian_starweaver_2024

CERTIFIED_WIZARD_2024 = CertifiedHeroProgression(
    class_id="wizard",
    ruleset="2024",
    template_builder=build_elian_starweaver_2024,
    profile_level_builder=build_elian_starweaver_2024_profile,
    max_level=20,
)
