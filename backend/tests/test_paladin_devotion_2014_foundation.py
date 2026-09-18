from app.combat.damage import resolve_weapon_damage
from app.combat.dice import FixedDiceProvider
from app.combat.state import build_combatant_state
from app.content.build_audit import audit_character_build
from app.content.demo import build_goblin_warrior
from app.content.paladin_devotion_2014_combat_profile import build_aurelia_brightshield_2014_combat_profile
from app.content.paladin_devotion_2014_profile import build_aurelia_brightshield_2014_profile
from app.content.paladin_devotion_2014_runtime import build_aurelia_brightshield_2014
from app.content.pregen_combat_audit import assert_pregen_combat_stats
from app.content.character_resource_audit import assert_character_resources_raw_ready
from app.domain.models import RollMode


def _state(level: int):
    return build_combatant_state(build_aurelia_brightshield_2014(level))


def _target(*, creature_type: str | None = None):
    template = build_goblin_warrior().model_copy(
        update={"creature_type": creature_type, "max_hp": 200, "ruleset": "2014"},
    )
    return build_combatant_state(template)


def test_aurelia_2014_legal_scores_and_progression_breakpoints() -> None:
    for level in range(1, 11):
        profile = build_aurelia_brightshield_2014_profile(level)
        assert sorted(profile.base_ability_scores.model_dump().values()) == [8, 10, 12, 13, 14, 15]
        assert profile.ruleset == "2014"
        assert profile.weapon_masteries == []
        assert profile.combat_loadout_kind == "one-hander-shield"
        assert profile.fighting_style == ("Defense" if level >= 2 else None)

    assert build_aurelia_brightshield_2014_profile(1).final_ability_scores.strength == 16
    assert build_aurelia_brightshield_2014_profile(4).final_ability_scores.strength == 18
    assert build_aurelia_brightshield_2014_profile(8).final_ability_scores.charisma == 17
    assert build_aurelia_brightshield_2014_profile(3).subclass_id == "oath-devotion"


def test_aurelia_runtime_and_fingerprint_match_levels_one_through_ten() -> None:
    for level in range(1, 11):
        runtime = build_aurelia_brightshield_2014(level)
        build_profile = build_aurelia_brightshield_2014_profile(level)
        fingerprint = build_aurelia_brightshield_2014_combat_profile(level)
        assert_pregen_combat_stats(runtime, fingerprint)
        assert_character_resources_raw_ready(runtime, build_profile, fingerprint)
        assert runtime.armor_class == (18 if level == 1 else 19)
        assert runtime.max_hp == 12 + (level - 1) * 8
        assert runtime.weapon_attack.weapon.mastery_property is None
        assert all(attack.weapon.mastery_property is None for attack in runtime.alternate_weapon_attacks)

    assert build_aurelia_brightshield_2014(1).attack_action is None
    assert len(build_aurelia_brightshield_2014(5).attack_action.slots) == 2
    assert build_aurelia_brightshield_2014(6).progression_features.aura_of_protection_2014_bonus == 2
    assert build_aurelia_brightshield_2014(8).progression_features.aura_of_protection_2014_bonus == 3
    assert "charmed" in build_aurelia_brightshield_2014(7).condition_immunities
    assert "frightened" in build_aurelia_brightshield_2014(10).condition_immunities


def test_aurelia_levels_one_through_ten_are_build_audit_ready() -> None:
    for level in range(1, 11):
        issues = audit_character_build(
            build_aurelia_brightshield_2014_profile(level),
            build_aurelia_brightshield_2014(level),
        )
        assert issues == []


def test_divine_smite_spends_slot_only_on_melee_damage_resolution() -> None:
    attacker = _state(2)
    defender = _target()
    _, components = resolve_weapon_damage(
        attacker,
        attacker.template.weapon_attack,
        FixedDiceProvider([4, 5, 6]),
        False,
        RollMode.NORMAL,
        "1:aurelia",
        target=defender,
    )
    smite = next(component for component in components if component.source == "Divine Smite")
    assert smite.notation == "2d8+0"
    assert next(item for item in attacker.resources if item.id == "spell-slot-1").current_uses == 1

    ranged = _state(2)
    _, ranged_components = resolve_weapon_damage(
        ranged,
        ranged.template.alternate_weapon_attacks[0],
        FixedDiceProvider([4]),
        False,
        RollMode.NORMAL,
        "1:aurelia-ranged",
        target=defender,
    )
    assert all(component.source != "Divine Smite" for component in ranged_components)
    assert next(item for item in ranged.resources if item.id == "spell-slot-1").current_uses == 2


def test_divine_smite_uses_highest_slot_scales_for_undead_and_doubles_on_critical() -> None:
    attacker = _state(5)
    undead = _target(creature_type="undead")
    _, components = resolve_weapon_damage(
        attacker,
        attacker.template.weapon_attack,
        FixedDiceProvider([4, 1, 2, 3, 4]),
        False,
        RollMode.NORMAL,
        "1:aurelia",
        target=undead,
    )
    smite = next(component for component in components if component.source == "Divine Smite")
    assert smite.notation == "4d8+0"
    assert next(item for item in attacker.resources if item.id == "spell-slot-2").current_uses == 1

    critical = _state(2)
    _, critical_components = resolve_weapon_damage(
        critical,
        critical.template.weapon_attack,
        FixedDiceProvider([1, 2, 3, 4, 5, 6]),
        True,
        RollMode.NORMAL,
        "1:aurelia-critical",
        target=_target(),
    )
    critical_smite = next(component for component in critical_components if component.source == "Divine Smite")
    assert critical_smite.notation == "4d8+0"
