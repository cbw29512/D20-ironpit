from __future__ import annotations
import logging
import pytest
from app.combat.condition_removal import choose_condition_removal_action, resolve_condition_removal, remove_condition
from app.combat.dice import FixedDiceProvider
from app.combat.healing import resolve_healing
from app.combat.state import begin_turn, build_combatant_state
from app.content.build_audit import assert_character_build_raw_ready
from app.content.canonical_spell_policy import canonical_spell_package
from app.content.character_resource_audit import assert_character_resources_raw_ready
from app.content.monsters import build_commoner
from app.content.paladin_devotion_2014_runtime import build_aurelia_brightshield_2014
from app.content.paladin_devotion_2024_combat_profile import build_aurelia_2024_combat_profiles
from app.content.paladin_devotion_2024_profile import build_aurelia_brightshield_2024_profile
from app.content.paladin_devotion_2024_runtime import build_aurelia_brightshield_2024
from app.content.pregen_combat_audit import assert_pregen_combat_stats
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.grid import GridPosition
from app.domain.size import CreatureSize
from app.domain.models import TimedEffect
from app.domain.modifiers import CombatModifier, ModifierKind
logger = logging.getLogger(__name__)
RESTORING = ["blinded", "charmed", "deafened", "frightened", "paralyzed", "stunned"]


def _setup(edition="2024", side="heroes"):
    try:
        hero = (build_aurelia_brightshield_2024 if edition == "2024" else build_aurelia_brightshield_2014)(14)
        remover = EncounterCombatant(combatant_id="aurelia", side=side, position_ft=0, state=build_combatant_state(hero))
        ally = EncounterCombatant(combatant_id="ally", side=side, position_ft=80, state=build_combatant_state(build_commoner()))
        remover.state.position = GridPosition(x=0, y=0)
        ally.state.position = GridPosition(x=1, y=0)
        members = {"heroes": [], "monsters": []}; members[side] = [remover, ally]
        other_side = "monsters" if side == "heroes" else "heroes"
        members[other_side] = [EncounterCombatant(combatant_id="opponent", side=other_side, position_ft=60, state=build_combatant_state(hero))]
        members[other_side][0].state.position = GridPosition(x=12, y=0)
        setup = EncounterSetup(**members, hero_total_levels=14, monster_total_cr="0", ruleset=edition)
        return hero, remover, ally, setup, hero.condition_removal_actions[0]
    except Exception:
        logger.exception("Failed removal parity fixture for %s/%s.", edition, side); raise


def test_level_fourteen_cumulative_source_and_independent_fingerprint():
    try:
        hero, previous = build_aurelia_brightshield_2024(14), build_aurelia_brightshield_2024(13)
        profile = build_aurelia_brightshield_2024_profile(14)
        assert hero.name == previous.name and hero.ability_scores == previous.ability_scores
        assert profile.advancement_increases == build_aurelia_brightshield_2024_profile(13).advancement_increases
        assert (hero.max_hp, hero.armor_class, hero.weapon_attack.attack_bonus) == (116, 19, 10)
        assert {r.id: r.max_uses for r in hero.resources} == {
            "lay-on-hands": 70, "spell-slot-1": 4, "spell-slot-2": 3, "spell-slot-3": 3,
            "spell-slot-4": 1, "channel-divinity": 3, "paladins-smite-free-cast": 1, "faithful-steed-free-cast": 1,
        }
        assert canonical_spell_package("paladin", 14, "2024", 3).spells == canonical_spell_package("paladin", 13, "2024", 3).spells
        action = hero.condition_removal_actions[0]
        assert set(action.removable_conditions) == set(RESTORING + ["poisoned"])
        assert (action.max_conditions_per_use, action.action_cost, action.range_ft) == (7, "bonus_action", 5)
        assert action.resource_costs_per_condition == {"lay-on-hands": 5} and not action.expends_spell_slot
        assert next(a for a in profile.feature_audits if a.feature_id == "restoring-touch").automated
        assert previous.condition_removal_actions[0].removable_conditions == ["poisoned"]
        old = build_aurelia_brightshield_2014(14)
        assert old.condition_removal_actions[0].removable_conditions == ["poisoned"]
        assert old.condition_removal_actions[0].action_cost == "action"
        fingerprint = next(p for p in build_aurelia_2024_combat_profiles() if p.level == 14)
        assert_character_build_raw_ready(profile, hero)
        assert_pregen_combat_stats(hero, fingerprint)
        assert_character_resources_raw_ready(hero, profile, fingerprint)
    except Exception:
        logger.exception("Paladin 14 cumulative source/isolation failed."); raise


