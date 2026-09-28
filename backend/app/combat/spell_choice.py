from __future__ import annotations

from dataclasses import dataclass

from app.combat.spell_area import AreaPlacement
from app.domain.spell_cast_modifiers import ResourceBackedSpellRangeModifier
from app.domain.alternate_spell_casts import AlternateSpellCastGrant
from app.domain.spell_damage_maximizers import SpellDamageMaximizerGrant
from app.domain.spells import SpellSaveAction


@dataclass(frozen=True)
class SpellChoice:
    action: SpellSaveAction
    slot_level: int
    target_ids: tuple[str, ...]
    placement: AreaPlacement | None = None
    expected_damage: float = 0.0
    range_modifier: ResourceBackedSpellRangeModifier | None = None
    alternate_cast: AlternateSpellCastGrant | None = None
    damage_maximizer: SpellDamageMaximizerGrant | None = None
