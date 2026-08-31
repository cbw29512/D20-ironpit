from app.content.monster_bonus_action_source_audit import complete_monster_bonus_action_fingerprints
from app.content.monster_blood_hawk import build_blood_hawk
from app.content.monster_catalog import load_monster_rows
from app.content.monster_legendary_source_audit import complete_monster_legendary_fingerprints
from app.content.monster_limited_use_source_audit import complete_monster_limited_use_fingerprints
from app.content.monster_reaction_source_audit import complete_monster_reaction_fingerprints
from app.content.monster_saving_throws import complete_monster_saving_throws
from app.content.monster_source_audit import audit_monster_source
from app.content.monster_spellcasting_source_audit import complete_monster_spellcasting_fingerprints
from app.content.monster_trait_source_audit import complete_monster_trait_fingerprints
from app.content.unarmed_opportunity_profiles import complete_unarmed_opportunity_profiles


def _candidate():
    monsters = [build_blood_hawk()]
    monsters = complete_monster_trait_fingerprints(monsters)
    monsters = complete_monster_reaction_fingerprints(monsters)
    monsters = complete_monster_bonus_action_fingerprints(monsters)
    monsters = complete_monster_limited_use_fingerprints(monsters)
    monsters = complete_monster_legendary_fingerprints(monsters)
    monsters = complete_monster_spellcasting_fingerprints(monsters)
    monsters = complete_monster_saving_throws(monsters)
    return complete_unarmed_opportunity_profiles(monsters)[0]


def test_blood_hawk_candidate_passes_full_srd_source_audit() -> None:
    row = next(row for row in load_monster_rows() if row["name"] == "Blood Hawk")
    hawk = _candidate()

    assert audit_monster_source(hawk, row) == []
    assert hawk.source_trait_names == ["Pack Tactics"]
    assert hawk.weapon_attack.conditional_damage[0].trigger == "target_bloodied"
    assert hawk.weapon_attack.conditional_damage[0].mode == "replace_weapon"
