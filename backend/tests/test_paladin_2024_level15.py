from __future__ import annotations

import logging

from app.combat.dice import FixedDiceProvider
from app.combat.encounter_attacks import resolve_encounter_attack
from app.combat.friendly_save_auras import sync_friendly_save_auras
from app.combat.modifier_stack import add_modifier, effective_armor_class, saving_throw_flat_bonus
from app.combat.state import build_combatant_state
from app.combat.timed_condition_lifecycle import expire_start_of_turn_conditions
from app.content.build_audit import assert_character_build_raw_ready
from app.content.canonical_spell_policy import canonical_spell_package
from app.content.character_resource_audit import assert_character_resources_raw_ready
from app.content.monsters import build_commoner
from app.content.paladin_devotion_2024_combat_profile import build_aurelia_2024_combat_profiles
from app.content.paladin_devotion_2024_profile import build_aurelia_brightshield_2024_profile
from app.content.paladin_devotion_2024_runtime import build_aurelia_brightshield_2024
from app.content.pregen_combat_audit import assert_pregen_combat_stats
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.grid import GridPosition
from app.domain.modifiers import CombatModifier, ModifierKind

logger = logging.getLogger(__name__)


def _member(combatant_id: str, side: str, template, x: int) -> EncounterCombatant:
    member = EncounterCombatant(
        combatant_id=combatant_id,
        side=side,
        position_ft=x * 5,
        state=build_combatant_state(template),
    )
    member.state.position = GridPosition(x=x, y=0)
    return member


def test_level_fifteen_extends_same_aurelia_and_spell_package() -> None:
    try:
        hero = build_aurelia_brightshield_2024(15)
        previous = build_aurelia_brightshield_2024(14)
        profile = build_aurelia_brightshield_2024_profile(15)
        assert hero.name == previous.name
        assert hero.ability_scores == previous.ability_scores
        assert profile.advancement_increases == build_aurelia_brightshield_2024_profile(14).advancement_increases
        assert (hero.max_hp, hero.armor_class, hero.weapon_attack.attack_bonus) == (124, 19, 10)
        assert {item.id: item.max_uses for item in hero.resources} == {
            "lay-on-hands": 75,
            "spell-slot-1": 4,
            "paladins-smite-free-cast": 1,
            "channel-divinity": 3,
            "spell-slot-2": 3,
            "faithful-steed-free-cast": 1,
            "spell-slot-3": 3,
            "spell-slot-4": 2,
        }
        package = canonical_spell_package("paladin", 15, "2024", 3)
        assert package is not None and len(package.spells) == 12
        assert package.spells[:-1] == canonical_spell_package("paladin", 14, "2024", 3).spells
        assert (package.spells[-1].id, package.spells[-1].spell_level) == ("aura-of-life", 4)
        assert package.spells[-1].required_capabilities == ["arena-out-of-scope"]
        rider = hero.progression_features.resource_backed_post_hit_damage
        assert rider is not None
        assert rider.post_hit_self_buff_action_id == "smite-of-protection-2024"
        action = hero.timed_self_buff_actions[0]
        assert (action.id, action.duration_rounds, action.expiry_timing) == (
            "smite-of-protection-2024", 1, "source_turn_start",
        )
        assert action.friendly_cover_aura is not None
        assert (action.friendly_cover_aura.radius_ft, action.friendly_cover_aura.cover_bonus) == (10, 2)
        audits = {item.feature_id: item for item in profile.feature_audits}
        assert audits["smite-of-protection"].automated
        fingerprint = next(item for item in build_aurelia_2024_combat_profiles() if item.level == 15)
        assert_character_build_raw_ready(profile, hero)
        assert_pregen_combat_stats(hero, fingerprint)
        assert_character_resources_raw_ready(hero, profile, fingerprint)
    except Exception:
        logger.exception("Paladin 15 cumulative source/build certification failed.")
        raise


