from __future__ import annotations

import logging

from app.domain.models import CombatantTemplate
from app.domain.modifiers import CombatModifier, ModifierKind

logger = logging.getLogger(__name__)


def opening_modifiers(template: CombatantTemplate) -> list[CombatModifier]:
    """Compile passive opening combat modifiers from declarative template data."""
    try:
        ward = template.progression_features.opening_targeting_ward
        if ward is None:
            return []
        return [CombatModifier(
            id=f"{template.id}:{ward.source_id}:opening",
            source_id=template.id,
            source_effect_id=ward.source_id,
            kind=ModifierKind.TARGETING_SAVE_GATE,
            save_ability=ward.save_ability,
            save_dc=ward.save_dc,
            ends_on_owner_attack=ward.ends_on_owner_attack,
        )]
    except Exception as exc:
        logger.exception("Failed to compile opening modifiers for %s.", template.id)
        raise RuntimeError("Opening combat modifiers could not be compiled.") from exc
