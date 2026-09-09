from __future__ import annotations

from app.content.monster_catalog import build_monster_catalog, load_monster_rows
from app.content.monster_source_classifier import source_blockers
from app.content.monster_trait_source_audit import parse_trait_names, trait_issues
from app.content.roster import build_arena_roster
from app.domain.catalog import CoverageStatus
from app.domain.traits import CombatTrait


def _row(name: str) -> dict[str, object]:
    return next(row for row in load_monster_rows() if row["name"] == name)


def _monster(name: str):
    return next(monster for monster in build_arena_roster().monsters if monster.name == name)


def test_trait_parser_preserves_multiple_printed_headings() -> None:
    assert parse_trait_names(
        "Pack Tactics. The wolf has Advantage on attack rolls. Sunlight Sensitivity. While in sunlight, it has Disadvantage."
    ) == ["Pack Tactics", "Sunlight Sensitivity"]


def test_wolf_pack_tactics_is_source_derived_and_runtime_backed() -> None:
    wolf = _monster("Wolf")
    assert wolf.source_trait_names == ["Pack Tactics"]
    assert CombatTrait.PACK_TACTICS in wolf.combat_traits
    assert trait_issues(wolf, _row("Wolf")) == []


def test_arena_neutral_trait_remains_fingerprinted() -> None:
    deer = _monster("Deer")
    assert deer.source_trait_names == ["Agile"]
    assert trait_issues(deer, _row("Deer")) == []


def test_xorn_environment_only_traits_are_neutral_in_standard_pit() -> None:
    row = _row("Xorn")
    source_traits = parse_trait_names(row["traits"])
    assert source_traits == ["Earth Glide", "Treasure Sense"]
    probe = _monster("Deer").model_copy(
        update={"source_trait_names": source_traits, "combat_traits": []},
    )
    assert trait_issues(probe, row) == []


def test_water_breathing_is_combat_irrelevant_but_source_fingerprinted() -> None:
    row = _row("Reef Shark")
    monster = _monster("Reef Shark")
    expected_traits = ["Pack Tactics", "Water Breathing"]
    assert parse_trait_names(row["traits"]) == expected_traits
    assert monster.source_trait_names == expected_traits
    assert CombatTrait.PACK_TACTICS in monster.combat_traits
    assert trait_issues(monster, row) == []
    card = next(card for card in build_monster_catalog() if card.name == "Reef Shark")
    assert card.coverage_status is CoverageStatus.RAW_READY
    assert card.runnable_template_id == "srd-reef-shark"
    assert card.blockers == []


def test_target_missing_hp_attack_modifiers_are_universally_compiled() -> None:
    rows = load_monster_rows()
    names = {str(row["name"]) for row in rows}
    catalog = {card.name: card for card in build_monster_catalog()}
    promoted = {"Giant Shark", "Hunter Shark", "Piranha", "Swarm of Piranhas"}
    for name in promoted:
        assert "conditional-attack-modifier" not in source_blockers(_row(name), names)
        monster = _monster(name)
        assert monster.weapon_attack.conditional_attack_modifiers
        modifier = monster.weapon_attack.conditional_attack_modifiers[0]
        assert modifier.trigger == "target_missing_hp"
        assert modifier.mode == "advantage"
        assert catalog[name].coverage_status is CoverageStatus.RAW_READY
        assert catalog[name].blockers == []


def test_sahuagin_blood_frenzy_reuses_target_missing_hp_advantage() -> None:
    monster = _monster("Sahuagin Warrior")
    assert monster.source_trait_names == ["Blood Frenzy", "Limited Amphibiousness", "Shark Telepathy"]
    assert CombatTrait.BLOOD_FRENZY in monster.combat_traits
    assert trait_issues(monster, _row("Sahuagin Warrior")) == []
    card = next(card for card in build_monster_catalog() if card.name == "Sahuagin Warrior")
    assert card.coverage_status is CoverageStatus.RAW_READY
    assert card.blockers == []


def test_other_conditional_attack_modifiers_remain_fail_closed() -> None:
    rows = load_monster_rows()
    names = {str(row["name"]) for row in rows}
    catalog = {card.name: card for card in build_monster_catalog()}
    unsupported = {"Ankheg", "Bugbear Stalker", "Bugbear Warrior", "Doppelganger", "Mimic"}
    detected = {
        str(row["name"])
        for row in rows
        if "conditional-attack-modifier" in source_blockers(row, names)
    }
    assert detected == unsupported
    for name in unsupported:
        card = catalog[name]
        assert card.coverage_status is CoverageStatus.BLOCKED
        assert card.runnable_template_id is None
        assert "monster-combat-mechanics-not-compiled" in card.blockers


def test_unknown_outcome_changing_trait_fails_closed() -> None:
    wolf = _monster("Wolf")
    row = dict(_row("Wolf"))
    row["traits"] = "Spell Reflection. The wolf reflects a spell that misses it."
    drifted = wolf.model_copy(update={"source_trait_names": ["Spell Reflection"], "combat_traits": []})
    assert "uncertified-trait:spell-reflection" in trait_issues(drifted, row)


def test_catalog_blocks_missing_runtime_pack_tactics(monkeypatch) -> None:
    roster = build_arena_roster()
    monsters = [
        monster.model_copy(update={"combat_traits": []}) if monster.name == "Wolf" else monster
        for monster in roster.monsters
    ]
    monkeypatch.setattr(
        "app.content.roster.build_arena_roster",
        lambda: roster.model_copy(update={"monsters": monsters}),
    )
    card = next(item for item in build_monster_catalog() if item.name == "Wolf")
    assert card.coverage_status is CoverageStatus.BLOCKED
    assert card.runnable_template_id is None
    assert "trait-runtime-missing:pack-tactics" in card.blockers
