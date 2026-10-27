"""Source-verified tests for 2014 lycanthrope opening beast form."""
from __future__ import annotations

import pytest

from app.content.monster_lycanthrope_opening_form_2014 import (
    opening_beast_form_id_2014,
    verified_lycanthrope_shapechanger_2014,
)
from app.content.monster_source_2014 import load_monster_source_2014


@pytest.mark.parametrize("monster_id", [
    "werebear",
    "wereboar",
    "wererat",
    "weretiger",
    "werewolf",
])
def test_verified_lycanthropes_open_in_beast_form(monster_id: str) -> None:
    monsters = {m.id: m for m in load_monster_source_2014()}
    monster = monsters[monster_id]
    assert verified_lycanthrope_shapechanger_2014(monster) is True
    assert opening_beast_form_id_2014(monster) == "beast"


def test_non_lycanthrope_fails_closed() -> None:
    monsters = {m.id: m for m in load_monster_source_2014()}
    assert verified_lycanthrope_shapechanger_2014(monsters["imp"]) is False
    with pytest.raises(ValueError):
        opening_beast_form_id_2014(monsters["imp"])
