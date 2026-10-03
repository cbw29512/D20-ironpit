from __future__ import annotations

from app.combat.damage import resolve_weapon_damage
from app.combat.dice import FixedDiceProvider
from app.combat.state import build_combatant_state
from app.content.build_audit import assert_character_build_raw_ready
from app.content.canonical_hero_policy import assert_canonical_profile_policy
from app.content.canonical_spell_policy import canonical_spell_package
from app.content.character_resource_audit import assert_character_resources_raw_ready
from app.content.monsters import build_commoner
from app.content.paladin_devotion_2024_combat_profile import build_aurelia_2024_combat_profiles
from app.content.paladin_devotion_2024_profile import build_aurelia_brightshield_2024_profile
from app.content.paladin_devotion_2024_runtime import build_aurelia_brightshield_2024
from app.content.pregen_combat_audit import assert_pregen_combat_stats
from app.domain.models import RollMode


def _resource(state, resource_id: str):
    return next(item for item in state.resources if item.id == resource_id)


def test_2024_paladin_level_two_is_raw_ready() -> None:
    profile = build_aurelia_brightshield_2024_profile(2)
    hero = build_aurelia_brightshield_2024(2)
    combat = build_aurelia_2024_combat_profiles()[1]

    assert (hero.armor_class, hero.max_hp, hero.fighting_style) == (19, 20, "Defense")
    assert {item.id: item.max_uses for item in hero.resources} == {
        "lay-on-hands": 10,
        "spell-slot-1": 2,
        "paladins-smite-free-cast": 1,
    }
    smite = hero.progression_features.resource_backed_post_hit_damage
    assert smite is not None
    assert smite.source_name == "Divine Smite"
    assert smite.trigger_attack_ids == ["aurelia-longsword", "aurelia-javelin"]
    assert (smite.base_dice_count, smite.dice_size, smite.damage_type) == (2, 8, "radiant")
    assert smite.bonus_target_creature_types == ["fiend", "undead"]
    assert smite.bonus_target_dice_count == 1

    package = canonical_spell_package("paladin", 2, "2024", 2)
    assert package is not None
    assert [spell.id for spell in package.spells] == ["cure-wounds", "divine-favor", "bless"]
    assert [spell.id for spell in package.always_prepared_spells] == ["divine-smite"]

    assert_canonical_profile_policy(profile)
    assert_character_build_raw_ready(profile, hero)
    assert_pregen_combat_stats(hero, combat)
    assert_character_resources_raw_ready(hero, profile, combat)


def test_divine_smite_free_cast_joins_the_triggering_attack_damage() -> None:
    turn_key = "1:aurelia"
    attacker = build_combatant_state(build_aurelia_brightshield_2024(2))
    attacker.feature_last_turn_keys["savage-attacker"] = turn_key
    target_template = build_commoner().model_copy(
        update={"creature_type": "fiend", "max_hp": 100},
        deep=True,
    )
    target = build_combatant_state(target_template)

    damage, components = resolve_weapon_damage(
        attacker,
        attacker.template.weapon_attack,
        FixedDiceProvider([4, 8, 7, 6]),
        False,
        RollMode.NORMAL,
        turn_key,
        target=target,
    )

    assert [part.source for part in components] == ["Longsword", "Divine Smite"]
    assert components[1].notation == "3d8+0"
    assert components[1].total == 21
    assert damage.total == 28
    assert attacker.bonus_action_available is False
    assert _resource(attacker, "paladins-smite-free-cast").current_uses == 0
    assert _resource(attacker, "spell-slot-1").current_uses == 2
    assert attacker.spell_slot_expended_turn_key is None


def test_divine_smite_falls_back_to_spell_slot_and_doubles_on_critical() -> None:
    turn_key = "1:aurelia"
    attacker = build_combatant_state(build_aurelia_brightshield_2024(2))
    attacker.feature_last_turn_keys["savage-attacker"] = turn_key
    _resource(attacker, "paladins-smite-free-cast").current_uses = 0
    target = build_combatant_state(build_commoner().model_copy(update={"max_hp": 100}, deep=True))

    _damage, components = resolve_weapon_damage(
        attacker,
        attacker.template.weapon_attack,
        FixedDiceProvider([4, 5, 8, 7, 6, 5]),
        True,
        RollMode.NORMAL,
        turn_key,
        target=target,
    )

    assert components[1].source == "Divine Smite"
    assert components[1].notation == "4d8+0"
    assert components[1].rolls == [8, 7, 6, 5]
    assert _resource(attacker, "spell-slot-1").current_uses == 1
    assert attacker.spell_slot_expended_turn_key == turn_key
