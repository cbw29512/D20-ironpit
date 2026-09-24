from app.combat.condition_immunity import condition_is_immune
from app.combat.grapple import apply_grapple
from app.combat.modifier_stack import add_modifier, effective_speed
from app.combat.movement_defenses import ignores_difficult_terrain
from app.combat.precombat_spells import prepare_defenses
from app.combat.state import begin_turn, build_combatant_state
from app.content.certified_hero_progressions import CERTIFIED_HERO_PROGRESSIONS
from app.content.demo import build_goblin_warrior
from app.content.paladin_devotion_2014_combat_profile import build_aurelia_brightshield_2014_combat_profile
from app.content.paladin_devotion_2014_profile import build_aurelia_brightshield_2014_profile
from app.content.paladin_devotion_2014_runtime import build_aurelia_brightshield_2014
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.modifiers import CombatModifier, ModifierKind
from app.domain.size import CreatureSize


def test_level_thirteen_is_prepared_without_advancing_certification_boundary() -> None:
    level_twelve = build_aurelia_brightshield_2014_profile(12)
    level_thirteen = build_aurelia_brightshield_2014_profile(13)
    runtime = build_aurelia_brightshield_2014(13)
    fingerprint = build_aurelia_brightshield_2014_combat_profile(13)

    assert level_thirteen.character_name == level_twelve.character_name == "Aurelia Brightshield"
    assert level_thirteen.species_id == level_twelve.species_id == "human"
    assert level_thirteen.background_id == level_twelve.background_id == "noble"
    assert level_thirteen.subclass_id == level_twelve.subclass_id == "oath-devotion"
    assert level_thirteen.class_equipment == level_twelve.class_equipment
    assert level_thirteen.advancement_increases == level_twelve.advancement_increases
    assert level_thirteen.final_ability_scores == level_twelve.final_ability_scores

    expected_resources = {
        "lay-on-hands": 65,
        "spell-slot-1": 4,
        "spell-slot-2": 3,
        "spell-slot-3": 3,
        "spell-slot-4": 1,
        "channel-divinity": 1,
    }
    assert {item.id: item.max_uses for item in runtime.resources} == expected_resources
    assert dict(fingerprint.resources) == expected_resources

    audit = next(item for item in level_thirteen.feature_audits if item.feature_id == "devotion-oath-spells-4")
    assert audit.automated is True

    certified = next(
        item for item in CERTIFIED_HERO_PROGRESSIONS
        if item.class_id == "paladin" and item.template_builder is build_aurelia_brightshield_2014
    )
    assert certified.max_level == 12


def test_level_thirteen_guardian_of_faith_reuses_persistent_hazard_schema() -> None:
    runtime = build_aurelia_brightshield_2014(13)
    assert len(runtime.persistent_hazard_actions) == 1
    guardian = runtime.persistent_hazard_actions[0]

    assert guardian.id == "guardian-of-faith"
    assert guardian.name == "Guardian of Faith"
    assert guardian.level == 4
    assert guardian.action_cost == "action"
    assert guardian.cast_range_ft == 30
    assert guardian.duration_rounds == 4800
    assert guardian.footprint_size == CreatureSize.LARGE
    assert guardian.trigger_radius_ft == 10
    assert guardian.save_ability == "dexterity"
    assert guardian.dc == 16
    assert guardian.failure_damage == 20
    assert guardian.success_damage == 10
    assert guardian.damage_type == "radiant"
    assert guardian.max_total_damage == 60



def test_freedom_of_movement_uses_source_owned_universal_movement_defenses() -> None:
    caster = EncounterCombatant(
        combatant_id="aurelia",
        side="heroes",
        position_ft=0,
        state=build_combatant_state(build_aurelia_brightshield_2014(13)),
    )
    enemy = EncounterCombatant(
        combatant_id="enemy",
        side="monsters",
        position_ft=30,
        state=build_combatant_state(build_goblin_warrior().model_copy(update={"ruleset": "2014"})),
    )
    setup = EncounterSetup(
        heroes=[caster],
        monsters=[enemy],
        hero_total_levels=13,
        monster_total_cr="1/4",
        ruleset="2014",
    )

    events, _ = prepare_defenses(setup)

    assert events[0].feature_id == "freedom-of-movement"
    effect = next(item for item in caster.state.timed_effects if item.source_effect_id == "freedom-of-movement")
    assert effect.owned_magical_condition_immunities == ["paralyzed", "restrained"]
    assert effect.difficult_terrain_bypass_scope == "all"
    assert effect.prevents_magical_speed_reduction is True
    assert effect.nonmagical_grapple_escape_movement_cost_ft == 5
    assert condition_is_immune(caster.state, "paralyzed", source_is_magical=True) is True
    assert condition_is_immune(caster.state, "restrained", source_is_magical=True) is True
    assert condition_is_immune(caster.state, "restrained", source_is_magical=False) is False
    assert ignores_difficult_terrain(caster.state, magical=False) is True
    assert ignores_difficult_terrain(caster.state, magical=True) is True


def test_freedom_of_movement_blocks_magical_speed_reduction_but_not_nonmagical_slowing() -> None:
    state = build_combatant_state(build_aurelia_brightshield_2014(13))
    from app.combat.timed_conditions import apply_timed_condition

    apply_timed_condition(
        state,
        "movement-ward",
        "caster",
        source_effect_id="freedom-of-movement",
        prevents_magical_speed_reduction=True,
        use_default_poison_recovery=False,
    )
    add_modifier(state, CombatModifier(
        id="magical-slow",
        source_id="spellcaster",
        source_effect_id="slow-spell",
        source_is_magical=True,
        kind=ModifierKind.SPEED,
        flat_bonus=-10,
    ))
    add_modifier(state, CombatModifier(
        id="mundane-slow",
        source_id="terrain",
        source_effect_id="mundane-slow",
        source_is_magical=False,
        kind=ModifierKind.SPEED,
        flat_bonus=-5,
    ))

    assert effective_speed(state) == 25


def test_freedom_of_movement_spends_five_feet_to_escape_nonmagical_grapple_at_turn_start() -> None:
    state = build_combatant_state(build_aurelia_brightshield_2014(13))
    from app.combat.timed_conditions import apply_timed_condition

    apply_timed_condition(
        state,
        "movement-ward",
        "caster",
        source_effect_id="freedom-of-movement",
        nonmagical_grapple_escape_movement_cost_ft=5,
        prevents_magical_speed_reduction=True,
        use_default_poison_recovery=False,
    )
    apply_grapple(state, "crocodile", 16, 5, restrains=True, source_is_magical=False)

    begin_turn(state)

    assert state.grapple_sources == []
    assert "grappled" not in state.active_effect_ids
    assert "restrained" not in state.active_effect_ids
    assert state.movement_remaining_ft == 25


def test_freedom_of_movement_magical_grapple_does_not_reduce_speed() -> None:
    state = build_combatant_state(build_aurelia_brightshield_2014(13))
    from app.combat.timed_conditions import apply_timed_condition

    apply_timed_condition(
        state,
        "movement-ward",
        "caster",
        source_effect_id="freedom-of-movement",
        prevents_magical_speed_reduction=True,
        owned_magical_condition_immunities=["restrained"],
        use_default_poison_recovery=False,
    )
    applied = apply_grapple(
        state,
        "magical-hand",
        16,
        5,
        restrains=True,
        source_is_magical=True,
    )

    begin_turn(state)

    assert applied == ["grappled"]
    assert state.grapple_sources[0].source_is_magical is True
    assert state.movement_remaining_ft == 30
