"""One source-neutral spoken-language eligibility primitive shared by spells.

Only explicit speech and comprehension evidence can qualify a target.
"""
from __future__ import annotations

import logging

from app.domain.languages import LanguageProfile

logger = logging.getLogger(__name__)
_PRIMORDIAL = frozenset({"primordial", "aquan", "auran", "ignan", "terran"})


def _family(language: str) -> str:
    try:
        return "primordial" if language in _PRIMORDIAL else language
    except Exception:
        logger.exception("Failed to normalize spoken language %r.", language)
        raise


def spoken_language_understood(
    speaker: LanguageProfile, listener: LanguageProfile,
) -> bool:
    """Fail closed when neither source supplies a provable shared language."""
    try:
        if speaker.speaks_all:
            return listener.understands_all or bool(listener.understood)
        if listener.understands_all:
            return bool(speaker.spoken)
        spoken = {_family(item) for item in speaker.spoken}
        understood = {_family(item) for item in listener.understood}
        return bool(spoken & understood)
    except Exception:
        logger.exception("Could not evaluate source-backed spoken-language eligibility.")
        raise
