from __future__ import annotations

from app.domain.character_builds import CharacterBuildProfile
from app.domain.models import CombatantTemplate


def complete_character_identity_tags(
    template: CombatantTemplate,
    profile: CharacterBuildProfile,
) -> CombatantTemplate:
    """Carry build identity into universal combat tags without class-specific logic."""
    tags = {tag.casefold() for tag in template.creature_tags}
    tags.add(profile.species_id.casefold())
    return template.model_copy(update={
        "creature_type": template.creature_type or "humanoid",
        "creature_tags": sorted(tags),
    })
