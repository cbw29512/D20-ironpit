from app.combat.ability_check_escape import resolve_escape_check, should_escape_check
from app.combat.dice import FixedDiceProvider
from app.combat.state import build_combatant_state
from app.combat.timed_conditions import apply_timed_condition
from app.content.arena_map import build_standard_iron_pit_map
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.grid import GridPosition
from app.domain.models import CombatantTemplate, VisualLoadout, Weapon, WeaponAttack, WeaponAttackKind
from app.domain.character_builds import AbilityScores


def _member() -> EncounterCombatant:
    template = CombatantTemplate(
        id="test-hero", name="Test Hero", archetype="Test", kind="character",
        armor_class=16, max_hp=30, speed_ft=30, initiative_bonus=1,
        ability_scores=AbilityScores(strength=16, dexterity=14, constitution=14, intelligence=10, wisdom=10, charisma=10),
        weapon_attack=WeaponAttack(
            id="club",
            weapon=Weapon(
                id="club", name="Club", attack_kind=WeaponAttackKind.MELEE,
                dice_count=1, dice_size=4, damage_type="bludgeoning", animation="slash",
            ),
            attack_bonus=5, damage_bonus=3,
        ),
        visual=VisualLoadout(armor="clothes", main_hand="club", body_style="humanoid"),
        source="test",
        saving_throw_bonuses={
            "strength": 3, "dexterity": 2, "constitution": 2,
            "intelligence": 0, "wisdom": 0, "charisma": 0,
        },
    )
    member = EncounterCombatant(
        combatant_id="hero", side="heroes", position_ft=25,
        state=build_combatant_state(template),
    )
    member.state.position = GridPosition(x=5, y=5)
    return member


def test_escape_check_spends_action_and_can_end_restrained() -> None:
    actor = _member()
    apply_timed_condition(
        actor.state, "restrained", "unicorn",
        source_effect_id="entangle",
        applied_round=1,
        expires_round=11,
        expiry_timing="source_turn_end",
        escape_check_ability="strength",
        escape_check_dc=14,
        use_default_poison_recovery=False,
    )
    assert should_escape_check(actor.state)
    dummy = _member()
    dummy.combatant_id = "dummy"
    dummy.side = "monsters"
    setup = EncounterSetup(
        heroes=[actor], monsters=[dummy], hero_total_levels=1, monster_total_cr="5",
        ruleset="2014", map_definition=build_standard_iron_pit_map(),
    )
    event = resolve_escape_check(1, 1, actor, FixedDiceProvider([20]), setup=setup)
    assert event.check_succeeded is True
    assert event.feature_id == "escape-check"
    assert "restrained" not in actor.state.active_effect_ids
    assert actor.state.action_available is False
