from __future__ import annotations

from app.content.monster_basic_candidates_2014 import unsupported_traits_2014
from app.content.monster_condition_auras import condition_auras_from_source
from app.content.monster_source_2014 import load_monster_source_2014


def _source():
    try:
        return next(row for row in load_monster_source_2014() if row.id == "pit-fiend")
    except Exception as exc:
        raise AssertionError("Missing repaired 2014 Pit Fiend source.") from exc


def test_repaired_source_binds_exact_fear_aura_without_identity_dispatch():
    try:
        source = _source()
        assert "Any creature hostile to the pit fiend" in source.source_traits
        assert "DC 21 Wisdom saving throw" in source.source_traits

        action, = condition_auras_from_source(source.source_traits, "2014")
        aura = action.hostile_start_turn_condition_aura
        assert action.id == "fear-aura" and action.activation_timing == "passive"
        assert (aura.radius_ft, aura.save_dc, aura.save_ability) == (20, 21, "wisdom")
        assert aura.condition_id == "frightened"
        assert aura.success_immunity is True
        assert aura.inactive_while_source_incapacitated is True
        assert aura.condition_expiry_timing == "target_turn_start"
        assert aura.effect_tags == ["frightened"]
        assert "Fear Aura" not in unsupported_traits_2014(source)

        renamed = source.model_copy(update={"id": "other-source", "name": "Other Source"})
        renamed_action, = condition_auras_from_source(renamed.source_traits, "2014")
        assert renamed_action == action
    except Exception:
        raise


def test_changed_outcome_clause_fails_closed_and_restores_trait_blocker():
    try:
        source = _source()
        changed = source.model_copy(update={
            "source_traits": source.source_traits.replace(
                "DC 21 Wisdom saving throw", "DC twenty-one Wisdom saving throw",
            ),
        })
        assert condition_auras_from_source(changed.source_traits, "2014") == []
        assert "Fear Aura" in unsupported_traits_2014(changed)
    except Exception:
        raise
