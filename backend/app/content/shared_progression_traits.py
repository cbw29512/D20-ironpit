from __future__ import annotations

from app.domain.models import CombatantTemplate
from app.domain.traits import CombatTrait


_PROGRESSION_TRAITS = {
    "cunning_action": CombatTrait.CUNNING_ACTION,
    "evasion": CombatTrait.EVASION,
}


def apply_progression_combat_traits(template: CombatantTemplate) -> CombatantTemplate:
    """Bind class progression flags to the same universal combat traits used by monsters."""
    traits = list(template.combat_traits)
    for field_name, trait in _PROGRESSION_TRAITS.items():
        if getattr(template.progression_features, field_name) and trait not in traits:
            traits.append(trait)
    return template.model_copy(update={"combat_traits": traits})
