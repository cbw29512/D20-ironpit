from __future__ import annotations

from app.combat.dice import FixedDiceProvider
from app.combat.encounter_attacks import resolve_encounter_attack
from app.combat.state import build_combatant_state
from app.content.attacks import build_fighter_longsword_attack
from app.content.demo import build_demo_fighter, build_goblin_warrior
from app.domain.character_builds import AbilityScores
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.grid import BattleMapDefinition, GridPosition
from app.domain.models import ResourceDefinition
from app.domain.post_hit_damage import PostHitFailedSave, ResourceBackedPostHitDamage

MAP = BattleMapDefinition(id="post-hit-save", width_squares=8, height_squares=8)


def _thunderous() -> ResourceBackedPostHitDamage:
    return ResourceBackedPostHitDamage(
        source_id="thunderous-smite-test",
        source_name="Thunderous Smite",
        trigger_attack_ids=["aldric-longsword"],
        action_cost="bonus_action",
        printed_spell_level=1,
        base_dice_count=2,
        dice_size=6,
        damage_type="thunder",
        failed_save=PostHitFailedSave(
            save_ability="strength",
            dc_ability="charisma",
            push_ft=10,
            condition_id="prone",
        ),
    )


def _smite() -> ResourceBackedPostHitDamage:
    return ResourceBackedPostHitDamage(
        source_id="radiant-smite-test",
        source_name="Radiant Smite",
        trigger_attack_ids=["aldric-longsword"],
        action_cost="bonus_action",
        printed_spell_level=1,
        base_dice_count=2,
        dice_size=8,
        damage_type="radiant",
    )


def _attacker(options: list[ResourceBackedPostHitDamage]) -> EncounterCombatant:
    attack = build_fighter_longsword_attack()
    attack = attack.model_copy(update={
        "weapon": attack.weapon.model_copy(update={"mastery_property": None}),
    })
    template = build_demo_fighter().model_copy(update={
        "ability_scores": AbilityScores(
            strength=16, dexterity=10, constitution=14,
            intelligence=10, wisdom=10, charisma=14,
        ),
        "weapon_attack": attack,
        "resources": [
            ResourceDefinition(id="spell-slot-1", name="1st-level Spell Slot", max_uses=2),
        ],
        "weapon_masteries": [],
        "progression_features": build_demo_fighter().progression_features.model_copy(update={
            "post_hit_damage_options": options,
        }),
    })
    state = build_combatant_state(template)
    state.position = GridPosition(x=1, y=1)
    return EncounterCombatant(combatant_id="hero", side="heroes", position_ft=0, state=state)


def _target(*, hp: int = 40, immunities: list[str] | None = None) -> EncounterCombatant:
    template = build_goblin_warrior().model_copy(update={
        "id": "target",
        "name": "Target",
        "max_hp": hp,
        "saving_throw_bonuses": {
            "strength": 0, "dexterity": 0, "constitution": 0,
            "intelligence": 0, "wisdom": 0, "charisma": 0,
        },
        "condition_immunities": immunities or [],
    })
    state = build_combatant_state(template)
    state.current_hp = hp
    state.position = GridPosition(x=2, y=1)
    return EncounterCombatant(combatant_id="target", side="monsters", position_ft=5, state=state)


def _fight(options, rolls, *, hp: int = 40, immunities: list[str] | None = None):
    hero = _attacker(options)
    target = _target(hp=hp, immunities=immunities)
    setup = EncounterSetup(
        heroes=[hero], monsters=[target], hero_total_levels=1,
        monster_total_cr="1/4", map_definition=MAP,
    )
    event = resolve_encounter_attack(
        1, 1, hero, target, hero.state.template.weapon_attack, 5,
        FixedDiceProvider(rolls), setup, turn_key="1:hero",
    )
    return hero, target, event


def test_failed_save_pushes_and_applies_prone_without_taking_the_later_option() -> None:
    hero, target, event = _fight([_thunderous(), _smite()], [15, 4, 3, 3, 1])
    sources = [component.source for component in event.damage_components or []]
    assert "Thunderous Smite" in sources
    assert "Radiant Smite" not in sources
    assert hero.state.bonus_action_available is False
    assert hero.state.resources[0].current_uses == 1
    assert "prone" in target.state.active_effect_ids
    assert target.state.position == GridPosition(x=4, y=1)
    assert event.save_succeeded is False
    assert event.save_ability == "strength"
    assert "pushed 10 feet" in event.description


def test_successful_save_keeps_damage_without_push_or_prone() -> None:
    hero, target, event = _fight([_thunderous()], [15, 4, 3, 3, 18])
    assert any(component.source == "Thunderous Smite" for component in event.damage_components or [])
    assert "prone" not in target.state.active_effect_ids
    assert target.state.position == GridPosition(x=2, y=1)
    assert event.save_succeeded is True
    assert hero.state.bonus_action_available is False


def test_later_option_fires_when_the_first_does_not_match_the_attack() -> None:
    skipped = _thunderous().model_copy(update={"trigger_attack_ids": ["other-attack"]})
    hero, target, event = _fight([skipped, _smite()], [15, 4, 6, 6])
    sources = [component.source for component in event.damage_components or []]
    assert sources.count("Radiant Smite") == 1
    assert "Thunderous Smite" not in sources
    assert "prone" not in target.state.active_effect_ids
    assert target.state.position == GridPosition(x=2, y=1)
    assert event.save_dc is None
    assert hero.state.bonus_action_available is False


def test_defeated_target_does_not_save_or_move() -> None:
    hero, target, event = _fight([_thunderous()], [15, 4, 6, 6], hp=1)
    assert target.state.current_hp == 0
    assert "prone" not in target.state.active_effect_ids
    assert target.state.position == GridPosition(x=2, y=1)
    assert event.save_dc is None
    assert hero.state.pending_post_hit_failed_save is None


def test_prone_immunity_still_pushes() -> None:
    _hero, target, event = _fight([_thunderous()], [15, 4, 3, 3, 1], immunities=["prone"])
    assert "prone" not in target.state.active_effect_ids
    assert target.state.position == GridPosition(x=4, y=1)
    assert event.save_succeeded is False
