from types import SimpleNamespace

from app.combat.miss_to_hit import resolve_miss_to_hit


def _features(enabled: bool) -> SimpleNamespace:
    return SimpleNamespace(miss_to_hit_once_per_turn=enabled)


def _state() -> SimpleNamespace:
    return SimpleNamespace(feature_last_turn_keys={})


def test_disabled_feature_preserves_miss_without_spending_state() -> None:
    state = _state()

    assert resolve_miss_to_hit(
        features=_features(False), state=state, turn_key="1:fighter", attack_hit=False
    ) is False
    assert state.feature_last_turn_keys == {}


def test_existing_hit_is_preserved_without_spending_state() -> None:
    state = _state()

    assert resolve_miss_to_hit(
        features=_features(True), state=state, turn_key="1:fighter", attack_hit=True
    ) is True
    assert state.feature_last_turn_keys == {}


def test_first_miss_converts_and_second_miss_same_turn_does_not() -> None:
    state = _state()
    features = _features(True)

    assert resolve_miss_to_hit(
        features=features, state=state, turn_key="1:fighter", attack_hit=False
    ) is True
    assert resolve_miss_to_hit(
        features=features, state=state, turn_key="1:fighter", attack_hit=False
    ) is False
    assert state.feature_last_turn_keys["miss_to_hit_once_per_turn"] == "1:fighter"


def test_capability_recharges_on_next_turn_key() -> None:
    state = _state()
    features = _features(True)

    assert resolve_miss_to_hit(
        features=features, state=state, turn_key="1:fighter", attack_hit=False
    ) is True
    assert resolve_miss_to_hit(
        features=features, state=state, turn_key="2:fighter", attack_hit=False
    ) is True
    assert state.feature_last_turn_keys["miss_to_hit_once_per_turn"] == "2:fighter"


def test_missing_turn_identity_fails_closed_without_spending_state() -> None:
    state = _state()

    assert resolve_miss_to_hit(
        features=_features(True), state=state, turn_key=None, attack_hit=False
    ) is False
    assert state.feature_last_turn_keys == {}
