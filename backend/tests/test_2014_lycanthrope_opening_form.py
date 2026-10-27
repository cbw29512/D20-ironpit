"""Permanent source-proof regression for 2014 lycanthrope opening form.

Does not claim admission or clear Shapechanger/extra-action blockers.
"""
from __future__ import annotations

from app.content.monster_lycanthrope_opening_form_2014 import (
    verified_lycanthrope_beast_opening_form_2014,
)
from app.content.monster_source_2014 import SourceMonster2014


def test_werewolf_extracts_wolf_beast_form() -> None:
    monster = SourceMonster2014.from_id("werewolf")
    assert verified_lycanthrope_beast_opening_form_2014(monster) == "wolf"


def test_werebear_extracts_bear_beast_form() -> None:
    monster = SourceMonster2014.from_id("werebear")
    assert verified_lycanthrope_beast_opening_form_2014(monster) == "large-bear"


def test_mutated_clause_fails_closed() -> None:
    monster = SourceMonster2014.from_id("werewolf")
    # Mutate the source in memory; proof must reject.
    mutated = monster.model_copy(update={"source_traits": (monster.source_traits or "").replace("wolf", "cat")})
    assert verified_lycanthrope_beast_opening_form_2014(mutated) is None


def test_non_lycanthrope_returns_none() -> None:
    monster = SourceMonster2014.from_id("goblin")
    assert verified_lycanthrope_beast_opening_form_2014(monster) is None
