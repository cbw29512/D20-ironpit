from __future__ import annotations

from app.combat.once_per_turn_hit_damage import once_per_turn_weapon_hit_bonus_damages
from app.content.ranger_2014_spell_package import build_ranger_2014_spell_package
from app.content.ranger_hunter_2014_profile import build_rowan_ashtrail_2014_profile
from app.content.ranger_hunter_2014_runtime import build_rowan_ashtrail_2014
from app.domain.models import CombatantState


def _state(template, *, hp: int | None = None) -> CombatantState:
    return CombatantState(template=template, current_hp=template.max_hp if hp is None else hp)


def _target(creature_type: str, *, bloodied: bool) -> CombatantState:
    template = build_rowan_ashtrail_2014(20).model_copy(
        update={"creature_type": creature_type}
    )
    hp = template.max_hp - 1 if bloodied else template.max_hp
    return _state(template, hp=hp)


def test_level_twenty_completes_ranger_progression() -> None:
    hero = build_rowan_ashtrail_2014(20)
    profile = build_rowan_ashtrail_2014_profile(20)
    package = build_ranger_2014_spell_package(20)

    assert hero.level == 20
    assert profile.level == 20
    assert hero.max_hp == 164
    assert profile.final_ability_scores.wisdom == 20
    assert hero.weapon_attack.attack_bonus == 13
    assert len(package.spells) == 11

    extra = hero.progression_features.once_per_turn_weapon_hit_damage_riders
    assert len(extra) == 1
    foe_slayer = extra[0]
    assert foe_slayer.source_id == "foe-slayer"
    assert foe_slayer.flat_bonus == 5
    assert foe_slayer.target_creature_types == ["monstrosity", "undead", "fiend"]


def test_foe_slayer_and_colossus_slayer_qualify_independently() -> None:
    hero = build_rowan_ashtrail_2014(20)
    attacker = _state(hero)

    favored_bloodied = _target("monstrosity", bloodied=True)
    both = once_per_turn_weapon_hit_bonus_damages(
        attacker, hero.weapon_attack, "1:rowan", favored_bloodied
    )
    assert [item[0] for item in both] == ["Colossus Slayer", "Foe Slayer"]
    assert both[1][1:4] == (0, 2, 5)

    assert once_per_turn_weapon_hit_bonus_damages(
        attacker, hero.weapon_attack, "1:rowan", favored_bloodied
    ) == []

    attacker.feature_last_turn_keys.clear()
    favored_full = _target("undead", bloodied=False)
    foe_only = once_per_turn_weapon_hit_bonus_damages(
        attacker, hero.weapon_attack, "2:rowan", favored_full
    )
    assert [item[0] for item in foe_only] == ["Foe Slayer"]

    attacker.feature_last_turn_keys.clear()
    other_bloodied = _target("beast", bloodied=True)
    colossus_only = once_per_turn_weapon_hit_bonus_damages(
        attacker, hero.weapon_attack, "3:rowan", other_bloodied
    )
    assert [item[0] for item in colossus_only] == ["Colossus Slayer"]
