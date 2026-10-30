"""2014 Sleep source contract: data is verified, runtime remains fail-closed."""
from __future__ import annotations

from app.content.monster_sleep_spell_source_2014 import sleep_spell_rules_2014
from app.content.monster_innate_source_2014 import innate_spells_2014
from app.content.monster_source_2014 import load_monster_source_2014


def test_sleep_source_preserves_raw_2014_hp_pool_semantics() -> None:
    data = sleep_spell_rules_2014()
    assert (data["pool_dice_count"], data["pool_dice_size"]) == (5, 8)
    assert (data["range_ft"], data["area_radius_ft"], data["duration_rounds"]) == (90, 20, 10)
    assert data["target_order"] == "ascending_current_hp"
    assert data["requires_full_current_hp_coverage"] is True
    assert data["excluded_creature_types"] == ["undead"]
    assert data["excluded_condition_immunities"] == ["charmed"]
    assert data["ends_on_damage"] is True
    assert data["allowed_removal_action_ids"] == ["wake-sleeper"]


def test_dust_mephit_printed_sleep_access_is_independent_of_effect_rules() -> None:
    monster = next(m for m in load_monster_source_2014() if m.id == "dust-mephit")
    spells = [s for s in innate_spells_2014(monster) if s.get("id") == "sleep"]
    assert len(spells) == 1
    assert spells[0].get("usage") == "per_day"
    assert spells[0].get("uses_per_day") == 1
    assert sleep_spell_rules_2014()["spell_id"] == spells[0]["id"]
