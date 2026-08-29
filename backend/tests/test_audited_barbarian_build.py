from app.content.audited_barbarian import build_rokhan_stonefury
from app.content.audited_barbarian_profile import build_rokhan_stonefury_profile
from app.content.build_audit import assert_character_build_raw_ready, audit_character_build


def test_rokhan_full_profile_passes_raw_audit() -> None:
    template = build_rokhan_stonefury()
    profile = build_rokhan_stonefury_profile()

    assert audit_character_build(profile, template) == []
    assert_character_build_raw_ready(profile, template)
    assert (template.armor_class, template.max_hp, template.initiative_bonus) == (13, 14, 1)
    assert template.rage_damage_bonus == 2
    assert {resource.id: resource.max_uses for resource in template.resources}["rage"] == 2


def test_rokhan_runtime_loadout_matches_audited_arena_weapons() -> None:
    template = build_rokhan_stonefury()
    profile = build_rokhan_stonefury_profile()

    runtime_weapon_ids = {
        template.weapon_attack.weapon.id,
        *(attack.weapon.id for attack in template.alternate_weapon_attacks),
    }
    audited_weapon_ids = {
        audit.runtime_attack_weapon_id
        for audit in profile.feature_audits
        if audit.runtime_attack_weapon_id
    }

    assert runtime_weapon_ids == {"greataxe", "handaxe"}
    assert audited_weapon_ids == runtime_weapon_ids
    assert template.weapon_attack.rage_eligible is True
    assert template.alternate_weapon_attacks[0].rage_eligible is True
