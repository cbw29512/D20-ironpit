from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


LORE_BARD_2014_FEATURE_LEVELS: dict[int, tuple[str, ...]] = {
    3: ("cutting-words",),
    6: ("additional-magical-secrets",),
    14: ("peerless-skill",),
}


def lore_bard_2014_features(level: int) -> tuple[str, ...]:
    try:
        if level not in range(1, 21):
            raise ValueError("2014 College of Lore progression covers levels 1 through 20.")
        features: list[str] = []
        for current in range(1, level + 1):
            for feature in LORE_BARD_2014_FEATURE_LEVELS.get(current, ()):
                if feature not in features:
                    features.append(feature)
        return tuple(features)
    except Exception:
        logger.exception("Failed to compile 2014 College of Lore features through level %s.", level)
        raise
