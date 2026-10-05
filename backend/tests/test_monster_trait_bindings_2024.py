from __future__ import annotations

from app.content.demo import build_goblin_warrior
from app.content.monster_trait_bindings_2024 import bind_monster_source_traits_2024
from app.content.monster_trait_source_audit import trait_issues
from app.content.monster_catalog import build_monster_catalog, load_monster_rows
from app.content.roster import build_arena_roster
from app.domain.catalog import CoverageStatus


def _row(name: str) -> dict[str, object]:
    return next(row for row in load_monster_rows() if row["name"] == name)


def test_magic_resistance_reuses_contextual_save_advantage() -> None:
    source = build_goblin_warrior().model_copy(update={
        "name": "Flesh Golem",
        "ruleset": "2024",
        "source_trait_names": [],
    })
    bound = bind_monster_source_traits_2024(source)
    grants = [
        grant for grant in bound.progression_features.saving_throw_advantage_grants
        if grant.source_id == "magic-resistance"
    ]
    assert len(grants) == 1
    grant = grants[0]
    assert grant.source_name == "Magic Resistance"
    assert grant.requires_magical_effect is True
    assert grant.requires_spell_effect is False
    assert set(grant.abilities) == {
        "strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma",
    }


def test_troll_limb_regeneration_source_shape_is_certifiable() -> None:
    from app.content.monsters_zero_engine import build_zero_engine_monsters

    limb = next(item for item in build_zero_engine_monsters() if item.name == "Troll Limb")
    row = _row("Troll Limb")
    assert limb.regeneration is not None
    assert limb.regeneration.amount == 5
    assert {item.value for item in limb.regeneration.suppressed_by_damage_types} == {"acid", "fire"}
    assert limb.regeneration.survives_zero_until_turn is True
    fingerprinted = limb.model_copy(update={"source_trait_names": ["Regeneration", "Troll Spawn"]})
    assert trait_issues(fingerprinted, row) == []


def test_troll_limb_is_raw_ready_in_production_roster() -> None:
    monster = next(item for item in build_arena_roster("2024").monsters if item.name == "Troll Limb")
    assert monster.id == "srd-troll-limb"
    card = next(item for item in build_monster_catalog() if item.name == "Troll Limb")
    assert card.coverage_status is CoverageStatus.RAW_READY
    assert card.runnable_template_id == "srd-troll-limb"
    assert card.blockers == []
