from pathlib import Path
import sys
from types import SimpleNamespace

import pytest

# The serializer is a repository-level build tool.  CI runs the Python
# certification suite from backend/, so make the repository root explicit
# rather than relying on the caller's working directory.
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.browser_recharge_serializer import recharge_rows


def _template(*, resources: tuple[str, ...], rules: tuple[tuple[str, int, int], ...]):
    return SimpleNamespace(
        id="recharge-test",
        resources=[SimpleNamespace(id=item) for item in resources],
        recharge_rules=[
            SimpleNamespace(resource_id=resource_id, minimum_roll=minimum_roll, die_size=die_size)
            for resource_id, minimum_roll, die_size in rules
        ],
    )


def test_recharge_rows_serialize_immutable_rule_data() -> None:
    template = _template(resources=("breath",), rules=(("breath", 5, 6),))

    assert recharge_rows(template) == [
        {"resourceId": "breath", "minimumRoll": 5, "dieSize": 6}
    ]


def test_recharge_rows_support_multiple_resources() -> None:
    template = _template(
        resources=("breath", "cloud"),
        rules=(("breath", 5, 6), ("cloud", 6, 6)),
    )

    assert recharge_rows(template) == [
        {"resourceId": "breath", "minimumRoll": 5, "dieSize": 6},
        {"resourceId": "cloud", "minimumRoll": 6, "dieSize": 6},
    ]


def test_recharge_rows_fail_closed_for_missing_resource_binding() -> None:
    template = _template(resources=(), rules=(("breath", 5, 6),))

    with pytest.raises(ValueError, match="does not reference a declared resource"):
        recharge_rows(template)
