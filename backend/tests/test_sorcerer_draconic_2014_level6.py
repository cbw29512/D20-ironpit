from __future__ import annotations

from app.combat.dice import FixedDiceProvider
from app.combat.spell_attack_resolution import resolve_spell_attack
from app.combat.spell_cast_effects import apply_spell_cast_timed_resistance
from app.combat.state import build_combatant_state
from app.content.sorcerer_2014_spell_package import build_sorcerer_2014_spell_package
from app.content.sorcerer_draconic_2014_profile import build_nyra_emberveil_2014_profile
from app.content.monsters import build_commoner
from app.content.sorcerer_draconic_2014_runtime import build_nyra_emberveil_2014
from app.domain.encounters import EncounterCombatant, EncounterSetup


def _nyra() -> EncounterCombatant:
    return EncounterCombatant(
        combatant_id="nyra",
        side="heroes",
        position_ft=0,
        state=build_combatant_state(build_nyra_emberveil_2014(6)),
    )


def test_level_six_elemental_affinity_adds_charisma_to_fire_spell_damage() -> None:
    hero = build_nyra_emberveil_2014(6)
    profile = build_nyra_emberveil_2014_profile(6)

    assert hero.level == 6
    assert profile.level == 6
    assert hero.max_hp == 32
    assert {item.id: item.max_uses for item in hero.resources} == {
        "spell-slot-1": 4,
        "spell-slot-2": 3,
        "spell-slot-3": 3,
        "sorcery-points": 6,
    }

    fire_bolt = next(item for item in hero.spell_attack_actions if item.id == "fire-bolt")
    burning_hands = next(item for item in hero.spell_save_actions if item.id == "burning-hands")
    fireball = next(item for item in hero.spell_save_actions if item.id == "fireball")
    assert (fire_bolt.damage_bonus, burning_hands.damage_bonus, fireball.damage_bonus) == (4, 4, 4)


def test_level_six_elemental_affinity_resistance_is_cast_triggered_and_resource_backed() -> None:
    nyra = _nyra()
    fire_bolt = next(item for item in nyra.state.template.spell_attack_actions if item.id == "fire-bolt")

    applied = apply_spell_cast_timed_resistance(nyra, fire_bolt, 1)
    points = next(item for item in nyra.state.resources if item.id == "sorcery-points")

    assert applied is not None
    assert applied.id == "elemental-affinity-fire-resistance"
    assert points.current_uses == 5
    effect = next(
        item for item in nyra.state.timed_effects
        if item.source_effect_id == "elemental-affinity-fire-resistance"
    )
    assert [item.value for item in effect.owned_damage_resistances] == ["fire"]
    assert effect.expires_round == 601

    assert apply_spell_cast_timed_resistance(nyra, fire_bolt, 2) is None
    assert points.current_uses == 5


def test_level_six_spell_package_has_seven_known_spells() -> None:
    package = build_sorcerer_2014_spell_package(6)

    assert len(package.cantrips) == 5
    assert len(package.spells) == 7
    assert package.spells[-1].id == "clairvoyance"


def test_level_six_spell_attack_resolution_triggers_resistance_without_extra_action() -> None:
    nyra = _nyra()
    enemy_template = build_commoner().model_copy(update={"ruleset": "2014", "max_hp": 20})
    enemy = EncounterCombatant(
        combatant_id="enemy",
        side="monsters",
        position_ft=30,
        state=build_combatant_state(enemy_template),
    )
    setup = EncounterSetup(
        heroes=[nyra],
        monsters=[enemy],
        hero_total_levels=6,
        monster_total_cr="0",
        ruleset="2014",
    )
    fire_bolt = next(item for item in nyra.state.template.spell_attack_actions if item.id == "fire-bolt")

    resolve_spell_attack(
        1, 1, nyra, enemy, fire_bolt, setup, "1:nyra", FixedDiceProvider([15, 5, 5]),
    )

    points = next(item for item in nyra.state.resources if item.id == "sorcery-points")
    assert points.current_uses == 5
    assert nyra.state.action_available is False
    assert any(
        effect.source_effect_id == "elemental-affinity-fire-resistance"
        for effect in nyra.state.timed_effects
    )
