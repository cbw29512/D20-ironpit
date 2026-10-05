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


def test_troll_keeps_regeneration_and_binds_loathsome_limbs_abstraction() -> None:
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
    assert len(troll.triggered_extra_attack_stacks) == 1
    limbs = troll.triggered_extra_attack_stacks[0]
    assert limbs.source_id == "loathsome-limbs"
    assert limbs.trigger_damage_type.value == "slashing"
    assert limbs.trigger_damage_minimum == 15
    assert limbs.requires_bloodied is True
    assert limbs.max_stacks == 4 and limbs.max_uses == 4
    assert limbs.exhaustion_per_stack == 1
    assert limbs.attack.attack_bonus == 6
    assert (limbs.attack.weapon.dice_count, limbs.attack.weapon.dice_size, limbs.attack.damage_bonus) == (2, 4, 4)
    assert limbs.clears_on_regeneration_heal is True
    assert trait_issues(troll, row) == []
