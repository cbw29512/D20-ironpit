from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
PYTHON_TURN = REPO_ROOT / "backend" / "app" / "combat" / "encounter_combat_turn.py"
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
        "CATEGORIES.ATTACK_ACTION",
        "CATEGORIES.AREA_SAVE",
        "CATEGORIES.SAVE_ACTION",
        "CATEGORIES.STANDARD_ATTACK",
        "CATEGORIES.DODGE",
    ])
