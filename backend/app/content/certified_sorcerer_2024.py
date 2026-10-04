from __future__ import annotations

from app.content.certified_hero_progression_model import CertifiedHeroProgression
from app.content.sorcerer_draconic_2024_profile import build_nyra_emberveil_2024_profile
from app.content.sorcerer_draconic_2024_runtime import build_nyra_emberveil_2024

CERTIFIED_SORCERER_2024 = CertifiedHeroProgression(
    class_id="sorcerer",
    ruleset="2024",
    template_builder=build_nyra_emberveil_2024,
    profile_level_builder=build_nyra_emberveil_2024_profile,
    max_level=20,
)
