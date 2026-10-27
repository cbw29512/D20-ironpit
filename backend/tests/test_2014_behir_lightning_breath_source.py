"""Source-proof regression for 2014 Behir Lightning Breath."""
from __future__ import annotations

from app.content.monster_source_2014 import load_monster_source_2014
from app.content.monster_source_line_save_recharge_2014 import (
    source_proven_behir_lightning_breath_2014,
)


def test_behir_lightning_breath_source_proof_extracts_exact_parameters() -> None:
    sources = load_monster_source_2014()
    behir = next(s for s in sources if s.name == "Behir")
    proven = source_proven_behir_lightning_breath_2014(behir)
    assert proven is not None
    assert proven.id == "lightning-breath"
    assert proven.save_ability == "dexterity"
    assert proven.dc == 16
    assert proven.area is not None
    assert proven.area.shape == "line"
    assert proven.area.length_ft == 20
    assert proven.area.width_ft == 5
    assert proven.damage_components[0].dice_count == 12
    assert proven.damage_components[0].dice_size == 10
    assert proven.damage_components[0].damage_type == "lightning"
    assert proven.half_on_success is True