@pytest.mark.parametrize("side", ["heroes", "monsters"])
def test_one_use_removes_seven_conditions_exact_cost_and_fresh_reset(side):
    try:
        hero, remover, ally, setup, action = _setup(side=side)
        ally.state.current_hp = 1
        ally.state.active_effect_ids = [*RESTORING, "poisoned", "prone"]
        ally.state.timed_effects = [TimedEffect(effect_id=c, source_id="enemy", source_effect_id=c) for c in RESTORING + ["poisoned"]]
        ally.state.timed_effects.append(TimedEffect(effect_id="stunned", source_id="second", source_effect_id="stunned"))
        chosen, target, conditions = choose_condition_removal_action(remover, setup, "1:aurelia")
        assert chosen.id == action.id and target is ally and len(conditions) == 7
        event = resolve_condition_removal(1, 1, remover, ally, chosen, conditions, "1:aurelia")
        assert set(event.removed_condition_ids) == set(RESTORING + ["poisoned"])
        assert "Restoring Touch" in event.description and ally.state.current_hp == 1
        assert event.resource_remaining == 35
        assert ally.state.active_effect_ids == ["prone"] and not ally.state.timed_effects
        assert next(r for r in remover.state.resources if r.id == "lay-on-hands").current_uses == 35
        assert not remover.state.bonus_action_available and remover.state.action_available
        assert remover.state.spell_slot_expended_turn_key is None
        assert choose_condition_removal_action(remover, setup, "1:aurelia") is None
        fresh = build_combatant_state(hero)
        assert fresh.current_hp == 116 and not fresh.timed_effects
        assert next(r for r in fresh.resources if r.id == "lay-on-hands").current_uses == 70
    except Exception:
        logger.exception("Restoring Touch %s-side cost/reset failed.", side); raise


@pytest.mark.parametrize("case", ["duplicate", "over-cap", "poor", "range", "enemy", "restricted", "incapacitated"])
def test_invalid_requests_preserve_every_state_field(case):
    try:
        _, remover, ally, _, action = _setup()
        ally.state.active_effect_ids = ["paralyzed", "deafened"]; conditions = ["paralyzed"]
        if case == "duplicate": conditions *= 2
        elif case == "over-cap": action = action.model_copy(update={"max_conditions_per_use": 1}); conditions.append("deafened")
        elif case == "poor": next(r for r in remover.state.resources if r.id == "lay-on-hands").current_uses = 4
        elif case == "range": ally.state.position = GridPosition(x=0, y=3); ally.position_ft = 0
        elif case == "enemy": ally.side = "monsters"
        elif case == "restricted": ally.state.timed_effects = [TimedEffect(effect_id="paralyzed", source_id="enemy", allowed_removal_action_ids=["different-remedy"])]
        else: remover.state.active_effect_ids = ["stunned"]
        before = [remover.model_dump(), ally.model_dump()]
        with pytest.raises(ValueError): resolve_condition_removal(1, 1, remover, ally, action, conditions, "1:aurelia")
        assert [remover.model_dump(), ally.model_dump()] == before
    except Exception:
        logger.exception("Invalid %s removal was not atomic.", case); raise


def test_any_affordable_legal_subset_can_resolve_independent_of_ai_priority():
    try:
        _, remover, ally, setup, action = _setup()
        pool = next(r for r in remover.state.resources if r.id == "lay-on-hands"); pool.current_uses = 5
        ally.state.active_effect_ids = ["paralyzed", "deafened"]
        assert choose_condition_removal_action(remover, setup, "1:aurelia")[2] == ["paralyzed"]
        resolve_condition_removal(1, 1, remover, ally, action, ["deafened"], "1:aurelia")
        assert ally.state.active_effect_ids == ["paralyzed"] and pool.current_uses == 0
    except Exception:
        logger.exception("Removal legality incorrectly followed Arena priority."); raise


@pytest.mark.parametrize("edition", ["2014", "2024"])
def test_remaining_pool_heals_missing_hp_and_preserves_edition_economy(edition):
    try:
        hero, remover, ally, _, _ = _setup(edition)
        pool = next(r for r in remover.state.resources if r.id == "lay-on-hands"); pool.current_uses = 9
        ally.state.current_hp = 1; action = hero.healing_actions[0]; before = action.model_dump()
        event = resolve_healing(1, 1, remover, ally, action, FixedDiceProvider([1]), "1:aurelia")
        assert (ally.state.current_hp, event.healing_roll.total, pool.current_uses) == (4, 3, 6)
        assert remover.state.bonus_action_available == (edition == "2014")
        assert remover.state.action_available == (edition == "2024") and action.model_dump() == before
        begin_turn(remover.state); ally.state.current_hp = 1; pool.current_uses = 2
        resolve_healing(2, 2, remover, ally, action, FixedDiceProvider([1]), "2:aurelia")
        assert ally.state.current_hp == 3 and pool.current_uses == 0
    except Exception:
        logger.exception("Finite %s Lay On Hands pool allocation failed.", edition); raise


