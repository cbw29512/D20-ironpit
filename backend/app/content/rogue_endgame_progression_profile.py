from __future__ import annotations

from app.content.audited_rogue_profile import _feature
from app.content.canonical_progression import advance_profile_data
from app.content.rogue_high_progression_profile import build_mara_quickstep_level12_profile
from app.domain.character_builds import CharacterBuildProfile


def build_mara_quickstep_level13_profile() -> CharacterBuildProfile:
    """Level 13 inherits level 12; Use Magic Device is loadout-dependent."""
    try:
        previous = build_mara_quickstep_level12_profile()
        data = advance_profile_data(previous, 13)
        data.update(
            feature_audits=[
                *data["feature_audits"],
                _feature(
                    "thief-use-magic-device", "Use Magic Device", "subclass",
                    combat_relevant=False, automated=False,
                    notes=(
                        "Mara's certified loadout has no qualifying attunement overflow, "
                        "charge-using magic item, or Spell Scroll. Preserve the feature without "
                        "faking item behavior; treasure integration can activate it later."
                    ),
                ).model_dump(),
            ],
            source_references=[
                *data["source_references"],
                "Basic Rules 2024: Thief 13 — Use Magic Device",
            ],
        )
        return CharacterBuildProfile.model_validate(data)
    except Exception as exc:
        raise RuntimeError("Mara Rogue level 13 profile could not be created.") from exc
