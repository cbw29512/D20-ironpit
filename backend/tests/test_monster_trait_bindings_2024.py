from __future__ import annotations

from app.content.demo import build_goblin_warrior
from app.content.monster_trait_bindings_2024 import bind_monster_source_traits_2024
from app.content.monster_trait_source_audit import trait_issues
from app.content.monster_catalog import load_monster_rows


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


def test_troll_keeps_regeneration_while_loathsome_limbs_is_arena_neutral() -> None:
    source = build_goblin_warrior().model_copy(update={
        "name": "Troll",
        "ruleset": "2024",
        "source_trait_names": [],
    })
    troll = bind_monster_source_traits_2024(source)
    row = _row("Troll")
    assert troll.regeneration is not None
    assert troll.regeneration.amount == 15
    assert {item.value for item in troll.regeneration.suppressed_by_damage_types} == {"acid", "fire"}
    assert troll.regeneration.survives_zero_until_turn is True
    issues = trait_issues(troll, row)
    assert "uncertified-trait:loathsome-limbs" not in issues
    assert not any("regeneration" in issue for issue in issues)
