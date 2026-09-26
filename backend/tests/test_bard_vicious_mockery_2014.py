from __future__ import annotations

import pytest

from app.combat.dice import FixedDiceProvider
from app.combat.encounter_attacks import resolve_encounter_attack
from app.combat.spell_policy import SpellChoice, choose_spell
from app.combat.spell_resolution import resolve_spell
from app.combat.state import build_combatant_state
from app.content.bard_2014_vicious_mockery import vicious_mockery_2014
from app.content.bard_lore_2014_runtime import build_lyra_silverstring_2014
from app.content.monsters import build_commoner
from app.domain.encounters import EncounterCombatant, EncounterSetup


def _member(template, combatant_id: str, side: str, position: int) -> EncounterCombatant:
    return EncounterCombatant(
        combatant_id=combatant_id,
        side=side,
        position_ft=position,
        state=build_combatant_state(template),
    )


@pytest.mark.parametrize(
    ("level", "dice_count"),
    [(1, 1), (5, 2), (11, 3), (17, 4)],
)
def test_vicious_mockery_uses_2014_cantrip_scaling(level: int, dice_count: int) -> None:
    charisma = build_lyra_silverstring_2014(level).ability_scores.modifier("charisma")
    spell = vicious_mockery_2014(level, charisma)

    assert spell.level == 0
    assert spell.action_cost == "action"
    assert spell.range_ft == 60
    assert spell.save_ability == "wisdom"
    assert spell.damage_dice_count == dice_count
    assert spell.damage_dice_size == 4
    assert spell.damage_type == "psychic"
    assert spell.success_damage == "none"
    assert spell.requires_target_hearing is True
    assert spell.requires_target_sight is True
    assert spell.failed_save_timed_effect is not None
    assert spell.failed_save_timed_effect.next_attack_disadvantage is True


def test_failed_vicious_mockery_save_disadvantages_and_consumes_next_attack() -> None:
    lyra = _member(build_lyra_silverstring_2014(1), "lyra", "heroes", 0)
    enemy_template = build_commoner().model_copy(update={
        "ruleset": "2014",
        "max_hp": 10,
        "saving_throw_bonuses": {
            "strength": 0,
            "dexterity": 0,
            "constitution": 0,
            "intelligence": 0,
            "wisdom": 0,
            "charisma": 0,
        },
    })
    enemy = _member(enemy_template, "enemy", "monsters", 30)
    setup = EncounterSetup(
        heroes=[lyra],
        monsters=[enemy],
        hero_total_levels=1,
        monster_total_cr="0",
        ruleset="2014",
    )
    spell = lyra.state.template.spell_save_actions[0]
    choice = SpellChoice(spell, 0, (enemy.combatant_id,))

    events, _ = resolve_spell(
        1,
        1,
        lyra,
        setup,
        choice,
        "1:lyra",
        FixedDiceProvider([1, 4]),
    )

    save_event = events[1]
    assert save_event.feature_id == "vicious-mockery"
    assert save_event.save_succeeded is False
    assert save_event.damage_roll is not None
    assert save_event.damage_roll.total == 4
    rider = next(
        effect
        for effect in enemy.state.timed_effects
        if effect.source_effect_id == "vicious-mockery"
    )
    assert rider.effect_id == "vicious-mockery-disadvantage"
    assert rider.expiry_timing == "target_turn_end"
    assert rider.next_attack_disadvantage is True

    attack = resolve_encounter_attack(
        3,
        1,
        enemy,
        lyra,
        enemy.state.template.weapon_attack,
        30,
        FixedDiceProvider([18, 2]),
        setup,
        spend_action=True,
        turn_key="1:enemy",
    )

    assert attack.attack_roll is not None
    assert attack.attack_roll.mode.value == "disadvantage"
    assert attack.attack_roll.rolls == [18, 2]
    assert not any(effect.next_attack_disadvantage for effect in enemy.state.timed_effects)


def test_vicious_mockery_policy_skips_deafened_or_unseen_targets() -> None:
    lyra = _member(build_lyra_silverstring_2014(1), "lyra", "heroes", 0)
    enemy = _member(
        build_commoner().model_copy(update={"ruleset": "2014"}),
        "enemy",
        "monsters",
        30,
    )
    setup = EncounterSetup(
        heroes=[lyra],
        monsters=[enemy],
        hero_total_levels=1,
        monster_total_cr="0",
        ruleset="2014",
    )

    enemy.state.active_effect_ids.append("deafened")
    assert choose_spell(lyra, setup, "1:lyra") is None

    enemy.state.active_effect_ids = ["invisible"]
    assert choose_spell(lyra, setup, "1:lyra") is None