def test_divine_smite_activates_live_half_cover_until_next_turn() -> None:
    try:
        hero = build_aurelia_brightshield_2024(15)
        aurelia = _member("aurelia", "heroes", hero, 0)
        ally = _member("ally", "heroes", build_commoner(), 2)
        enemy_template = build_commoner().model_copy(update={"max_hp": 100})
        enemy = _member("enemy", "monsters", enemy_template, 1)
        setup = EncounterSetup(
            heroes=[aurelia, ally],
            monsters=[enemy],
            hero_total_levels=15,
            monster_total_cr="0",
            ruleset="2024",
        )
        turn_key = "1:aurelia"
        aurelia.state.feature_last_turn_keys["savage-attacker"] = turn_key
        event = resolve_encounter_attack(
            1, 1, aurelia, enemy, hero.weapon_attack, 5,
            FixedDiceProvider([18, 4, 5, 6, 7, 8, 3, 2]),
            setup, spend_action=False, turn_key=turn_key,
        )
        assert event.hit is True
        assert any(item.source == "Divine Smite" for item in event.damage_components)
        assert "Smite of Protection activates." in event.description
        assert any(
            effect.source_effect_id == "smite-of-protection-2024"
            and effect.expires_round == 2
            and effect.expiry_timing == "source_turn_start"
            for effect in aurelia.state.timed_effects
        )
        assert effective_armor_class(aurelia.state) == hero.armor_class + 2
        assert effective_armor_class(ally.state) == ally.state.template.armor_class + 2
        assert saving_throw_flat_bonus(ally.state, "dexterity") == 2
        assert saving_throw_flat_bonus(ally.state, "wisdom") == 0
        assert effective_armor_class(enemy.state) == enemy.state.template.armor_class

        ally.state.position = GridPosition(x=3, y=0)
        sync_friendly_save_auras(setup)
        assert effective_armor_class(ally.state) == ally.state.template.armor_class
        ally.state.position = GridPosition(x=1, y=0)
        sync_friendly_save_auras(setup)
        assert effective_armor_class(ally.state) == ally.state.template.armor_class + 2

        expire_start_of_turn_conditions(2, 2, aurelia, setup)
        sync_friendly_save_auras(setup)
        assert not any(
            effect.source_effect_id == "smite-of-protection-2024"
            for effect in aurelia.state.timed_effects
        )
        assert effective_armor_class(ally.state) == ally.state.template.armor_class
    except Exception:
        logger.exception("Paladin 15 Smite of Protection lifecycle failed.")
        raise


def test_half_cover_uses_strongest_cover_without_breaking_normal_stacking() -> None:
    try:
        state = build_combatant_state(build_commoner())
        add_modifier(state, CombatModifier(
            id="shield", source_id="spell", source_effect_id="shield-of-faith",
            kind=ModifierKind.ARMOR_CLASS, flat_bonus=2,
        ))
        for suffix, bonus in [("half", 2), ("three-quarters", 5)]:
            add_modifier(state, CombatModifier(
                id=f"cover-ac-{suffix}", source_id=suffix, source_effect_id="cover",
                kind=ModifierKind.COVER_ARMOR_CLASS, flat_bonus=bonus,
            ))
            add_modifier(state, CombatModifier(
                id=f"cover-save-{suffix}", source_id=suffix, source_effect_id="cover",
                kind=ModifierKind.COVER_SAVING_THROW_FLAT, flat_bonus=bonus,
                save_ability="dexterity",
            ))
        add_modifier(state, CombatModifier(
            id="bless-like", source_id="other", source_effect_id="other-save",
            kind=ModifierKind.SAVING_THROW_FLAT, flat_bonus=3,
        ))
        assert effective_armor_class(state) == state.template.armor_class + 2 + 5
        assert saving_throw_flat_bonus(state, "dexterity") == 3 + 5
        assert saving_throw_flat_bonus(state, "wisdom") == 3
    except Exception:
        logger.exception("Strongest-cover modifier semantics failed.")
        raise
