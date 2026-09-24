from app.combat.condition_immunity import condition_is_immune
from app.combat.defensive_modifier_rules import attacks_against_disadvantage_sources
from app.combat.state import build_combatant_state
from app.content.paladin_devotion_2014_profile import build_aurelia_brightshield_2014_profile
from app.content.paladin_devotion_2014_runtime import build_aurelia_brightshield_2014


def test_level_15_is_incremental_purity_of_spirit_progression() -> None:
    level14 = build_aurelia_brightshield_2014(14)
    hero = build_aurelia_brightshield_2014(15)
    profile = build_aurelia_brightshield_2014_profile(15)

    assert hero.max_hp > level14.max_hp
    assert hero.ability_scores == level14.ability_scores
    assert {item.id: item.max_uses for item in hero.resources if item.id.startswith("spell-slot-")} == {
        "spell-slot-1": 4,
        "spell-slot-2": 3,
        "spell-slot-3": 3,
        "spell-slot-4": 2,
    }
    assert len(hero.passive_modifier_grants) == 3
    assert {item.source_id for item in hero.passive_modifier_grants} == {"purity-of-spirit"}

    audits = {item.feature_id: item for item in profile.feature_audits}
    assert audits["purity-of-spirit"].combat_relevant is True
    assert audits["purity-of-spirit"].automated is True


def test_purity_of_spirit_reuses_source_typed_modifier_rules() -> None:
    hero = build_aurelia_brightshield_2014(15)
    state = build_combatant_state(hero)
    fiend = build_aurelia_brightshield_2014(14).model_copy(
        update={"id": "test-fiend", "name": "Test Fiend", "creature_type": "fiend"},
    )
    humanoid = build_aurelia_brightshield_2014(14).model_copy(
        update={"id": "test-humanoid", "name": "Test Humanoid", "creature_type": "humanoid"},
    )

    assert attacks_against_disadvantage_sources(state, fiend) == 1
    assert attacks_against_disadvantage_sources(state, humanoid) == 0
    assert condition_is_immune(state, "charmed", fiend) is True
    assert condition_is_immune(state, "frightened", fiend) is True
    assert condition_is_immune(state, "charmed", humanoid) is False
    assert condition_is_immune(state, "frightened", humanoid) is False
    assert all(item.source_effect_id == "purity-of-spirit" for item in state.active_modifiers)
    assert all(item.source_name == "Purity of Spirit" for item in state.active_modifiers)


def test_purity_of_spirit_passives_rebuild_with_fresh_combat_state() -> None:
    hero = build_aurelia_brightshield_2014(15)
    first = build_combatant_state(hero)
    assert len(first.active_modifiers) == 3

    first.active_modifiers.clear()
    rebuilt = build_combatant_state(hero)

    assert len(first.active_modifiers) == 0
    assert len(rebuilt.active_modifiers) == 3
    assert len(hero.passive_modifier_grants) == 3
