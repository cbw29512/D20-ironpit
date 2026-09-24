from __future__ import annotations

import logging

from pydantic import BaseModel, Field, model_validator

from app.domain.actions import AbilityName, DamageTypeName

logger = logging.getLogger(__name__)


class SpellDamageBonusGrant(BaseModel):
    """Source-neutral ability-modifier bonus applied once to one qualifying spell damage roll."""

    source_id: str = Field(min_length=1)
    source_name: str = Field(min_length=1)
    ability: AbilityName
    eligible_spell_ids: list[str] = Field(default_factory=list)
    eligible_damage_types: list[DamageTypeName] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_matchers(self) -> "SpellDamageBonusGrant":
        try:
            if not self.eligible_spell_ids and not self.eligible_damage_types:
                raise ValueError("Spell damage bonus requires at least one spell-id or damage-type matcher.")
            if len(set(self.eligible_spell_ids)) != len(self.eligible_spell_ids):
                raise ValueError("Spell damage bonus spell IDs must be unique.")
            if len(set(self.eligible_damage_types)) != len(self.eligible_damage_types):
                raise ValueError("Spell damage bonus damage types must be unique.")
            return self
        except ValueError:
            raise
        except Exception as exc:
            logger.exception("Spell damage bonus schema validation failed for %s.", self.source_id)
            raise RuntimeError("Spell damage bonus grant could not be validated.") from exc
