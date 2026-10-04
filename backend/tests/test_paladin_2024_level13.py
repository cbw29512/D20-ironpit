from __future__ import annotations

import logging

from app.combat.damage import resolve_weapon_damage
from app.combat.dice import FixedDiceProvider
from app.combat.debuff_counters import debuff_is_countered
from app.combat.effective_movement_modes import effective_movement_modes
from app.combat.grapple import apply_grapple
from app.combat.precombat_spells import choose_defensive_spell, resolve_defensive_spell
from app.combat.state import begin_turn, build_combatant_state
from app.combat.timed_conditions import expire_start_of_turn_conditions
from app.content.build_audit import assert_character_build_raw_ready
from app.content.canonical_spell_policy import canonical_spell_package
from app.content.character_resource_audit import assert_character_resources_raw_ready
from app.content.monsters import build_commoner
from app.content.paladin_devotion_2024_combat_profile import build_aurelia_2024_combat_profiles
from app.content.paladin_devotion_2024_profile import build_aurelia_brightshield_2024_profile
from app.content.paladin_devotion_2024_runtime import build_aurelia_brightshield_2024
from app.content.pregen_combat_audit import assert_pregen_combat_stats
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import RollMode

logger = logging.getLogger(__name__)


def test_level_thirteen_extends_the_same_build_and_edition_spell_package() -> None:
    try:
        hero = build_aurelia_brightshield_2024(13)
        previous = build_aurelia_brightshield_2024(12)
        profile = build_aurelia_brightshield_2024_profile(13)
        assert hero.name == previous.name
        assert hero.ability_scores == previous.ability_scores
        assert profile.advancement_increases == build_aurelia_brightshield_2024_profile(12).advancement_increases
        assert (hero.max_hp, hero.armor_class) == (108, 19)
        assert (hero.weapon_attack.attack_bonus, hero.weapon_attack.damage_bonus) == (10, 5)
        assert hero.weapon_attack.on_hit_damage == previous.weapon_attack.on_hit_damage
        assert hero.saving_throw_bonuses["charisma"] == hero.skill_bonuses["persuasion"] == 8
        assert hero.progression_features.friendly_saving_throw_aura.flat_bonus == 3
        assert (hero.saving_throw_actions[0].dc, hero.saving_throw_actions[0].max_targets) == (16, 3)
        assert {r.id: r.max_uses for r in hero.resources} == {
            "lay-on-hands": 65, "spell-slot-1": 4, "spell-slot-2": 3,
            "spell-slot-3": 3, "spell-slot-4": 1, "channel-divinity": 3,
            "paladins-smite-free-cast": 1, "faithful-steed-free-cast": 1,
        }
        package = canonical_spell_package("paladin", 13, "2024", 3)
        assert len(package.spells) == 11
        assert package.spells[:-1] == canonical_spell_package("paladin", 12, "2024", 3).spells
        assert package.spells[-1].id == "staggering-smite"
        assert package.spells[-1].required_capabilities == ["post-hit-spell"]
        assert any(item.id == "staggering-smite" for item in hero.progression_features.post_hit_spell_options)
        oath = {s.id: s for s in package.always_prepared_spells}
        assert oath["freedom-of-movement"].always_prepared_from_level == 13
        assert oath["guardian-of-faith"].required_capabilities == ["arena-unavailable-summon"]
        assert "death-ward" not in oath
        assert not hero.persistent_hazard_actions
        assert hero.progression_features.resource_backed_post_hit_damage == previous.progression_features.resource_backed_post_hit_damage
        fingerprint = next(p for p in build_aurelia_2024_combat_profiles() if p.level == 13)
        assert_character_build_raw_ready(profile, hero)
        assert_pregen_combat_stats(hero, fingerprint)
        assert_character_resources_raw_ready(hero, profile, fingerprint)
        assert previous.max_hp == 100
        assert all(r.id != "spell-slot-4" for r in previous.resources)
        assert all(s.id != "freedom-of-movement" for s in previous.defensive_spell_actions)
    except Exception:
        logger.exception("Paladin 13 cumulative source, resources or edition isolation failed.")
        raise


def test_level_thirteen_opening_spell_pays_slot_and_owns_movement_lifecycle() -> None:
    try:
        hero = build_aurelia_brightshield_2024(13)
        member = EncounterCombatant(combatant_id="aurelia", side="heroes", position_ft=0,
                                    state=build_combatant_state(hero))
        spell, slot_level, resource = choose_defensive_spell(member)
        assert (spell.id, slot_level, spell.target_count_per_slot_above) == ("freedom-of-movement", 4, 1)
        event = resolve_defensive_spell(1, member, [member], spell, slot_level, resource)
        assert event.feature_id == "freedom-of-movement"
        assert resource.current_uses == 0
        assert member.state.concentration is None
        assert effective_movement_modes(member.state).swim_ft == 30
        assert debuff_is_countered(member.state, "paralyzed", source_is_magical=True)
        assert not debuff_is_countered(member.state, "paralyzed", source_is_magical=False)
        assert apply_grapple(member.state, "monster", 12, 5, restrains=True) == ["grappled", "restrained"]
        assert begin_turn(member.state) == [("restrained", "monster", 5)]
        assert member.state.movement_remaining_ft == 25
        assert member.state.grapple_sources == []
        assert choose_defensive_spell(member) is None  # One opening buff per fight.
        setup = EncounterSetup(heroes=[member], monsters=[EncounterCombatant(
            combatant_id="enemy", side="monsters", position_ft=30,
            state=build_combatant_state(build_commoner()),
        )], hero_total_levels=13,
                               monster_total_cr="0", ruleset="2024")
        expire_start_of_turn_conditions(2, 601, member, setup)
        assert effective_movement_modes(member.state).swim_ft == 0
        assert not debuff_is_countered(member.state, "paralyzed", source_is_magical=True)
        fresh = build_combatant_state(hero)
        assert next(r for r in fresh.resources if r.id == "spell-slot-4").current_uses == 1
        assert fresh.opening_buff_id is None
        assert fresh.current_hp == 108
        assert fresh.timed_effects == []
    except Exception:
        logger.exception("Paladin 13 shared opening spell payment, movement or reset failed.")
        raise


def test_thrown_melee_weapon_keeps_smite_and_radiant_strikes_qualifiers() -> None:
    try:
        hero = build_aurelia_brightshield_2024(13)
        state = build_combatant_state(hero)
        target = build_combatant_state(build_commoner())
        turn_key = "1:aurelia"
        state.feature_last_turn_keys["savage-attacker"] = turn_key
        attack = hero.alternate_weapon_attacks[0]
        assert attack.weapon.attack_kind.value == "ranged"
        damage, components = resolve_weapon_damage(
            state, attack, FixedDiceProvider([3, 4, 5, 6, 7, 8, 1, 2]),
            True, RollMode.NORMAL, turn_key, target=target,
        )
        assert [(c.source, c.notation) for c in components] == [
            ("Javelin", "2d6+5"), ("Radiant Strikes", "2d8+0"), ("Divine Smite", "4d8+0"),
        ]
        assert damage.total == 41
        assert not state.bonus_action_available
        assert next(r for r in state.resources if r.id == "paladins-smite-free-cast").current_uses == 0
        assert next(r for r in state.resources if r.id == "spell-slot-4").current_uses == 1
        assert state.spell_slot_expended_turn_key is None
    except Exception:
        logger.exception("Thrown Melee weapon 2024 Smite/Radiant Strikes qualification failed.")
        raise
