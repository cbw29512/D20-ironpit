from __future__ import annotations

import logging

from app.domain.class_loadouts import CanonicalSpellChoice


def spell_choice(
    spell_id: str,
    name: str,
    role: str,
    *capabilities: str,
    spell_level: int = 1,
    min_character_level: int = 1,
    always_prepared_from_level: int | None = None,
) -> CanonicalSpellChoice:
    try:
        return CanonicalSpellChoice(
            id=spell_id,
            name=name,
            spell_level=spell_level,
            min_character_level=min_character_level,
            always_prepared_from_level=always_prepared_from_level,
            role=role,
            required_capabilities=list(capabilities),
        )
    except Exception:
        logging.getLogger(__name__).exception("Failed to compile canonical spell choice %s.", spell_id)
        raise
