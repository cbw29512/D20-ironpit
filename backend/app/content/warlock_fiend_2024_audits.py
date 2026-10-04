from __future__ import annotations

import logging

from app.content.warlock_fiend_2024_high_audits import build_varek_fiend_2024_high_audits
from app.content.warlock_fiend_2024_low_audits import build_varek_fiend_2024_low_audits
from app.domain.character_builds import FeatureAudit

logger = logging.getLogger(__name__)


def build_varek_fiend_2024_audits(level: int) -> list[FeatureAudit]:
    try:
        audits = build_varek_fiend_2024_low_audits(level)
        audits.extend(build_varek_fiend_2024_high_audits(level))
        return audits
    except Exception:
        logger.exception("Failed to build Varek's 2024 Fiend audits at level %s.", level)
        raise
