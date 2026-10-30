from app.combat.dice import FixedDiceProvider
from app.combat.regeneration import resolve_start_turn_regeneration
from app.combat.state import build_combatant_state
from app.combat.zero_hp import apply_damage
from app.content.capability_registry import build_combatant_from_capabilities
from app.content.monster_catalog import load_monster_rows
from app.content.monster_source_audit import audit_monster_source
from app.domain.models import DamageType


def _row(name: str):
    return next(row for row in load_monster_rows() if row["name"] == name)


def test_troll_limb_source_derives_regeneration_and_audits_clean() -> None:
    limb = build_combatant_from_capabilities("srd-troll-limb")
    assert limb.regeneration is not None
    assert limb.regeneration.hit_points == 5
    assert set(limb.regeneration.suppressed_by_damage_types) == {DamageType.ACID, DamageType.FIRE}
    assert limb.regeneration.dies_at_start_turn_if_zero_and_suppressed is True
    assert audit_monster_source(limb, _row("Troll Limb")) == []


def test_regeneration_revives_zero_hp_monster_without_suppression() -> None:
    state = build_combatant_state(build_combatant_from_capabilities("srd-troll-limb"))
    outcome = apply_damage(state, state.current_hp, damage_types={DamageType.SLASHING}, dice=FixedDiceProvider([10]))
    assert outcome == "damaged" and state.current_hp == 0 and not state.is_dead
    healed, died = resolve_start_turn_regeneration(state)
    assert (healed, died, state.current_hp, state.is_dead) == (5, False, 5, False)


def test_regeneration_suppression_kills_zero_hp_monster_at_start_turn() -> None:
    state = build_combatant_state(build_combatant_from_capabilities("srd-troll-limb"))
    apply_damage(state, state.current_hp, damage_types={DamageType.FIRE}, dice=FixedDiceProvider([10]))
    assert state.current_hp == 0 and not state.is_dead
    healed, died = resolve_start_turn_regeneration(state)
    assert (healed, died, state.current_hp, state.is_dead) == (0, True, 0, True)


def test_nonlethal_fire_suppresses_one_regeneration_turn_only() -> None:
    state = build_combatant_state(build_combatant_from_capabilities("srd-troll-limb"))
    apply_damage(state, 4, damage_types={DamageType.FIRE}, dice=FixedDiceProvider([10]))
    healed, died = resolve_start_turn_regeneration(state)
    assert (healed, died, state.current_hp) == (0, False, 10)
    healed, died = resolve_start_turn_regeneration(state)
    assert (healed, died, state.current_hp) == (4, False, 14)


def test_positive_hp_regeneration_is_source_derived_and_does_not_revive_zero_hp() -> None:
    oni = build_combatant_from_capabilities("srd-oni")
    guardian = build_combatant_from_capabilities("srd-shield-guardian")
    assert oni.regeneration is not None and oni.regeneration.minimum_current_hp == 1
    assert guardian.regeneration is not None and guardian.regeneration.minimum_current_hp == 1
    assert "trait-source-unsupported:regeneration" not in audit_monster_source(oni, _row("Oni"))
    assert "trait-source-unsupported:regeneration" not in audit_monster_source(guardian, _row("Shield Guardian"))

    state = build_combatant_state(oni)
    state.current_hp = 0
    state.is_alive = True
    state.is_dead = False
    healed, died = resolve_start_turn_regeneration(state)
    assert (healed, died, state.current_hp) == (0, False, 0)
