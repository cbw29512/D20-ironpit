from __future__ import annotations

import logging

from app.combat.friendly_save_auras import sync_friendly_save_auras
from app.combat.modifier_stack import saving_throw_flat_bonus
from app.combat.state import build_combatant_state
from app.content.build_audit import assert_character_build_raw_ready
from app.content.canonical_hero_policy import assert_canonical_profile_policy
from app.content.canonical_spell_policy import canonical_spell_package
from app.content.monsters import build_commoner
from app.content.paladin_devotion_2024_combat_profile import build_aurelia_2024_combat_profiles
from app.content.paladin_devotion_2024_profile import build_aurelia_brightshield_2024_profile
from app.content.paladin_devotion_2024_runtime import build_aurelia_brightshield_2024
from app.content.pregen_combat_audit import assert_pregen_combat_stats
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.grid import GridPosition

logger = logging.getLogger(__name__)


def test_level_twelve_asi_updates_every_charisma_consumer() -> None:
    try:
        profile = build_aurelia_brightshield_2024_profile(12)
        hero = build_aurelia_brightshield_2024(12)
        previous = build_aurelia_brightshield_2024(11)
        # A level delta extends the same build rather than replacing its foundation.
        assert hero.name == previous.name
        assert profile.final_ability_scores.charisma == 17
        assert profile.final_ability_scores.strength == 20
        assert [(i.ability, i.amount) for i in profile.advancement_increases] == [
            ("strength", 2), ("strength", 1), ("charisma", 1), ("charisma", 2),
        ]
        assert (hero.max_hp, hero.armor_class) == (100, 19)
        assert (hero.weapon_attack.attack_bonus, hero.weapon_attack.damage_bonus) == (9, 5)
        assert hero.weapon_attack.on_hit_damage == previous.weapon_attack.on_hit_damage
        assert hero.attack_action == previous.attack_action
        assert hero.saving_throw_bonuses["charisma"] == 7
        assert hero.skill_bonuses["persuasion"] == hero.skill_bonuses["intimidation"] == 7
        assert hero.progression_features.friendly_saving_throw_aura.flat_bonus == 3
        assert hero.attack_action_weapon_buffs[0].attack_roll_bonus == 3
        assert (hero.saving_throw_actions[0].dc, hero.saving_throw_actions[0].max_targets) == (15, 3)
        assert hero.healing_actions[1].healing_bonus == 3
        assert {r.id: r.max_uses for r in hero.resources} == {
            "lay-on-hands": 60, "spell-slot-1": 4, "spell-slot-2": 3,
            "spell-slot-3": 3, "channel-divinity": 3,
            "paladins-smite-free-cast": 1, "faithful-steed-free-cast": 1,
        }
        # 2024 uses the class table; gaining Charisma does not add preparations.
        package = canonical_spell_package("paladin", 12, "2024", 3)
        assert len(package.spells) == 10
        assert package == canonical_spell_package("paladin", 11, "2024", 2)
        assert any(a.feature_id == "ability-score-improvement-l12" and a.automated
                   for a in profile.feature_audits)
        assert_canonical_profile_policy(profile)
        assert_character_build_raw_ready(profile, hero)
        fingerprint = next(p for p in build_aurelia_2024_combat_profiles() if p.level == 12)
        assert_pregen_combat_stats(hero, fingerprint)
        assert previous.ability_scores.charisma == 15
        assert previous.progression_features.friendly_saving_throw_aura.flat_bonus == 2
        assert previous.max_hp == 92
    except Exception:
        logger.exception("Paladin 12 cumulative build or derived Charisma regression failed.")
        raise


def test_level_twelve_aura_uses_live_positions_and_fresh_state() -> None:
    try:
        hero = build_aurelia_brightshield_2024(12)
        source = EncounterCombatant(
            combatant_id="aurelia", side="heroes", position_ft=0,
            state=build_combatant_state(hero),
        )
        ally = EncounterCombatant(
            combatant_id="ally", side="heroes", position_ft=5,
            state=build_combatant_state(build_commoner()),
        )
        setup = EncounterSetup(
            heroes=[source, ally], monsters=[EncounterCombatant(
                combatant_id="enemy", side="monsters", position_ft=30,
                state=build_combatant_state(build_commoner()),
            )], hero_total_levels=12,
            monster_total_cr="0", ruleset="2024",
        )
        # Exercise the authoritative 5-foot grid rather than scalar migration state.
        source.state.position = GridPosition(x=0, y=0)
        ally.state.position = GridPosition(x=1, y=0)
        setup.monsters[0].state.position = GridPosition(x=6, y=0)
        sync_friendly_save_auras(setup)
        assert saving_throw_flat_bonus(source.state) == 3
        assert saving_throw_flat_bonus(ally.state) == 3
        ally.state.position = GridPosition(x=3, y=0)
        sync_friendly_save_auras(setup)
        assert saving_throw_flat_bonus(ally.state) == 0
        ally.state.position = GridPosition(x=1, y=0)
        source.state.active_effect_ids.append("incapacitated")
        sync_friendly_save_auras(setup)
        assert saving_throw_flat_bonus(ally.state) == 0
        # Match restoration rebuilds state; it never mutates the source template.
        fresh = build_combatant_state(hero)
        assert "incapacitated" not in fresh.active_effect_ids
        assert fresh.current_hp == 100
        assert next(r for r in fresh.resources if r.id == "lay-on-hands").current_uses == 60
        assert hero.progression_features.friendly_saving_throw_aura.flat_bonus == 3
    except Exception:
        logger.exception("Paladin 12 live aura or match reset regression failed.")
        raise
