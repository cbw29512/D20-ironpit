from __future__ import annotations

from types import SimpleNamespace

from app.combat.condition_rules import can_see
from app.combat.defensive_modifier_rules import attacks_against_disadvantage_sources
from app.combat.effective_senses import (
    BLINDSIGHT_REQUIRES_HEARING,
    effective_sense_range_ft,
    sense_is_suppressed,
    source_sense_range_ft,
)
from app.combat.spell_modifiers import build_spell_modifier
from app.combat.state import build_combatant_state
from app.content.audited_druid import build_thalen_greenbough_level
from app.content.druid_2024_land_spells import build_blur_2024
from app.domain.modifiers import CombatModifier, ModifierKind


def _synthetic_hearing_blindsight(
    *,
    blindsight_ft: int = 60,
    deafened: bool = False,
    requires_hearing: bool = True,
    name: str = "Synthetic Hearing Blindsight",
) -> SimpleNamespace:
    """Build a data-only observer. No creature or trait name is consulted by the engine."""
    return SimpleNamespace(
        name=name,
        blindsight_requires_hearing=requires_hearing,
        active_effect_ids=["deafened"] if deafened else [],
        active_modifiers=[],
        timed_effects=[],
        template=SimpleNamespace(
            name=name,
            blindsight_ft=blindsight_ft,
            truesight_ft=0,
            blindsight_requires_hearing=requires_hearing,
            size="medium",
        ),
    )


def _flagged_combatant(*, blindsight_ft: int = 60, requires_hearing: bool = True):
    state = build_combatant_state(
        build_thalen_greenbough_level(2).model_copy(
            update={
                "id": "synthetic-hearing-blindsight",
                "name": "Synthetic Hearing Blindsight",
                "blindsight_ft": blindsight_ft,
                "truesight_ft": 0,
            },
        ),
    )
    object.__setattr__(state.template, BLINDSIGHT_REQUIRES_HEARING, requires_hearing)
    object.__setattr__(state, BLINDSIGHT_REQUIRES_HEARING, requires_hearing)
    return state


def test_hearing_flag_zeroes_blindsight_only_while_deafened() -> None:
    observer = _synthetic_hearing_blindsight(deafened=False)
    assert observer.template.blindsight_ft == 60
    assert source_sense_range_ft(observer, "blindsight") == 60
    assert effective_sense_range_ft(observer, "blindsight") == 60
    assert sense_is_suppressed(observer, "blindsight") is False

    observer.active_effect_ids.append("deafened")
    assert effective_sense_range_ft(observer, "blindsight") == 0
    assert sense_is_suppressed(observer, "blindsight") is True
    assert observer.template.blindsight_ft == 60
    assert source_sense_range_ft(observer, "blindsight") == 60

    observer.active_effect_ids.remove("deafened")
    assert effective_sense_range_ft(observer, "blindsight") == 60
    assert observer.template.blindsight_ft == 60


def test_deafened_does_not_strip_blindsight_without_hearing_flag() -> None:
    observer = _synthetic_hearing_blindsight(deafened=True, requires_hearing=False)
    assert getattr(observer.template, BLINDSIGHT_REQUIRES_HEARING) is False
    assert effective_sense_range_ft(observer, "blindsight") == 60


def test_name_alone_never_suppresses_blindsight() -> None:
    observer = _synthetic_hearing_blindsight(
        deafened=True,
        requires_hearing=False,
        name="Bat",
    )
    assert effective_sense_range_ft(observer, "blindsight") == 60


def test_invisible_target_is_hidden_when_hearing_blindsight_is_deafened() -> None:
    observer = _flagged_combatant()
    target = build_combatant_state(build_thalen_greenbough_level(2))
    target.active_effect_ids.append("invisible")

    assert can_see(observer, target, 30) is True
    observer.active_effect_ids.append("deafened")
    assert can_see(observer, target, 30) is False
    observer.active_effect_ids.remove("deafened")
    assert can_see(observer, target, 30) is True
    assert observer.template.blindsight_ft == 60


def test_blur_bypass_uses_effective_blindsight() -> None:
    defender = build_combatant_state(build_thalen_greenbough_level(2))
    blur = build_blur_2024()
    defender.active_modifiers.append(build_spell_modifier(
        "druid",
        "druid",
        blur.id,
        blur.modifier_effects[0],
        0,
        blur.name,
        concentration_required=True,
        round_number=1,
    ))
    hearing = _synthetic_hearing_blindsight(deafened=False)
    assert attacks_against_disadvantage_sources(defender, hearing, 5) == 0

    hearing.active_effect_ids.append("deafened")
    assert attacks_against_disadvantage_sources(defender, hearing, 5) == 1

    ordinary = _synthetic_hearing_blindsight(deafened=True, requires_hearing=False)
    assert attacks_against_disadvantage_sources(defender, ordinary, 5) == 0


def test_template_only_attacker_still_uses_source_ranges() -> None:
    defender = SimpleNamespace(active_modifiers=[
        CombatModifier(
            id="blur",
            kind=ModifierKind.ATTACKS_AGAINST_DISADVANTAGE,
            source_id="druid",
            source_effect_id="blur",
            bypass_attacker_senses=["blindsight", "truesight"],
        ),
    ])
    template = SimpleNamespace(blindsight_ft=10, truesight_ft=0, creature_type="beast")
    assert attacks_against_disadvantage_sources(defender, template, 5) == 0
    assert attacks_against_disadvantage_sources(defender, template, 15) == 1
