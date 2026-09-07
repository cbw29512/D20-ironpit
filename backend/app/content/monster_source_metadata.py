from __future__ import annotations

from app.content.monster_bonus_action_source_audit import complete_monster_bonus_action_fingerprints
from app.content.monster_legendary_source_audit import complete_monster_legendary_fingerprints
from app.content.monster_limited_use_source_audit import complete_monster_limited_use_fingerprints
from app.content.monster_reaction_source_audit import complete_monster_reaction_fingerprints
from app.content.monster_saving_throws import complete_monster_saving_throws
from app.content.monster_spellcasting_source_audit import complete_monster_spellcasting_fingerprints
from app.content.monster_trait_source_audit import complete_monster_trait_fingerprints
from app.content.unarmed_opportunity_profiles import complete_unarmed_opportunity_profiles
from app.domain.models import CombatantTemplate


def complete_monster_source_metadata(templates: list[CombatantTemplate]) -> list[CombatantTemplate]:
    """Derive auditable SRD metadata once after any monster capability source compiles."""
    result = complete_monster_trait_fingerprints(templates)
    result = complete_monster_reaction_fingerprints(result)
    result = complete_monster_bonus_action_fingerprints(result)
    result = complete_monster_limited_use_fingerprints(result)
    result = complete_monster_legendary_fingerprints(result)
    result = complete_monster_spellcasting_fingerprints(result)
    result = complete_monster_saving_throws(result)
    return complete_unarmed_opportunity_profiles(result)
