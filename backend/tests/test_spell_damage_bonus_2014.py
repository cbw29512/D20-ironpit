from app.combat.dice import FixedDiceProvider
from app.combat.spell_attack_resolution import _damage
from app.combat.spell_damage_bonus import matching_spell_damage_bonuses
from app.combat.spell_policy import SpellChoice
from app.combat.spell_resolution import _save_action
from app.combat.state import build_combatant_state
from app.content.sorcerer_draconic_2014_runtime import build_nyra_emberveil_2014
from app.content.wizard_evoker_2014_runtime import build_elian_starweaver_2014


def test_elemental_affinity_matches_fire_once_and_not_force() -> None:
    state = build_combatant_state(build_nyra_emberveil_2014(6))
    fire = matching_spell_damage_bonuses(state, "fireball", "fire")
    force = matching_spell_damage_bonuses(state, "disintegrate", "force")
    assert [(name, amount) for _, name, amount in fire] == [("Elemental Affinity", 4)]
    assert force == []


def test_empowered_evocation_matches_only_selected_evocation_spell_ids() -> None:
    state = build_combatant_state(build_elian_starweaver_2014(10))
    assert matching_spell_damage_bonuses(state, "fire-bolt", "fire")[0][2] == 5
    assert matching_spell_damage_bonuses(state, "fireball", "fire")[0][2] == 5
    assert matching_spell_damage_bonuses(state, "disintegrate", "force") == []


def test_save_spell_conversion_applies_bonus_before_half_damage_resolution() -> None:
    state = build_combatant_state(build_nyra_emberveil_2014(6))
    fireball = next(item for item in state.template.spell_save_actions if item.id == "fireball")
    action = _save_action(SpellChoice(fireball, 3, ("target",)), state)
    assert action.damage_bonus == 4
    assert action.damage_dice_count == 8
    assert action.damage_type == "fire"


def test_spell_attack_bonus_is_flat_and_not_doubled_on_critical() -> None:
    state = build_combatant_state(build_elian_starweaver_2014(10))
    fire_bolt = state.template.spell_attack_actions[0]
    roll, components, names = _damage(
        state,
        fire_bolt,
        True,
        FixedDiceProvider([1, 1, 1, 1]),
    )
    assert roll.rolls == [1, 1, 1, 1]
    assert roll.modifier == 5
    assert roll.total == 9
    assert components[0].modifier == 5
    assert names == ["Empowered Evocation"]
