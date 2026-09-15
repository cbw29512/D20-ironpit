from app.combat.charge_prone import resolve_charge_prone
from app.combat.dice import FixedDiceProvider
from app.combat.state import build_combatant_state
from app.content.demo import build_demo_fighter
from app.content.monster_catalog_2014 import MVP_CATALOG_PATH, monster_by_id_2014
from app.domain.charge_profiles import ChargeDamageDefinition, ChargeProfileDefinition
from app.domain.encounters import EncounterCombatant
from app.domain.events import BattleEvent


def test_2014_compiler_provides_all_six_saving_throw_bonuses() -> None:
    bandit = monster_by_id_2014("bandit", MVP_CATALOG_PATH)
    assert bandit.saving_throw_bonuses == {
        "strength": 0,
        "dexterity": 1,
        "constitution": 1,
        "intelligence": 0,
        "wisdom": 0,
        "charisma": 0,
    }


def test_charge_prone_uses_printed_save_instead_of_automatic_prone() -> None:
    target = EncounterCombatant(
        combatant_id="target",
        side="heroes",
        position_ft=0,
        state=build_combatant_state(build_demo_fighter()),
    )
    profile = ChargeProfileDefinition(
        minimum_move_ft=20,
        prone_save_ability="strength",
        prone_save_dc=20,
        bonus_damage=ChargeDamageDefinition(
            dice_count=1, dice_size=6, damage_type="piercing"
        ),
    )
    event = BattleEvent(
        sequence=1,
        round_number=1,
        event_type="attack",
        actor_id="charger",
        actor_name="Charger",
        target_id="target",
        target_name="Aldric Vane",
        hit=True,
        animation="strike",
        description="Charger hits.",
    )

    resolved = resolve_charge_prone(event, target, profile, FixedDiceProvider([1]), None)

    assert resolved.save_dc == 20
    assert resolved.save_succeeded is False
    assert "prone" in target.state.active_effect_ids
    assert "prone" in resolved.applied_condition_ids


def test_form_qualified_pounce_binds_to_weretiger_claw() -> None:
    weretiger = monster_by_id_2014("weretiger")
    attacks = [weretiger.weapon_attack, *weretiger.alternate_weapon_attacks]
    claw = next(attack for attack in attacks if attack.weapon.name.startswith("Claw"))

    assert claw.charge_profile is not None
    assert claw.charge_profile.minimum_move_ft == 15
    assert claw.charge_profile.prone_save_dc == 14
    assert claw.charge_profile.follow_up_attack_id == "bite-tiger-or-hybrid-form-only"


def test_wereboar_compiles_with_form_qualified_charge_and_arena_neutral_curse() -> None:
    wereboar = monster_by_id_2014("wereboar")
    attacks = [wereboar.weapon_attack, *wereboar.alternate_weapon_attacks]
    tusks = next(attack for attack in attacks if attack.weapon.name.startswith("Tusks"))

    assert tusks.charge_profile is not None
    assert tusks.charge_profile.minimum_move_ft == 15
    assert tusks.charge_profile.prone_save_dc == 13
