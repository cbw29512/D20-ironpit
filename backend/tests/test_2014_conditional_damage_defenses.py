from __future__ import annotations

from app.combat.damage_defenses import adjusted_damage_amount
from app.combat.state import build_combatant_state
from app.content.capability_compiler import compile_combatant
from app.content.monster_basic_candidates_2014 import basic_blockers_2014
from app.content.monster_conditional_damage_defenses_2014 import (
    conditional_damage_defenses_2014,
    remaining_unsupported_defense_text_2014,
)
from app.content.monster_definition_adapter_2014 import adapt_basic_monster_2014
from app.content.monster_source_2014 import load_monster_source_2014
from app.domain.damage_sources import DamageDefenseKind, DamageSourceQualifier
from app.domain.weapons_base import DamageType

_ORDINARY_ATTACK = {
    DamageSourceQualifier.ATTACK,
    DamageSourceQualifier.WEAPON,
    DamageSourceQualifier.MELEE,
}
_NON_ATTACK = {DamageSourceQualifier.WEAPON, DamageSourceQualifier.MELEE}


def _monster(monster_id: str):
    return next(item for item in load_monster_source_2014() if item.id == monster_id)


def test_2014_nonmagical_defense_family_binds_all_printed_clauses() -> None:
    source = load_monster_source_2014()
    with_defense = [item for item in source if item.unsupported_defense_text]
    assert len(with_defense) == 58

    bound = []
    leftover = []
    for monster in with_defense:
        defenses = conditional_damage_defenses_2014(monster)
        remaining = remaining_unsupported_defense_text_2014(monster)
        if remaining:
            leftover.append((monster.id, remaining))
        else:
            bound.append(monster.id)
            assert len(defenses) == len(monster.unsupported_defense_text)

    assert set(bound) == {item.id for item in with_defense} - {"rakshasa"}
    assert leftover == [(
        "rakshasa",
        ["piercing from magic weapons wielded by good creatures"],
    )]
    rakshasa = _monster("rakshasa")
    assert [item.kind for item in conditional_damage_defenses_2014(rakshasa)] == [
        DamageDefenseKind.IMMUNITY,
    ]
    assert "mechanic:defense" in basic_blockers_2014(rakshasa)
    clay = _monster("clay-golem")
    assert remaining_unsupported_defense_text_2014(clay) == []
    assert "mechanic:defense" not in basic_blockers_2014(clay)
    assert "source:trait" not in basic_blockers_2014(clay)


def test_2014_silvered_and_adamantine_qualifiers_use_shared_forbidden_set() -> None:
    werewolf = conditional_damage_defenses_2014(_monster("werewolf"))[0]
    gargoyle = conditional_damage_defenses_2014(_monster("gargoyle"))[0]
    xorn = conditional_damage_defenses_2014(_monster("xorn"))[0]
    banshee = conditional_damage_defenses_2014(_monster("banshee"))[0]

    assert werewolf.kind is DamageDefenseKind.IMMUNITY
    assert set(werewolf.forbidden_source_qualifiers) == {
        DamageSourceQualifier.MAGICAL, DamageSourceQualifier.SILVERED,
    }
    assert gargoyle.kind is DamageDefenseKind.RESISTANCE
    assert set(gargoyle.forbidden_source_qualifiers) == {
        DamageSourceQualifier.MAGICAL, DamageSourceQualifier.ADAMANTINE,
    }
    assert [item.value for item in xorn.damage_types] == ["piercing", "slashing"]
    assert banshee.kind is DamageDefenseKind.RESISTANCE
    assert banshee.forbidden_source_qualifiers == [DamageSourceQualifier.MAGICAL]
    assert banshee.required_source_qualifiers == [DamageSourceQualifier.ATTACK]


def test_gargoyle_unlocks_and_keeps_printed_adamantine_bypass() -> None:
    source = _monster("gargoyle")
    assert basic_blockers_2014(source) == ()
    template = compile_combatant(adapt_basic_monster_2014(source))
    assert template.id == "2014-gargoyle"
    assert len(template.conditional_damage_defenses) == 1
    defense = template.conditional_damage_defenses[0]
    assert defense.kind is DamageDefenseKind.RESISTANCE
    assert DamageSourceQualifier.ADAMANTINE in defense.forbidden_source_qualifiers

    gargoyle = build_combatant_state(template)
    assert adjusted_damage_amount(
        10, DamageType.SLASHING, gargoyle, source_qualifiers=_ORDINARY_ATTACK,
    ) == 5
    assert adjusted_damage_amount(
        10, DamageType.SLASHING, gargoyle,
        source_qualifiers={*_ORDINARY_ATTACK, DamageSourceQualifier.ADAMANTINE},
    ) == 10
    assert adjusted_damage_amount(
        10, DamageType.SLASHING, gargoyle,
        source_qualifiers={*_ORDINARY_ATTACK, DamageSourceQualifier.MAGICAL},
    ) == 10
    assert adjusted_damage_amount(
        10, DamageType.SLASHING, gargoyle, source_qualifiers=_NON_ATTACK,
    ) == 10
    assert adjusted_damage_amount(
        10, DamageType.FIRE, gargoyle, source_qualifiers=_ORDINARY_ATTACK,
    ) == 10


def test_werewolf_immunity_is_bypassed_by_silvered_or_magical_attacks() -> None:
    defense = conditional_damage_defenses_2014(_monster("werewolf"))[0]
    from app.content.demo import build_demo_fighter

    target = build_combatant_state(build_demo_fighter())
    target.template = target.template.model_copy(update={"conditional_damage_defenses": [defense]})
    assert adjusted_damage_amount(
        10, DamageType.PIERCING, target, source_qualifiers=_ORDINARY_ATTACK,
    ) == 0
    assert adjusted_damage_amount(
        10, DamageType.PIERCING, target,
        source_qualifiers={*_ORDINARY_ATTACK, DamageSourceQualifier.SILVERED},
    ) == 10
    assert adjusted_damage_amount(
        10, DamageType.PIERCING, target,
        source_qualifiers={*_ORDINARY_ATTACK, DamageSourceQualifier.MAGICAL},
    ) == 10


def test_2024_srd_has_no_nonmagical_bps_defense_leftovers() -> None:
    from app.content.monster_catalog import load_monster_rows
    from app.content.monster_defense_source_audit import parse_defense_profile

    leftovers = []
    for row in load_monster_rows():
        try:
            parse_defense_profile(row)
        except ValueError as exc:
            if any(token in str(exc).lower() for token in ("nonmagical", "silvered", "adamantine")):
                leftovers.append(str(row.get("name")))
    assert leftovers == []
