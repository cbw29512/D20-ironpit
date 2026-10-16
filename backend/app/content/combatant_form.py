"""Validated form boundary shared by official content and future homebrew editors.

The form is NOT another combat engine. It compiles into the existing
CombatantTemplate and all fight mutations remain in CombatantState.
"""
from __future__ import annotations

import logging
from collections.abc import Mapping
from typing import Any

from pydantic import ValidationError

from app.content.capability_compiler import compile_combatant
from app.domain.capabilities import CombatantDefinition
from app.domain.models import CombatantTemplate

logger = logging.getLogger(__name__)


def compile_combatant_form(values: Mapping[str, Any]) -> CombatantTemplate:
    """Validate submitted declarative fields and reuse the canonical compiler."""
    try:
        if not isinstance(values, Mapping):
            raise ValueError("Combatant form must be a mapping.")
        # Pydantic's existing default ignores unknown keys; at an editor
        # boundary that could silently erase a homebrew combat mechanic.
        unknown = set(values) - set(CombatantDefinition.model_fields)
        if unknown:
            raise ValueError(
                "Unrecognized combatant form fields: " + ", ".join(sorted(unknown))
            )
        definition = CombatantDefinition.model_validate(dict(values))
        if definition.schema_version != 1:
            raise ValueError("Unsupported combatant form schema version.")
        # No special case for homebrew, pregen, or monster names.
        return compile_combatant(definition)
    except (ValueError, ValidationError):
        logger.exception("Invalid combatant form: %s", values.get("id", "<unknown>") if isinstance(values, Mapping) else "<invalid>")
        raise
    except Exception:
        logger.exception("Combatant form compilation failed.")
        raise
