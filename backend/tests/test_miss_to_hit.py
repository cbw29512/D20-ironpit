from app.combat.miss_to_hit import resolve_miss_to_hit
from app.content.fighter_progression import build_karnok_stoneward_level
from app.domain.models import CombatantState


def _fighter(*, enabled: bool) -> CombatantState:
    template = build_karnok_stoneward_level(18)
    features = template.progression_features.model_copy(update={"miss_to_hit_once_per_turn": enabled})
    template = template.model_copy(update={"progression_features": features})
    return CombatantState(template=template, current_hp=template.max_hp)


def test_miss_to_hit_is_inert_without_declared_capability() -> None:
    attacker = _fighter(enabled=False)
    assert resolve_miss_to_hit(attacker, False, "1:fighter") == (False, False)
    assert attacker.feature_last_turn_keys == {}


def test_miss_to_hit_converts_only_first_miss_in_turn() -> None:
    attacker = _fighter(enabled=True)
    assert resolve_miss_to_hit(attacker, False, "1:fighter") == (True, True)
    assert resolve_miss_to_hit(attacker, False, "1:fighter") == (False, False)


def test_miss_to_hit_recharges_on_next_turn_key() -> None:
    attacker = _fighter(enabled=True)
    assert resolve_miss_to_hit(attacker, False, "1:fighter") == (True, True)
    assert resolve_miss_to_hit(attacker, False, "2:fighter") == (True, True)


def test_miss_to_hit_never_spends_on_an_existing_hit() -> None:
    attacker = _fighter(enabled=True)
    assert resolve_miss_to_hit(attacker, True, "1:fighter") == (True, False)
    assert resolve_miss_to_hit(attacker, False, "1:fighter") == (True, True)


def test_miss_to_hit_fails_closed_without_turn_identity() -> None:
    attacker = _fighter(enabled=True)
    assert resolve_miss_to_hit(attacker, False, None) == (False, False)
    assert attacker.feature_last_turn_keys == {}
