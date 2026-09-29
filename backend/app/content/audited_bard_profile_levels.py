from __future__ import annotations

import logging

from app.content.audited_bard_profile import build_lyra_silverstring_profile
from app.domain.character_builds import CharacterBuildProfile

logger = logging.getLogger(__name__)


def _profile(level: int) -> CharacterBuildProfile:
    try:
        return build_lyra_silverstring_profile(level)
    except Exception:
        logger.exception("Failed to build 2024 Lyra profile export at level %s.", level)
        raise


def build_lyra_silverstring_level1_profile() -> CharacterBuildProfile:
    return _profile(1)


def build_lyra_silverstring_level2_profile() -> CharacterBuildProfile:
    return _profile(2)


def build_lyra_silverstring_level3_profile() -> CharacterBuildProfile:
    return _profile(3)


def build_lyra_silverstring_level4_profile() -> CharacterBuildProfile:
    return _profile(4)


def build_lyra_silverstring_level5_profile() -> CharacterBuildProfile:
    return _profile(5)


def build_lyra_silverstring_level6_profile() -> CharacterBuildProfile:
    return _profile(6)


def build_lyra_silverstring_level7_profile() -> CharacterBuildProfile:
    return _profile(7)


def build_lyra_silverstring_level8_profile() -> CharacterBuildProfile:
    return _profile(8)

def build_lyra_silverstring_level9_profile() -> CharacterBuildProfile:
    return _profile(9)

def build_lyra_silverstring_level10_profile() -> CharacterBuildProfile:
    return _profile(10)


def build_lyra_silverstring_level11_profile() -> CharacterBuildProfile:
    return _profile(11)


def build_lyra_silverstring_level12_profile() -> CharacterBuildProfile:
    return _profile(12)


def build_lyra_silverstring_level13_profile() -> CharacterBuildProfile:
    return _profile(13)


def build_lyra_silverstring_level14_profile() -> CharacterBuildProfile:
    return _profile(14)


def build_lyra_silverstring_level15_profile() -> CharacterBuildProfile:
    return _profile(15)


def build_lyra_silverstring_level16_profile() -> CharacterBuildProfile:
    return _profile(16)


def build_lyra_silverstring_level17_profile() -> CharacterBuildProfile:
    return _profile(17)


def build_lyra_silverstring_level18_profile() -> CharacterBuildProfile:
    return _profile(18)
