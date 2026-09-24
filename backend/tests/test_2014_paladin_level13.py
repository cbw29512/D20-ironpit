from app.combat.precombat_spells import choose_defensive_spell
from app.combat.state import build_combatant_state
from app.content.canonical_hero_policy import canonical_spell_package
from app.content.certified_heroes import build_certified_hero_entries_for_ruleset
from app.content.paladin_devotion_2014_audits import build_paladin_2014_feature_audits
from app.content.paladin_devotion_2014_runtime import build_aurelia_brightshield_2014
from app.domain.encounters import EncounterCombatant


def _resources(template) -> dict[str, int]:
    return {item.id: item.max_uses for item in template.resources}


def test_aurelia_level_13_adds_fourth_level_slots_without_rebuilding_the_character() -> None:
    level12 = build_aurelia_brightshield_2014(12)
    hero = build_aurelia_brightshield_2014(13)

    assert hero.name == level12.name == "Aurelia Brightshield"
    assert hero.ruleset == level12.ruleset == "2014"
    assert hero.ability_scores == level12.ability_scores
    assert hero.armor_class == level12.armor_class
    assert hero.max_hp > level12.max_hp
    assert _resources(hero)["spell-slot-1"] == 4
    assert _resources(hero)["spell-slot-2"] == 3
    assert _resources(hero)["spell-slot-3"] == 3
    assert _resources(hero)["spell-slot-4"] == 1


def test_level_13_runtime_uses_death_ward_and_freedom_of_movement_not_guardian_entity() -> None:
    hero = build_aurelia_brightshield_2014(13)
    defensive = {spell.id for spell in hero.defensive_spell_actions}

    assert "death-ward" in defensive
    assert "freedom-of-movement" in defensive
    assert "guardian-of-faith" not in defensive

    state = build_combatant_state(hero)
    member = EncounterCombatant(combatant_id="aurelia", side="heroes", position_ft=0, state=state)
    choice = choose_defensive_spell(member)
    assert choice is not None
    assert choice[0].id == "death-ward"
    assert choice[1] == 4


def test_guardian_of_faith_remains_source_visible_but_arena_unavailable() -> None:
    package = canonical_spell_package("paladin", 13, "2014", 3)
    assert package is not None

    oath = {spell.id: spell for spell in package.always_prepared_spells}
    assert "freedom-of-movement" in oath
    assert "guardian-of-faith" in oath
    assert oath["guardian-of-faith"].required_capabilities == ["arena-unavailable-summon"]

    audits = {item.feature_id: item for item in build_paladin_2014_feature_audits(13)}
    guardian = audits["guardian-of-faith"]
    assert guardian.combat_relevant is False
    assert guardian.automated is False
    assert audits["death-ward"].automated is True


def test_level_13_is_registered_for_2014_paladin_certification() -> None:
    registry = {
        key: (template.name, template.id)
        for key, template in build_certified_hero_entries_for_ruleset("2014")
    }
    assert registry[("paladin", 13, "canonical-2014")] == (
        "Aurelia Brightshield",
        "aurelia-brightshield-2014-l13",
    )
