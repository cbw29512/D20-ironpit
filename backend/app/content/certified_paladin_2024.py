from __future__ import annotations

from app.content.certified_hero_progression_model import CertifiedHeroProgression
from app.content.paladin_devotion_2024_profile import build_aurelia_brightshield_2024_profile
from app.content.paladin_devotion_2024_runtime import build_aurelia_brightshield_2024

CERTIFIED_PALADIN_2024 = CertifiedHeroProgression(
    class_id="paladin",
    ruleset="2024",
    template_builder=build_aurelia_brightshield_2024,
    profile_level_builder=build_aurelia_brightshield_2024_profile,
    max_level=14,
)
