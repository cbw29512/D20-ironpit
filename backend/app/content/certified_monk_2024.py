from __future__ import annotations

from app.content.certified_hero_progression_model import CertifiedHeroProgression
from app.content.monk_open_hand_2024_profile import build_kael_stillwater_2024_profile
from app.content.monk_open_hand_2024_runtime import build_kael_stillwater_2024

CERTIFIED_MONK_2024 = CertifiedHeroProgression(
    class_id="monk",
    ruleset="2024",
    template_builder=build_kael_stillwater_2024,
    profile_level_builder=build_kael_stillwater_2024_profile,
    max_level=5,
)
