from app.combat.dice import FixedDiceProvider
from app.combat.damage import resolve_weapon_damage
from app.combat.state import build_combatant_state
from app.content.cleric_life_2014_runtime import build_seraphine_dawnshield_2014
from app.domain.damage_riders import OncePerTurnWeaponHitDamageRider
from app.domain.progression import ProgressionCombatFeatures


def _state_with_rider():
    template = build_seraphine_dawnshield_2014(7).model_copy(deep=True)
    template.progression_features = ProgressionCombatFeatures(
        once_per_turn_weapon_hit_damage_rider=OncePerTurnWeaponHitDamageRider(
            source_id="test-rider",
            source_name="Test Rider",
            dice_count=1,
            dice_size=8,
            damage_type="radiant",
        )
    )
    return build_combatant_state(template)


def test_once_per_turn_weapon_hit_rider_fires_once_per_turn() -> None:
    attacker = _state_with_rider()
    attack = attacker.template.weapon_attack

    first, components = resolve_weapon_damage(
        attacker, attack, FixedDiceProvider([4, 6]), False, "normal", "1:attacker",
    )
    assert [part.source for part in components] == ["Warhammer", "Test Rider"]
    assert first.total == 11

    second, components = resolve_weapon_damage(
        attacker, attack, FixedDiceProvider([5]), False, "normal", "1:attacker",
    )
    assert [part.source for part in components] == ["Warhammer"]
    assert second.total == 6

    third, components = resolve_weapon_damage(
        attacker, attack, FixedDiceProvider([3, 7]), False, "normal", "2:attacker",
    )
    assert [part.source for part in components] == ["Warhammer", "Test Rider"]
    assert third.total == 11


def test_once_per_turn_weapon_hit_rider_dice_double_on_critical() -> None:
    attacker = _state_with_rider()
    attack = attacker.template.weapon_attack
    result, components = resolve_weapon_damage(
        attacker, attack, FixedDiceProvider([4, 5, 6, 7]), True, "normal", "1:attacker",
    )
    assert [part.source for part in components] == ["Warhammer", "Test Rider"]
    assert components[1].rolls == [6, 7]
    assert result.total == 23
