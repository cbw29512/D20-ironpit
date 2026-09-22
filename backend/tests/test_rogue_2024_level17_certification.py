from __future__ import annotations

from app.combat.dice import FixedDiceProvider
from app.combat.encounter_events import build_initiative_events
from app.combat.encounter_initiative import roll_encounter_initiative
from app.combat.encounter_setup import build_encounter_setup
from app.content.audited_rogue import build_mara_quickstep_level, unsupported_mara_rogue_features
from app.content.certified_heroes import build_certified_hero_registry
from app.content.rogue_combat_fingerprint import build_mara_quickstep_level17_combat_profile
from app.content.rogue_final_progression_profile import build_mara_quickstep_level17_profile
from app.domain.models import EncounterSelection


def test_2024_rogue_level17_reuses_source_tagged_extra_turn_grant() -> None:
    level16 = build_mara_quickstep_level(16)
    template = build_mara_quickstep_level(17)

    assert unsupported_mara_rogue_features(17) == ()
    assert template.id == "mara-quickstep-l17"
    assert template.level == 17
    assert template.ability_scores is not None
    assert (
        template.ability_scores.dexterity,
        template.ability_scores.constitution,
        template.ability_scores.wisdom,
    ) == (20, 20, 12)
    assert (template.armor_class, template.max_hp, template.initiative_bonus) == (16, 173, 5)
    assert template.max_hp - level16.max_hp == 10
    assert (template.weapon_attack.attack_bonus, template.weapon_attack.damage_bonus) == (11, 5)
    assert template.saving_throw_bonuses == {
        "strength": 1, "dexterity": 11, "constitution": 5,
        "intelligence": 6, "wisdom": 7, "charisma": 6,
    }
    assert template.progression_features.sneak_attack_d6 == 9

    grants = template.progression_features.first_round_extra_turn_grants
    assert len(grants) == 1
    assert grants[0].source_id == "thiefs-reflexes"
    assert grants[0].source_name == "Thief's Reflexes"
    assert grants[0].initiative_offset == -10


def test_thiefs_reflexes_uses_shared_round_one_schedule_and_exact_log_name() -> None:
    setup = build_encounter_setup(EncounterSelection(
        hero_ids=["mara-quickstep-l17"],
        monster_ids=["srd-commoner"],
    ))
    initiative = roll_encounter_initiative(setup, FixedDiceProvider([15, 12]))
    mara_id = setup.heroes[0].combatant_id
    monster_id = setup.monsters[0].combatant_id

    assert initiative.turn_order == [mara_id, monster_id]
    assert initiative.first_round_turn_order == [mara_id, monster_id, mara_id]
    assert initiative.first_round_turn_order.count(mara_id) == 2
    assert initiative.turn_order.count(mara_id) == 1
    assert len(initiative.first_round_extra_turns) == 1

    extra = initiative.first_round_extra_turns[0]
    assert extra.combatant_id == mara_id
    assert extra.initiative_count == 10
    assert extra.source_id == "thiefs-reflexes"
    assert extra.source_name == "Thief's Reflexes"

    events, _ = build_initiative_events(initiative, 1)
    feature = next(event for event in events if event.feature_id == "thiefs-reflexes")
    assert "Thief's Reflexes" in feature.description
    assert "Initiative 10" in feature.description


def test_2024_rogue_level17_profile_fingerprint_and_registry_match() -> None:
    profile = build_mara_quickstep_level17_profile()
    audits = {item.feature_id: item for item in profile.feature_audits}
    assert profile.level == 17
    assert audits["thiefs-reflexes"].combat_relevant is True
    assert audits["thiefs-reflexes"].automated is True

    fingerprint = build_mara_quickstep_level17_combat_profile()
    assert fingerprint.abilities.wisdom == 12
    assert (fingerprint.armor_class, fingerprint.max_hp, fingerprint.sneak_attack_d6) == (16, 173, 9)
    assert ("adrenaline-rush", 6) in fingerprint.resources

    registry = build_certified_hero_registry()
    assert registry[("rogue", 17, "canonical")] == ("Mara Quickstep", "mara-quickstep-l17")
