from __future__ import annotations

from app.domain.models import CombatantTemplate
from app.domain.modifiers import CombatModifier, ModifierKind


def opening_modifiers(template: CombatantTemplate) -> list[CombatModifier]:
    """Compile passive opening combat modifiers from declarative template data."""
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
