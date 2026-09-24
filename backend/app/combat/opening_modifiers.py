from __future__ import annotations

import logging

from app.combat.spell_modifiers import build_spell_modifier
from app.domain.models import CombatantTemplate
from app.domain.modifiers import CombatModifier, ModifierKind

logger = logging.getLogger(__name__)


def opening_modifiers(template: CombatantTemplate) -> list[CombatModifier]:
    """Compile passive opening combat modifiers from declarative template data."""
    try:
        features = template.progression_features
        modifiers: list[CombatModifier] = []
        ward = features.opening_targeting_ward
        if ward is not None:
            modifiers.append(CombatModifier(
                id=f"{template.id}:{ward.source_id}:opening",
                source_id=template.id,
                source_effect_id=ward.source_id,
                kind=ModifierKind.TARGETING_SAVE_GATE,
                save_ability=ward.save_ability,
                save_dc=ward.save_dc,
                ends_on_owner_attack=ward.ends_on_owner_attack,
            ))
        for grant in features.saving_throw_advantage_grants:
            for ability in grant.abilities:
                modifiers.append(CombatModifier(
                    id=f"{template.id}:{grant.source_id}:save-advantage:{ability}",
                    source_id=template.id,
                    source_effect_id=grant.source_id,
                    source_name=grant.source_name,
                    kind=ModifierKind.SAVING_THROW_ADVANTAGE,
                    save_ability=ability,
                    requires_magical_effect=grant.requires_magical_effect,
                    against_effect_tags=list(grant.against_effect_tags),
                ))
        for grant in features.passive_modifier_grants:
            for index, effect in enumerate(grant.modifier_effects):
                modifier = build_spell_modifier(
                    template.id,
                    template.id,
                    grant.source_id,
                    effect,
                    index,
                )
                modifier.source_name = grant.source_name
                modifiers.append(modifier)
        return modifiers
    except Exception as exc:
        logger.exception("Failed to compile opening modifiers for %s.", template.id)
        raise RuntimeError("Opening combat modifiers could not be compiled.") from exc
