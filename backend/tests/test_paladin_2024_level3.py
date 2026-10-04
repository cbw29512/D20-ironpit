from __future__ import annotations

from app.combat.attack_action_weapon_buffs import resolve_attack_action_weapon_buff
from app.combat.attack_damage_type_choice import choose_attack_damage_type
from app.combat.defensive_modifier_rules import saving_throw_advantage_sources
from app.combat.modifier_stack import add_modifier, attack_roll_flat_bonus
from app.combat.spell_modifiers import build_spell_modifier
from app.combat.state import build_combatant_state
from app.content.audited_fighter import build_karnok_stoneward
from app.content.build_audit import assert_character_build_raw_ready
from app.content.canonical_hero_policy import assert_canonical_profile_policy
from app.content.canonical_spell_policy import canonical_spell_package
from app.content.paladin_devotion_2024_combat_profile import build_aurelia_2024_combat_profiles
from app.content.paladin_devotion_2024_profile import build_aurelia_brightshield_2024_profile
from app.content.paladin_devotion_2024_runtime import build_aurelia_brightshield_2024
from app.content.pregen_combat_audit import assert_pregen_combat_stats
from app.domain.encounters import EncounterCombatant
from app.domain.models import DamageType
from app.domain.saving_throw_context import SavingThrowContext


def _member(template, combatant_id: str, side: str, position: int) -> EncounterCombatant:
    return EncounterCombatant(
        combatant_id=combatant_id,
        side=side,
        position_ft=position,
        state=build_combatant_state(template),
    )


def test_2024_paladin_level_three_profile_and_resources_are_raw_ready() -> None:
    profile = build_aurelia_brightshield_2024_profile(3)
    hero = build_aurelia_brightshield_2024(3)
    combat = next(item for item in build_aurelia_2024_combat_profiles() if item.level == 3)

    assert (profile.subclass_id, profile.subclass_name) == ("oath-devotion", "Oath of Devotion")
    assert (hero.max_hp, hero.armor_class) == (28, 19)
    assert {item.id: item.max_uses for item in hero.resources} == {
        "lay-on-hands": 15,
        "spell-slot-1": 3,
        "paladins-smite-free-cast": 1,
        "channel-divinity": 2,
    }

    package = canonical_spell_package("paladin", 3, "2024", 2)
    assert package is not None
    assert [spell.id for spell in package.spells] == [
        "cure-wounds", "divine-favor", "bless", "searing-smite",
    ]
    assert [spell.id for spell in package.always_prepared_spells] == [
        "divine-smite", "protection-from-evil-and-good", "shield-of-faith",
    ]
    assert package.spells[-1].required_capabilities == ["post-hit-spell"]

    assert_canonical_profile_policy(profile)
    assert_character_build_raw_ready(profile, hero)
    assert_pregen_combat_stats(hero, combat)


def test_sacred_weapon_reuses_attack_bonus_and_damage_type_choice_primitives() -> None:
    paladin = _member(
        build_aurelia_brightshield_2024(3),
        "hero-1:aurelia-brightshield-l3",
        "heroes",
        0,
    )
    resistant_target_template = build_karnok_stoneward().model_copy(
        update={"damage_resistances": [DamageType.SLASHING]},
    )
    target = _member(resistant_target_template, "monster-1:target", "monsters", 5)

    event = resolve_attack_action_weapon_buff(1, 1, paladin)
    assert event is not None
    assert event.feature_id == "sacred-weapon"
    assert event.resource_remaining == 1
    assert attack_roll_flat_bonus(paladin.state, "longsword") == 2

    chosen = choose_attack_damage_type(
        paladin.state,
        paladin.state.template.weapon_attack,
        target.state,
        source_qualifiers={"attack", "weapon", "melee"},
    )
    assert chosen is DamageType.RADIANT

    # A second Attack action while the same 10-minute effect is active does not spend again.
    assert resolve_attack_action_weapon_buff(2, 2, paladin) is None
    channel = next(item for item in paladin.state.resources if item.id == "channel-divinity")
    assert channel.current_uses == 1


def test_protection_from_evil_and_good_save_advantage_is_context_specific() -> None:
    hero = build_aurelia_brightshield_2024(3)
    protection = next(
        spell for spell in hero.defensive_spell_actions
        if spell.id == "protection-from-evil-and-good"
    )
    wisdom_charm = next(
        effect for effect in protection.modifier_effects
        if effect.kind == "saving-throw-advantage"
        and effect.save_ability == "wisdom"
        and effect.required_effect_tags == ["charm"]
    )

    target_state = build_combatant_state(build_karnok_stoneward())
    modifier = build_spell_modifier(
        "aurelia", "target", protection.id, wisdom_charm, 0, protection.name,
        concentration_required=True, round_number=1,
    )
    add_modifier(target_state, modifier)

    assert saving_throw_advantage_sources(
        target_state,
        "wisdom",
        SavingThrowContext(source_creature_type="fiend", effect_tags=frozenset({"charm"})),
    ) == 1
    assert saving_throw_advantage_sources(
        target_state,
        "wisdom",
        SavingThrowContext(source_creature_type="humanoid", effect_tags=frozenset({"charm"})),
    ) == 0
    assert saving_throw_advantage_sources(
        target_state,
        "wisdom",
        SavingThrowContext(source_creature_type="fiend", effect_tags=frozenset({"poison"})),
    ) == 0
