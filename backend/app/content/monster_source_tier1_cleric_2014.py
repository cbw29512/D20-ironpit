"""Prove a complete low-level prepared Cleric source without creature-name dispatch.

Schema: source Spellcasting supplies caster level, spell IDs/levels, slots,
Wisdom save DC and attack bonus. Immutable source stays on the card.
State: the existing generic spell-slot resources spend uses per fight; the
existing shared combat spell resolvers own save, buff, healing and targeting.
Only Light and Thaumaturgy are noncombat in the fixed Iron Pit arena.
"""
from __future__ import annotations

import logging

from app.content.monster_source_2014 import SourceMonster2014
from app.content.monster_source_sections_2014 import source_sections_2014

logger = logging.getLogger(__name__)

# Exact supported 2014 source grammar, not a card/monster identity map.
# A changed or additional spell, tier, slot, or outcome must fail closed.
_KNOWN = (
    ("light", "light", 0),
    ("sacred-flame", "sacred flame", 0),
    ("thaumaturgy", "thaumaturgy", 0),
    ("bless", "bless", 1),
    ("cure-wounds", "cure wounds", 1),
    ("sanctuary", "sanctuary", 1),
)


def source_proves_tier1_cleric_spells_2014(monster: SourceMonster2014) -> bool:
    """Prove the entire source paragraph and structured spell/slot facts."""
    try:
        source = monster.spellcasting
        if "Spellcasting" not in monster.trait_names:
            return False
        if not isinstance(source, dict) or source.get("source_complete") is not True:
            return False
        if (source.get("caster_level") != 1
                or source.get("ability") != "wisdom"
                or source.get("slots") != {"1": 3}):
            return False
        dc, attack = source.get("save_dc"), source.get("attack_bonus")
        if type(dc) is not int or type(attack) is not int or dc < 1:
            return False
        spells = source.get("spells")
        if not isinstance(spells, list) or len(spells) != len(_KNOWN):
            return False
        if [(item.get("id"), item.get("name"), item.get("level"))
                for item in spells if isinstance(item, dict)] != list(_KNOWN):
            return False
        if any(not isinstance(item, dict) or set(item) != {"id", "name", "level"}
               for item in spells):
            return False

        # This exact complete clause includes the unheaded Cantrips/1st-level
        # paragraphs. Another effect appended to either paragraph is rejected.
        name = monster.name.casefold().strip()
        expected = (
            f"The {name} is a 1st-level spellcaster. Its spellcasting "
            f"ability is Wisdom (spell save DC {dc}, +{attack} to hit "
            f"with spell attacks). The {name} has following cleric "
            "spells prepared: Cantrips (at will): light, sacred flame, "
            "thaumaturgy 1st level (3 slots): bless, cure wounds, sanctuary"
        )
        section = source_sections_2014(
            monster.source_traits, include_continuations=True,
        ).get("Spellcasting", "")
        return " ".join(section.casefold().split()) == expected.casefold()
    except Exception:
        logger.exception("Failed full-source Tier-1 Cleric spell proof.")
        raise