def test_removal_preserves_siblings_then_cleans_last_source_owned_modifiers():
    try:
        _, remover, ally, _, action = _setup()
        ally.state.active_effect_ids = ["blinded", "restrained"]
        ally.state.timed_effects = [TimedEffect(effect_id=c, source_id="enemy", source_effect_id="group") for c in ["blinded", "restrained"]]
        ally.state.active_modifiers = [CombatModifier(id="owned", source_id="enemy", source_effect_id="group", source_name="source", kind=ModifierKind.SPEED, flat_bonus=-5)]
        resolve_condition_removal(1, 1, remover, ally, action, ["blinded"], "1:aurelia")
        assert ally.state.active_effect_ids == ["restrained"]
        assert len(ally.state.timed_effects) == len(ally.state.active_modifiers) == 1
        remove_condition(ally, "restrained")
        assert not ally.state.timed_effects and not ally.state.active_modifiers
    except Exception:
        logger.exception("Removal failed shared source ownership cleanup."); raise


def test_production_support_uses_restoring_touch_and_live_footprint_range():
    try:
        from app.combat.encounter_turn_support import resolve_support_actions
        _, remover, ally, setup, _ = _setup()
        ally.state.template.size = CreatureSize.LARGE
        ally.state.position = GridPosition(x=0, y=1)
        ally.state.active_effect_ids = ["stunned"]
        events, sequence = resolve_support_actions(1, 1, remover, setup, FixedDiceProvider([1]), "1:aurelia")
        assert events[0].removed_condition_ids == ["stunned"]
        assert events[0].resource_remaining == 65 and sequence >= 2
        assert "stunned" not in ally.state.active_effect_ids
        assert not remover.state.bonus_action_available
        # Missing grid authority fails closed even if scalar distance says touch.
        begin_turn(remover.state)
        ally.state.position = None; ally.position_ft = 0; ally.state.active_effect_ids = ["stunned"]
        before = [remover.model_dump(), ally.model_dump()]
        with pytest.raises(RuntimeError): choose_condition_removal_action(remover, setup, "2:aurelia")
        assert [remover.model_dump(), ally.model_dump()] == before
    except Exception:
        logger.exception("Production support/grid condition removal failed."); raise


def test_healing_unavailable_economy_does_not_mark_slot_or_spend_pool():
    try:
        hero, remover, ally, _, _ = _setup()
        ally.state.current_hp = 1
        remover.state.action_available = False; remover.state.bonus_action_available = False
        before = [remover.model_dump(), ally.model_dump()]
        for action in hero.healing_actions:
            with pytest.raises(ValueError): resolve_healing(1, 1, remover, ally, action, FixedDiceProvider([1]), "1:aurelia")
            assert [remover.model_dump(), ally.model_dump()] == before
    except Exception:
        logger.exception("Invalid healing economy was not atomic."); raise


@pytest.mark.parametrize("edition", ["2014", "2024"])
@pytest.mark.parametrize("kind", ["undead", "construct"])
def test_source_owned_lay_on_hands_creature_exclusions(edition, kind):
    try:
        hero, remover, ally, _, action = _setup(edition)
        ally.state.template.creature_type = kind
        ally.state.current_hp = 1; ally.state.active_effect_ids = ["poisoned"]
        if edition == "2014":
            before = [remover.model_dump(), ally.model_dump()]
            with pytest.raises(ValueError): resolve_condition_removal(1, 1, remover, ally, action, ["poisoned"], "1:aurelia")
            with pytest.raises(ValueError): resolve_healing(1, 1, remover, ally, hero.healing_actions[0], FixedDiceProvider([1]), "1:aurelia")
            assert [remover.model_dump(), ally.model_dump()] == before
        else:
            resolve_condition_removal(1, 1, remover, ally, action, ["poisoned"], "1:aurelia")
            begin_turn(remover.state)
            resolve_healing(2, 2, remover, ally, hero.healing_actions[0], FixedDiceProvider([1]), "2:aurelia")
            assert ally.state.current_hp == 4 and "poisoned" not in ally.state.active_effect_ids
    except Exception:
        logger.exception("Edition %s Lay On Hands exclusion failed for %s.", edition, kind); raise
