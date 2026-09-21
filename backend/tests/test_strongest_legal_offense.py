from app.combat.dice import FixedDiceProvider
from app.combat.encounter_combat_turn import resolve_combat_turn
from app.combat.pit_policy import choose_standard_attack
from app.combat.state import build_combatant_state
from app.content.audited_fighter import build_karnok_stoneward
from app.content.monsters import build_commoner
from app.content.monsters_recharge_save import build_hell_hound
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.grid import BattleMapDefinition, GridPosition
from app.domain.weapons import DamageType, Weapon, WeaponAttack, WeaponAttackKind


def _member(template, combatant_id: str, side: str, x: int, y: int) -> EncounterCombatant:
    state = build_combatant_state(template)
    state.position = GridPosition(x=x, y=y)
    return EncounterCombatant(
        combatant_id=combatant_id, side=side, position_ft=x * 5, state=state,
    )


def test_stronger_legal_weapon_beats_weaker_weapon_listed_first() -> None:
    template = build_karnok_stoneward().model_copy(deep=True)
    greatsword = template.weapon_attack
    dagger = WeaponAttack(
        id="test-dagger",
        weapon=Weapon(
            id="dagger", name="Dagger", attack_kind=WeaponAttackKind.MELEE,
            dice_count=1, dice_size=4, damage_type=DamageType.PIERCING,
            animation="stab",
        ),
        attack_bonus=greatsword.attack_bonus,
        damage_bonus=greatsword.damage_bonus,
    )
    template.weapon_attack = dagger
    template.alternate_weapon_attacks = [greatsword]

    actor = _member(template, "fighter", "heroes", 1, 1)
    target = _member(build_commoner(), "target", "monsters", 2, 1)
    setup = EncounterSetup(
        heroes=[actor], monsters=[target], hero_total_levels=1,
        monster_total_cr="0", ruleset="2024",
        map_definition=BattleMapDefinition(id="weapon-priority", width_squares=8, height_squares=8),
    )

    choice = choose_standard_attack(actor, setup)
    assert choice is not None
    assert choice[1].id == greatsword.id


def test_ready_recharge_area_power_precedes_ordinary_multiattack() -> None:
    actor = _member(build_hell_hound(), "hell-hound", "monsters", 1, 1)
    first = _member(build_commoner(), "hero-1", "heroes", 2, 1)
    second = _member(build_commoner(), "hero-2", "heroes", 3, 1)
    setup = EncounterSetup(
        heroes=[first, second], monsters=[actor], hero_total_levels=2,
        monster_total_cr="3", ruleset="2024",
        map_definition=BattleMapDefinition(id="signature-priority", width_squares=10, height_squares=10),
    )

    events, _ = resolve_combat_turn(
        1, 1, actor, first, setup,
        FixedDiceProvider([1, 2, 3, 4, 5, 1, 20]),
    )

    assert any(event.save_dc == 12 for event in events)
    assert not any(event.event_type == "attack" for event in events)
    resource = next(item for item in actor.state.resources if item.id == "fire-breath")
    assert resource.current_uses == 0
