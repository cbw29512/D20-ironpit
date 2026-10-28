"""Source proof for 2014 Damage Transfer foundation."""
from __future__ import annotations

from app.content.monster_source_2014 import load_monster_source_2014
from app.content.monster_damage_transfer_source_2014 import source_proves_damage_transfer_2014


def test_cloaker_and_rug_damage_transfer_source_matches() -> None:
    monsters = {m.name: m for m in load_monster_source_2014()}
    cloaker = monsters["Cloaker"]
    rug = monsters["Rug of Smothering"]
    assert source_proves_damage_transfer_2014(cloaker)
    assert source_proves_damage_transfer_2014(rug)
    # Renamed or missing fails closed
    other = next(m for m in monsters.values() if m.name == "Goblin")
    assert not source_proves_damage_transfer_2014(other)
