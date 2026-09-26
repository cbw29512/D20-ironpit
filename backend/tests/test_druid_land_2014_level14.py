from __future__ import annotations

from app.combat.dice import FixedDiceProvider
from app.combat.state import build_combatant_state
from app.combat.targeting_wards import check_targeting_ward
from app.content.druid_2014_spell_package import build_druid_2014_spell_package
from app.content.druid_land_2014_audits import build_druid_land_2014_feature_audits
from app.content.druid_land_2014_runtime import build_thalen_greenbough_2014
from app.domain.encounters import EncounterCombatant


def _member(template, combatant_id: str, side: str) -> EncounterCombatant:
    return EncounterCombatant(
        combatant_id=combatant_id,
        side=side,
        position_ft=0 if side == "heroes" else 5,
        state=build_combatant_state(template),
    )


def _typed_attacker(creature_type: str) -> EncounterCombatant:
    template = build_thalen_greenbough_2014(13).model_copy(
        update={
            "id": f"test-{creature_type}",
            "name": f"Test {creature_type.title()}",
            "creature_type": creature_type,
        },
    )
    return _member(template, f"attacker-{creature_type}", "monsters")


def test_level_fourteen_progression_and_natures_sanctuary_binding() -> None:
    hero = build_thalen_greenbough_2014(14)

    assert hero.level == 14
    assert hero.max_hp == 115
    assert hero.ability_scores.constitution == 16
    assert hero.ability_scores.wisdom == 20
    assert {resource.id: resource.max_uses for resource in hero.resources} == {
        "spell-slot-1": 4,
        "spell-slot-2": 3,
        "spell-slot-3": 3,
        "spell-slot-4": 3,
        "spell-slot-5": 2,
        "spell-slot-6": 1,
        "spell-slot-7": 1,
        "wild-shape": 2,
    }

    ward = next(
        item for item in hero.passive_modifier_grants
        if item.source_id == "natures-sanctuary"
    )
    assert ward.source_name == "Nature's Sanctuary"
    assert ward.kind == "targeting-save-gate"
    assert set(ward.source_creature_types) == {"beast", "plant"}
    assert ward.save_ability == "wisdom"
    assert ward.save_dc == 18
    assert ward.ends_on_owner_attack is False
    assert ward.success_immunity_hours == 24


def test_natures_sanctuary_uses_source_check_result_and_success_immunity() -> None:
    druid = _member(build_thalen_greenbough_2014(14), "thalen14", "heroes")
    beast = _typed_attacker("beast")
    plant = _typed_attacker("plant")
    humanoid = _typed_attacker("humanoid")

    failed = check_targeting_ward(beast, druid, FixedDiceProvider([1]))
    assert failed is not None
    assert failed.succeeded is False
    assert failed.gate.source_effect_id == "natures-sanctuary"

    plant_failed = check_targeting_ward(plant, druid, FixedDiceProvider([1]))
    assert plant_failed is not None
    assert plant_failed.succeeded is False

    assert check_targeting_ward(humanoid, druid, FixedDiceProvider([1])) is None

    succeeded = check_targeting_ward(beast, druid, FixedDiceProvider([20]))
    assert succeeded is not None
    assert succeeded.succeeded is True
    assert beast.state.targeting_gate_immunity_keys

    # The printed 24-hour immunity outlasts any Iron Pit fight, so the fresh
    # combat state remembers this source/target ward for the rest of the match.
    assert check_targeting_ward(beast, druid, FixedDiceProvider([1])) is None


def test_level_fourteen_spell_count_and_audit_are_legal() -> None:
    package = build_druid_2014_spell_package(14, 5)

    assert len(package.spells) == 19
    assert package.spells[-1].id == "transport-via-plants"
    assert package.spells[-1].spell_level == 6
    assert package.spells[-1].required_capabilities == ["arena-out-of-scope"]

    audit = next(
        item for item in build_druid_land_2014_feature_audits(14)
        if item.feature_id == "natures-sanctuary"
    )
    assert audit.combat_relevant is True
    assert audit.automated is True
