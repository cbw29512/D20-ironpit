from __future__ import annotations

from app.combat.damage import resolve_weapon_damage
from app.combat.dice import FixedDiceProvider
from app.combat.state import build_combatant_state
from app.content.canonical_spell_policy import canonical_spell_package
from app.content.ranger_hunter_2014_profile import build_rowan_ashtrail_2014_profile
from app.content.ranger_hunter_2014_runtime import build_rowan_ashtrail_2014


def test_2014_hunter_ranger_level_three_snapshot() -> None:
    hero = build_rowan_ashtrail_2014(3)
    profile = build_rowan_ashtrail_2014_profile(3)
    rider = hero.progression_features.once_per_turn_weapon_hit_damage_rider

    assert hero.level == 3
    assert hero.max_hp == 28
    assert hero.weapon_attack.attack_bonus == 7
    assert profile.subclass_id == "hunter"
    assert profile.subclass_name == "Hunter"
    assert {item.id: item.max_uses for item in hero.resources} == {"spell-slot-1": 3}
    assert rider is not None
    assert rider.source_id == "colossus-slayer"
    assert rider.source_name == "Colossus Slayer"
    assert (rider.dice_count, rider.dice_size) == (1, 8)
    assert rider.damage_type is None
    assert rider.requires_target_below_max_hp is True


def test_2014_colossus_slayer_is_check_then_result() -> None:
    attacker = build_combatant_state(build_rowan_ashtrail_2014(3))
    target = build_combatant_state(build_rowan_ashtrail_2014(3))
    attack = attacker.template.weapon_attack

    full, components = resolve_weapon_damage(
        attacker, attack, FixedDiceProvider([4]), False, "normal", "1:rowan", target=target,
    )
    assert [part.source for part in components] == ["Longbow"]
    assert full.total == 7
    assert attacker.feature_last_turn_keys.get("colossus-slayer") is None

    target.current_hp -= 1
    damaged, components = resolve_weapon_damage(
        attacker, attack, FixedDiceProvider([4, 6]), False, "normal", "1:rowan", target=target,
    )
    assert [part.source for part in components] == ["Longbow", "Colossus Slayer"]
    assert components[1].damage_type == attack.weapon.damage_type
    assert damaged.total == 13

    repeat, components = resolve_weapon_damage(
        attacker, attack, FixedDiceProvider([5]), False, "normal", "1:rowan", target=target,
    )
    assert [part.source for part in components] == ["Longbow"]
    assert repeat.total == 8


def test_2014_ranger_level_three_spell_and_feature_audits() -> None:
    package = canonical_spell_package("ranger", 3, "2014")
    audits = {item.feature_id: item for item in build_rowan_ashtrail_2014_profile(3).feature_audits}

    assert package is not None
    assert [spell.id for spell in package.spells] == ["longstrider", "cure-wounds", "detect-magic"]
    assert audits["colossus-slayer"].combat_relevant is True
    assert audits["colossus-slayer"].automated is True
    assert audits["primeval-awareness"].combat_relevant is False
