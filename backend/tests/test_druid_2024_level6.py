from __future__ import annotations

from app.combat.alternate_spell_casts import available_alternate_casts, spend_alternate_cast
from app.combat.state import build_combatant_state
from app.content.audited_druid import build_thalen_greenbough_level
from app.content.audited_druid_profile import build_thalen_greenbough_profile
from app.content.canonical_spell_policy import canonical_spell_package
from app.content.character_resource_audit import assert_character_resources_raw_ready
from app.content.pregen_combat_profiles import build_pregen_combat_profiles


def _resource(state, resource_id: str):
    return next(item for item in state.resources if item.id == resource_id)


def test_2024_druid_level_six_progression_and_natural_recovery_resource() -> None:
    profile = build_thalen_greenbough_profile(6)
    hero = build_thalen_greenbough_level(6)

    assert profile.level == 6
    assert hero.level == 6
    assert hero.max_hp == 33
    assert hero.ability_scores.wisdom == 19
    assert _resource(build_combatant_state(hero), "wild-shape").max_uses == 3

    resources = {item.id: item.max_uses for item in hero.resources}
    assert resources["spell-slot-1"] == 4
    assert resources["spell-slot-2"] == 3
    assert resources["spell-slot-3"] == 3
    assert resources["natural-recovery-free-cast"] == 1

    package = canonical_spell_package("druid", 6, "2024", 4)
    assert package is not None
    assert len(package.spells) == 10
    assert package.spells[-1].id == "aid"

    aid = next(item for item in hero.defensive_spell_actions if item.id == "aid")
    assert (
        aid.level,
        aid.action_cost,
        aid.range_ft,
        aid.duration_minutes,
        aid.target_count,
        aid.max_hp_increase,
        aid.current_hp_increase,
    ) == (2, "action", 30, 480, 3, 5, 5)

    audit = next(
        item for item in profile.feature_audits
        if item.feature_id == "natural-recovery"
    )
    assert audit.combat_relevant is True
    assert audit.automated is True


def test_2024_druid_natural_recovery_reuses_shared_alternate_cast_engine() -> None:
    state = build_combatant_state(build_thalen_greenbough_level(6))

    grants = state.template.progression_features.alternate_spell_cast_grants
    assert {(item.spell_id, item.cast_level) for item in grants} == {
        ("burning-hands", 1),
        ("blur", 2),
        ("fireball", 3),
    }
    assert {item.resource_id for item in grants} == {"natural-recovery-free-cast"}
    assert {item.source_name for item in grants} == {"Natural Recovery"}

    fireball_grants = available_alternate_casts(state, "fireball")
    assert len(fireball_grants) == 1
    fireball = fireball_grants[0]
    assert fireball.cast_level == 3

    remaining = spend_alternate_cast(state, fireball)
    assert remaining == 0
    assert _resource(state, "natural-recovery-free-cast").current_uses == 0

    assert available_alternate_casts(state, "fireball") == ()
    assert available_alternate_casts(state, "burning-hands") == ()
    assert available_alternate_casts(state, "blur") == ()
