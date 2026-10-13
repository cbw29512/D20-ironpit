from __future__ import annotations

from app.content.monster_source_2014 import SourceMonster2014


def supports_rock_catching_reaction_2014(monster: SourceMonster2014) -> bool:
    """Require 2014 source evidence before binding the shared Reaction."""
    return (
        monster.reaction_names == ["Rock Catching"]
        and bool(monster.source_reactions)
        and "DC 10" in monster.source_reactions
        and "Dexterity" in monster.source_reactions
    )
