from app.combat.dice import FixedDiceProvider
from app.combat.saving_throws import resolve_save_action
from app.combat.state import build_combatant_state
from app.content.demo import build_goblin_warrior
from app.content.hero_combat_feature_registry import compile_progression_feature_fields
from app.content.shared_progression_traits import apply_progression_combat_traits
from app.domain.models import EncounterCombatant, SavingThrowAction
from app.domain.traits import CombatTrait


def _member(combatant_id: str, side: str, *, ruleset: str, evasion: bool = True):
    traits = [CombatTrait.EVASION] if evasion else []
    template = build_goblin_warrior().model_copy(update={
        "id": combatant_id,
        "name": combatant_id,
        "ruleset": ruleset,
        "combat_traits": traits,
        "max_hp": 30,
    })
    return EncounterCombatant(
        combatant_id=combatant_id,
        side=side,
        position_ft=0,
        state=build_combatant_state(template),
    )


def _blast(save_ability: str = "dexterity") -> SavingThrowAction:
    return SavingThrowAction(
        id="test-blast",
        name="Test Blast",
        save_ability=save_ability,
        dc=15,
        range_ft=30,
        damage_dice_count=2,
        damage_dice_size=6,
        damage_type="fire",
        success_damage="half",
    )


def _resolve(target, *, succeeded: bool, action: SavingThrowAction | None = None):
    actor = _member("caster", "monsters", ruleset="2014", evasion=False)
    return resolve_save_action(
        1, 1, actor, target, action or _blast(), 0, FixedDiceProvider([]),
        spend_action=False, check_resource=False, spend_resource=False,
        shared_damage_rolls=[6, 5], precomputed_save=(None, succeeded),
    )


def test_2014_evasion_success_zero_and_failure_half_preserve_rolls() -> None:
    success_target = _member("assassin-success", "heroes", ruleset="2014")
    success = _resolve(success_target, succeeded=True)
    assert success_target.state.current_hp == 30
    assert success.damage_roll is not None and success.damage_roll.total == 0
    assert success.damage_components[0].rolls == [6, 5]
    assert "Evasion" in success.description

    failure_target = _member("assassin-failure", "heroes", ruleset="2014")
    failure = _resolve(failure_target, succeeded=False)
    assert failure_target.state.current_hp == 25
    assert failure.damage_roll is not None and failure.damage_roll.total == 5


def test_2024_evasion_is_disabled_while_incapacitated() -> None:
    active = _member("rogue-active", "heroes", ruleset="2024")
    active_failure = _resolve(active, succeeded=False)
    assert active.state.current_hp == 25
    assert active_failure.damage_roll is not None and active_failure.damage_roll.total == 5

    incapacitated = _member("rogue-incapacitated", "heroes", ruleset="2024")
    incapacitated.state.active_effect_ids.append("incapacitated")
    disabled = _resolve(incapacitated, succeeded=False)
    assert incapacitated.state.current_hp == 19
    assert disabled.damage_roll is not None and disabled.damage_roll.total == 11
    assert "Evasion" not in disabled.description


def test_evasion_only_modifies_dexterity_saves_for_half_damage() -> None:
    target = _member("wrong-save", "heroes", ruleset="2014")
    result = _resolve(target, succeeded=True, action=_blast("constitution"))
    assert target.state.current_hp == 25
    assert result.damage_roll is not None and result.damage_roll.total == 5


def test_progression_features_bind_to_shared_combat_traits() -> None:
    fields = compile_progression_feature_fields(["cunning-action", "evasion"], 7)
    template = build_goblin_warrior()
    progression = template.progression_features.model_copy(update=fields)
    bound = apply_progression_combat_traits(template.model_copy(update={"progression_features": progression}))
    assert CombatTrait.CUNNING_ACTION in bound.combat_traits
    assert CombatTrait.EVASION in bound.combat_traits
