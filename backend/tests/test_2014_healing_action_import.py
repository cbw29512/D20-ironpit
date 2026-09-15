from __future__ import annotations

import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[2] / "scripts"
sys.path.insert(0, str(SCRIPTS))

from import_2014_healing_actions import parse_limited_healing_action  # noqa: E402


def test_daily_usage_after_bold_heading_parses_planetar_healing_touch_shape() -> None:
    paragraph = (
        "<p><em><strong>Healing Touch</strong></em> (4/Day). The planetar touches another creature. "
        "The target magically regains 30 (6d8 + 3) hit points and is freed from any curse, disease, "
        "poison, blindness, or deafness.</p>"
    )

    parsed = parse_limited_healing_action(paragraph)

    assert parsed is not None
    action, uses = parsed
    assert uses == 4
    assert action == {
        "id": "healing-touch",
        "name": "Healing Touch",
        "action_cost": "action",
        "range_ft": 5,
        "target_mode": "other",
        "dice_count": 6,
        "dice_size": 8,
        "healing_bonus": 3,
        "removable_conditions": ["poisoned", "blinded", "deafened"],
        "resource_id": "healing-touch",
        "resource_cost": 1,
        "animation": "healing",
    }


def test_daily_usage_inside_heading_remains_supported() -> None:
    paragraph = (
        "<p><strong>Healing Burst (3/Day).</strong> The creature touches another creature. "
        "The target regains 10 (2d6 + 3) hit points.</p>"
    )

    parsed = parse_limited_healing_action(paragraph)

    assert parsed is not None
    action, uses = parsed
    assert uses == 3
    assert action["id"] == "healing-burst"
    assert action["dice_count"] == 2
    assert action["dice_size"] == 6
    assert action["healing_bonus"] == 3
