from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
PYTHON_TURN = REPO_ROOT / "backend" / "app" / "combat" / "encounter_combat_turn.py"
PYTHON_MAIN_ACTION = REPO_ROOT / "backend" / "app" / "combat" / "encounter_main_action.py"
PYTHON_ACTION_SURGE = REPO_ROOT / "backend" / "app" / "combat" / "encounter_action_surge.py"
BROWSER_PROFILES = REPO_ROOT / "frontend" / "browser-main-action-profiles.js"


def _positions_in_order(source: str, tokens: list[str]) -> list[int]:
    positions = [source.index(token) for token in tokens]
    assert positions == sorted(positions), f"Policy order drifted: {list(zip(tokens, positions, strict=True))}"
    return positions


def test_python_normal_post_move_main_action_policy_order_is_stable() -> None:
    source = PYTHON_TURN.read_text(encoding="utf-8")
    assert "return resolve_post_move_action(" in source
    post_move = PYTHON_MAIN_ACTION.read_text(encoding="utf-8")
    _positions_in_order(post_move, [
        "threshold_event, sequence = resolve_hp_threshold_turn(",
        "pick = decide_post_move_offense(",
        "if pick.family == \"save-zone\":",
        "if pick.family == \"spell\":",
        "if pick.family == \"presence\":",
        "if pick.family == \"multi-save\":",
        "if pick.family == \"area-weapon\":",
        "if pick.family == \"attack-action\"",
        "if pick.family == \"area-save\":",
        "if pick.family == \"save-action\"",
        "if pick.family == \"standard-attack\"",
        "events.append(resolve_dodge_action(",
    ])


def test_browser_normal_post_move_profile_matches_python_policy_order() -> None:
    source = BROWSER_PROFILES.read_text(encoding="utf-8")
    start = source.index("normalPostMove: Object.freeze([")
    end = source.index("]),", start)
    profile = source[start:end]
    for token in [
        "CATEGORIES.HP_THRESHOLD_INSTANT_DEATH",
        "CATEGORIES.HP_THRESHOLD_CONDITION",
        "CATEGORIES.SPELL_OFFENSE",
        "CATEGORIES.ATTACK_ACTION",
        "CATEGORIES.STANDARD_ATTACK",
        "CATEGORIES.DODGE",
    ]:
        assert token in profile


def test_python_action_surge_policy_is_attack_only() -> None:
    source = PYTHON_ACTION_SURGE.read_text(encoding="utf-8")
    assert "choose_area_weapon_attack(" in source
    assert "resolve_area_weapon_attack(" in source
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
    assert "CATEGORIES.AREA_WEAPON_ATTACK" in profile
    assert "CATEGORIES.ATTACK_ACTION" in profile
    assert "CATEGORIES.STANDARD_ATTACK" in profile
    for forbidden in [
        "CATEGORIES.SPELL_OFFENSE",
        "CATEGORIES.INTIMIDATING_PRESENCE_2014",
        "CATEGORIES.DEFERRED_EFFECT",
        "CATEGORIES.AREA_SAVE",
        "CATEGORIES.SAVE_ACTION",
        "CATEGORIES.DODGE",
    ]:
        assert forbidden not in profile
