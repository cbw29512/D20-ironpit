from app.combat.attacks import resolve_attack
from app.combat.dice import FixedDiceProvider
from app.combat.grid_passage import can_pass_through, creature_space_is_difficult
from app.combat.state import build_combatant_state
from app.content.audited_fighter import build_karnok_stoneward
from app.content.capability_registry import build_combatant_from_capabilities
from app.content.monster_catalog import load_monster_rows
from app.content.monster_source_audit import audit_monster_source
from app.domain.encounters import EncounterCombatant


def _row(name: str):
    return next(row for row in load_monster_rows() if row["name"] == name)


def test_ettin_compiles_entirely_from_existing_control_and_modifier_primitives() -> None:
    ettin = build_combatant_from_capabilities("srd-ettin")
    battleaxe, morningstar = ettin.weapon_attack, ettin.alternate_weapon_attacks[0]

    assert battleaxe.knocks_prone_max_size is not None
    assert battleaxe.knocks_prone_max_size.value == "large"
    rider = morningstar.on_hit_modifier_effects[0]
    assert rider.kind == "next-attack-disadvantage"
    assert rider.expires_at_end_of_target_turn is True
    assert audit_monster_source(ettin, _row("Ettin")) == []


def test_fire_giant_reuses_damage_push_and_next_attack_disadvantage_primitives() -> None:
    giant = build_combatant_from_capabilities("srd-fire-giant")
    flame_sword, hammer = giant.weapon_attack, giant.alternate_weapon_attacks[0]

    assert [(part.dice_count, part.dice_size, part.damage_type.value) for part in flame_sword.on_hit_damage] == [(3, 6, "fire")]
    assert [(part.dice_count, part.dice_size, part.damage_type.value) for part in hammer.on_hit_damage] == [(1, 8, "fire")]
    assert hammer.push_target_away_ft == 15
    assert hammer.on_hit_modifier_effects[0].kind == "next-attack-disadvantage"
    assert audit_monster_source(giant, _row("Fire Giant")) == []


def test_specter_life_drain_reduces_max_hp_by_post_defense_damage() -> None:
    specter = build_combatant_from_capabilities("srd-specter")
    attacker = build_combatant_state(specter)
    target_template = build_karnok_stoneward().model_copy(deep=True)
    target_template.damage_resistances.append("necrotic")
    target = build_combatant_state(target_template)
    before_max = target.template.max_hp

    event = resolve_attack(
        1, 1, attacker, target, specter.weapon_attack, 5,
        FixedDiceProvider([15, 6, 4]), actor_event_id="specter", target_event_id="target", spend_action=False,
    )

    assert event.damage_roll is not None and event.damage_roll.total == 5
    assert event.max_hp_before == before_max
    assert event.max_hp_after == before_max - 5
    assert target.max_hp_reduction == 5
    assert audit_monster_source(specter, _row("Specter")) == []


def test_specter_incorporeal_passage_is_universal_movement_data() -> None:
    specter_template = build_combatant_from_capabilities("srd-specter")
    target_template = build_karnok_stoneward().model_copy(deep=True)
    specter = EncounterCombatant(
        combatant_id="specter", side="monsters", position_ft=0,
        state=build_combatant_state(specter_template),
    )
    target = EncounterCombatant(
        combatant_id="target", side="heroes", position_ft=5,
        state=build_combatant_state(target_template),
    )

    assert can_pass_through(specter, target) is True
    assert creature_space_is_difficult(specter, target) is True
