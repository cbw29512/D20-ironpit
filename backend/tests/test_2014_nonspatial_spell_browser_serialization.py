"""Parity proof: persistent spell source fields survive browser serialization.

The normal 2014 Hero certification installs the backend package only; the
repository's scripts directory is not installed as a Python package.
Resolve the project root explicitly inside this serializer-specific test.
"""
from __future__ import annotations

import logging
from pathlib import Path
import sys

from app.content.cleric_life_2014_runtime import build_seraphine_dawnshield_2014

logger = logging.getLogger(__name__)


def test_2014_spiritual_weapon_browser_card_is_nonspatial() -> None:
    try:
        # Repo-scoped serializer, not part of the pip-installed backend package.
        repo_root = str(Path(__file__).resolve().parents[2])
        if repo_root not in sys.path:
            sys.path.insert(0, repo_root)
        from scripts.browser_template_serializer import template_row

        hero = build_seraphine_dawnshield_2014(3)
        before = hero.model_dump_json()
        row = template_row(hero)["persistent_spell_attack_actions"][0]

        assert row["id"] == "spiritual-weapon"
        assert row["spatialMode"] == "nonspatial"
        assert row["durationRounds"] == 10
        assert row["attack"]["range"] == 60
        assert row["attack"]["actionCost"] == "bonus_action"
        assert row["attack"]["damageDiceCount"] == 1
        assert row["attack"]["damageDiceSize"] == 8
        assert row["attack"]["damageType"] == "force"
        assert hero.model_dump_json() == before
    except Exception:
        logger.exception("2014 persistent spell browser serialization lost typed fields.")
        raise
