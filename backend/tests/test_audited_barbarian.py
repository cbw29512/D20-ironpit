from app.content.audited_barbarian import build_rokhan_stonefury
from app.content.audited_barbarian_profile import build_rokhan_stonefury_profile
from app.content.build_audit import assert_character_build_raw_ready, audit_character_build


def test_rokhan_full_profile_passes_legal_build_audit() -> None:
    template = build_rokhan_stonefury()
    profile = build_rokhan_stonefury_profile()

    assert audit_character_build(profile, template) == []
    assert_character_build_raw_ready(profile, template)
    assert template.archetype == "Barbarian"
    assert template.level == 1
    assert template.max_hp == 14
    assert template.armor_class == 13
    assert template.rage_damage_bonus == 2
    assert {resource.id: resource.max_uses for resource in template.resources}["rage"] == 2


def test_rokhan_arena_loadout_exposes_greataxe_and_handaxe() -> None:
    template = build_rokhan_stonefury()
    runtime_weapon_ids = {
        template.weapon_attack.weapon.id,
        *(attack.weapon.id for attack in template.alternate_weapon_attacks),
    }

    assert runtime_weapon_ids == {"greataxe", "handaxe"}
    assert template.weapon_attack.rage_eligible is True
    assert template.alternate_weapon_attacks[0].rage_eligible is True
    assert sorted(template.weapon_masteries) == ["flail", "pike"]
