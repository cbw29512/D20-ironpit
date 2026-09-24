from types import SimpleNamespace

from app.combat.modifier_stack import effective_speed
from app.domain.modifiers import CombatModifier, ModifierKind
from app.domain.runtime import CombatantState, TimedEffect


def _state(*, protected: bool) -> CombatantState:
    return CombatantState.model_construct(
        template=SimpleNamespace(speed_ft=30),
        exhaustion_level=0,
        active_modifiers=[
            CombatModifier(
                id="magic-slow",
                source_id="caster",
                source_effect_id="slow-effect",
                kind=ModifierKind.SPEED,
                flat_bonus=-10,
                source_is_magical=True,
            ),
            CombatModifier(
                id="mud-slow",
                source_id="hazard",
                source_effect_id="mud-effect",
                kind=ModifierKind.SPEED,
                flat_bonus=-5,
                source_is_magical=False,
            ),
        ],
        timed_effects=[
            TimedEffect(
                effect_id="movement-protection",
                source_id="ally",
                prevents_magical_speed_reduction=True,
            )
        ] if protected else [],
    )


def test_magical_speed_reduction_is_ignored_while_protected() -> None:
    # 30 base - 5 nonmagical penalty; the magical -10 is prevented.
    assert effective_speed(_state(protected=True)) == 25


def test_magical_speed_reduction_returns_without_protection() -> None:
    # Both penalties apply when the generic protection is absent.
    assert effective_speed(_state(protected=False)) == 15
