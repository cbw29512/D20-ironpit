"""2014 prepared caster source proof for the complete ten-spell Priest.

Data schema: the immutable card owns spellcasting level, ability, spell
IDs/names/levels, exact slot counts, DC, attack bonus and printed paragraphs.
Fight state: normal generic slot resources and spell effect lifecycles.
A changed source text, spell, slot or rider is rejected rather than guessed.
"""
from __future__ import annotations

import logging
import re

from app.content.monster_source_2014 import SourceMonster2014
from app.content.monster_source_sections_2014 import source_sections_2014

logger = logging.getLogger(__name__)

# This checks the *entire* printed heading and all unheaded continuations.
# Capturing the printed subject avoids monster ID/name runtime branching.
_PRINTED = re.compile(
    r"The (?P<actor>[a-z][a-z' -]*) is a 5th-level spellcaster\. "
    r"Its spellcasting ability is Wisdom \(spell save DC (?P<dc>\d+), "
    r"\+(?P<attack>\d+) to hit with spell attacks\)\. "
    r"The (?P=actor) has the following cleric spells prepared: "
    r"Cantrips \(at will\): light, sacred flame, thaumaturgy "
    r"1st level \(4 slots\): cure wounds, guiding bolt, sanctuary "
    r"2nd level \(3 slots\): lesser restoration, spiritual weapon "
    r"3rd level \(2 slots\): dispel magic, spirit guardians",
    re.IGNORECASE,
)

_KNOWN = (
    ("light", "light", 0),
    ("sacred-flame", "sacred flame", 0),
    ("thaumaturgy", "thaumaturgy", 0),
    ("cure-wounds", "cure wounds", 1),
    ("guiding-bolt", "guiding bolt", 1),
    ("sanctuary", "sanctuary", 1),
    ("lesser-restoration", "lesser restoration", 2),
    ("spiritual-weapon", "spiritual weapon", 2),
    ("dispel-magic", "dispel magic", 3),
    ("spirit-guardians", "spirit guardians", 3),
)


def source_proves_priest_spellcasting_2014(monster: SourceMonster2014) -> bool:
    """Fail closed if the 2014 spell package no longer matches printed RAW."""
    try:
        if "Spellcasting" not in monster.trait_names:
            return False
        source = monster.spellcasting
        if not isinstance(source, dict) or source.get("source_complete") is not True:
            return False
        if (
            source.get("caster_level") != 5
            or source.get("ability") != "wisdom"
            or source.get("slots") != {"1": 4, "2": 3, "3": 2}
            or source.get("unsupported_text") is not None
        ):
            return False
        dc, attack = source.get("save_dc"), source.get("attack_bonus")
        if type(dc) is not int or type(attack) is not int:
            return False
        if (dc, attack) != (13, 5):
            return False
        spells = source.get("spells")
        if not isinstance(spells, list) or len(spells) != len(_KNOWN):
            return False
        if any(
            not isinstance(row, dict) or set(row) != {"id", "name", "level"}
            for row in spells
        ):
            return False
        if tuple((row["id"], row["name"], row["level"]) for row in spells) != _KNOWN:
            return False
        wisdom = monster.abilities.get("wis")
        if type(wisdom) is not int or not 1 <= wisdom <= 30:
            return False

        printed = source_sections_2014(
            monster.source_traits, include_continuations=True,
        ).get("Spellcasting", "")
        match = _PRINTED.fullmatch(" ".join(printed.replace("’", "'").split()))
        return bool(
            match and (int(match["dc"]), int(match["attack"])) == (dc, attack)
        )
    except Exception:
        logger.exception("2014 complete Priest spellcasting proof failed.")
        raise
