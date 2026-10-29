"""Source proof for Vampire Weaknesses recurring environment damage family."""
import json
from pathlib import Path

def test_vampire_weaknesses_binding_report_exists():
    path = Path("docs/generated/VAMPIRE_WEAKNESSES_BINDINGS_2014.json")
    assert path.exists()
    data = json.loads(path.read_text())
    assert data["applicable_card_count"] == 2
    assert set(data["applicable_cards"]) == {"vampire", "vampire-spawn"}
    assert data["status"].startswith("blocked")
    assert len(data["exceptions"]) == 2
