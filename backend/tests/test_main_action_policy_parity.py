from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
PYTHON_TURN = REPO_ROOT / "backend" / "app" / "combat" / "encounter_combat_turn.py"
PYTHON_ACTION_SURGE = REPO_ROOT / "backend" / "app" / "combat" / "encounter_action_surge.py"
BROWSER_PROFILES = REPO_ROOT / "frontend" / "browser-main-action-profiles.js"


def _positions_in_order(source: str, tokens: list[str]) -> list[int]:
    positions = [source.index(token) for token in tokens]
    assert positions == sorted(positions), f"Policy order drifted: {list(zip(tokens, positions, strict=True))}"
    return positions


def test_python_normal_post_move_main_action_policy_order_is_stable() -> None:
    source = PYTHON_TURN.read_text(encoding="utf-8")
    post_move = source[source.index("movement_events, sequence = move_to_enable_offense("):]
    _positions_in_order(post_move, [
        "spell_events, sequence = resolve_best_spell_offense(",
        "presence = resolve_intimidating_presence(",
        "deferred = resolve_deferred_save_effect(",
        "action_events, sequence = resolve_attack_action(",
        "area_result = resolve_area_save_turn(",
        "chosen_save = save_choice(",
        "attack_choice = choose_standard_attack(",
        "events.append(resolve_dodge_action(",
    ])


def test_browser_normal_post_move_profile_matches_python_policy_order() -> None:
    source = BROWSER_PROFILES.read_text(encoding="utf-8")
    start = source.index("normalPostMove: Object.freeze([")
    end = source.index("]),", start)
    profile = source[start:end]
    _positions_in_order(profile, [
        "CATEGORIES.SPELL_OFFENSE",
        "CATEGORIES.INTIMIDATING_PRESENCE_2014",
        "CATEGORIES.DEFERRED_SAVE_EFFECT",
        "CATEGORIES.ATTACK_ACTION",
        "CATEGORIES.AREA_SAVE",
        "CATEGORIES.SAVE_ACTION",
        "CATEGORIES.STANDARD_ATTACK",
        "CATEGORIES.DODGE",
    ])


def test_python_action_surge_policy_is_attack_only() -> None:
    source = PYTHON_ACTION_SURGE.read_text(encoding="utf-8")
    assert "resolve_attack_action(" in source
    assert "choose_standard_attack(" in source
    assert "resolve_standard_attack_action(" in source
    assert "resolve_best_spell_offense" not in source
    assert "resolve_area_save_turn" not in source


def test_browser_action_surge_profile_matches_python_attack_only_policy() -> None:
    source = BROWSER_PROFILES.read_text(encoding="utf-8")
    start = source.index("actionSurgeAttack: Object.freeze([")
    end = source.index("]),", start)
    profile = source[start:end]
    assert "CATEGORIES.ATTACK_ACTION" in profile
    assert "CATEGORIES.STANDARD_ATTACK" in profile
    for forbidden in [
        "CATEGORIES.SPELL_OFFENSE",
        "CATEGORIES.INTIMIDATING_PRESENCE_2014",
        "CATEGORIES.DEFERRED_SAVE_EFFECT",
        "CATEGORIES.AREA_SAVE",
        "CATEGORIES.SAVE_ACTION",
        "CATEGORIES.DODGE",
    ]:
        assert forbidden not in profile
