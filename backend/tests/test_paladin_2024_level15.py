from __future__ import annotations

import logging

from app.combat.damage import resolve_weapon_damage
from app.combat.dice import FixedDiceProvider
from app.combat.friendly_save_auras import sync_friendly_save_auras
from app.combat.modifier_stack import effective_armor_class, saving_throw_flat_bonus
from app.combat.state import build_combatant_state
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
from app.domain.models import RollMode, TimedEffect

logger = logging.getLogger(__name__)


def _member(template, combatant_id: str, x: int) -> EncounterCombatant:
    state = build_combatant_state(template)
    state.position = GridPosition(x=x, y=0)
    return EncounterCombatant(
        combatant_id=combatant_id,
        side="heroes",
        position_ft=x * 5,
        state=state,
    )


def test_level_fifteen_is_incremental_and_raw_ready() -> None:
    try:
        hero = build_aurelia_brightshield_2024(15)
        previous = build_aurelia_brightshield_2024(14)
        profile = build_aurelia_brightshield_2024_profile(15)
        assert hero.name == previous.name
        assert hero.ability_scores == previous.ability_scores
        assert (hero.max_hp, hero.armor_class, hero.weapon_attack.attack_bonus) == (124, 19, 10)
        assert {item.id: item.max_uses for item in hero.resources} == {
            "lay-on-hands": 75,
            "spell-slot-1": 4,
            "spell-slot-2": 3,
            "spell-slot-3": 3,
            "spell-slot-4": 2,
            "channel-divinity": 3,
            "paladins-smite-free-cast": 1,
            "faithful-steed-free-cast": 1,
        }
        package = canonical_spell_package("paladin", 15, "2024", 3)
        assert len(package.spells) == 12
        assert "death-ward" in {spell.id for spell in package.spells}
        death_ward = next(action for action in hero.defensive_spell_actions if action.id == "death-ward")
        assert death_ward.source == "D&D Beyond Basic Rules 2024: Death Ward"
        assert death_ward.modifier_effects[0].kind == "zero-hp-replacement"
        aura = hero.progression_features.friendly_defensive_auras[0]
        assert (
            aura.source_id,
            aura.radius_ft,
            aura.armor_class_bonus,
            aura.saving_throw_bonus,
            aura.saving_throw_abilities,
            aura.non_stacking_group,
        ) == ("smite-of-protection-2024", 10, 2, 2, ["dexterity"], "cover")
        rule = hero.progression_features.resource_backed_post_hit_damage
        assert rule is not None and rule.on_use_self_effect_id == "smite-of-protection-2024"
        assert next(a for a in profile.feature_audits if a.feature_id == "smite-of-protection").automated
        fingerprint = next(item for item in build_aurelia_2024_combat_profiles() if item.level == 15)
        assert_character_build_raw_ready(profile, hero)
        assert_pregen_combat_stats(hero, fingerprint)
        assert_character_resources_raw_ready(hero, profile, fingerprint)
    except Exception:
        logger.exception("Paladin 15 cumulative certification failed.")
        raise


def test_divine_smite_activates_live_half_cover_and_tracks_live_aura_range() -> None:
    try:
        hero = build_aurelia_brightshield_2024(15)
        source = _member(hero, "aurelia", 0)
        ally = _member(build_commoner(), "ally", 2)
        enemy = _member(build_commoner(), "enemy-template", 8)
        enemy.side = "monsters"
        setup = EncounterSetup(
            heroes=[source, ally],
            monsters=[enemy],
            hero_total_levels=15,
            monster_total_cr="0",
            ruleset="2024",
        )
        target_state = enemy.state
        resolve_weapon_damage(
            source.state,
            hero.weapon_attack,
            FixedDiceProvider([4, 5, 6, 7]),
            critical=False,
            attack_mode=RollMode.NORMAL,
            turn_key="1:aurelia",
            target=target_state,
        )
        assert any(
            effect.source_effect_id == "smite-of-protection-2024"
            and effect.expiry_timing == "source_turn_start"
            for effect in source.state.timed_effects
        )
        sync_friendly_save_auras(setup)
        assert effective_armor_class(ally.state) == ally.state.template.armor_class + 2
        assert saving_throw_flat_bonus(ally.state, "dexterity") == 5  # Aura of Protection + Half Cover.
        assert saving_throw_flat_bonus(ally.state, "wisdom") == 3  # Aura of Protection only.
        ally.state.position = GridPosition(x=3, y=0)
        sync_friendly_save_auras(setup)
        assert effective_armor_class(ally.state) == ally.state.template.armor_class
    except Exception:
        logger.exception("Smite of Protection live aura failed.")
        raise


def test_overlapping_half_cover_sources_do_not_stack_and_fall_back() -> None:
    try:
        hero = build_aurelia_brightshield_2024(15)
        first = _member(hero, "first", 0)
        second = _member(hero, "second", 1)
        ally = _member(build_commoner(), "ally", 2)
        enemy = _member(build_commoner(), "enemy", 10)
        enemy.side = "monsters"
        for source in (first, second):
            source.state.timed_effects.append(TimedEffect(
                effect_id="smite-of-protection-2024",
                source_id=source.combatant_id,
                source_effect_id="smite-of-protection-2024",
                applied_round=1,
                expiry_timing="source_turn_start",
            ))
        setup = EncounterSetup(
            heroes=[first, second, ally],
            monsters=[enemy],
            hero_total_levels=30,
            monster_total_cr="0",
            ruleset="2024",
        )
        sync_friendly_save_auras(setup)
        cover = [
            item for item in ally.state.active_modifiers
            if item.non_stacking_group == "cover"
        ]
        assert len(cover) == 4  # Two sources: AC + Dexterity save from each.
        assert effective_armor_class(ally.state) == ally.state.template.armor_class + 2
        assert saving_throw_flat_bonus(ally.state, "dexterity") == 5  # +3 Aura of Protection, +2 cover.
        first.state.timed_effects = []
        sync_friendly_save_auras(setup)
        assert effective_armor_class(ally.state) == ally.state.template.armor_class + 2
        assert saving_throw_flat_bonus(ally.state, "dexterity") == 5
        second.state.timed_effects = []
        sync_friendly_save_auras(setup)
        assert effective_armor_class(ally.state) == ally.state.template.armor_class
        assert saving_throw_flat_bonus(ally.state, "dexterity") == 3
    except Exception:
        logger.exception("Overlapping Half Cover source fallback failed.")
        raise
