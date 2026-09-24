import json
from pathlib import Path

PACKETS = {
    "bard_lore.json": ("bard", "college-lore"),
    "druid_land.json": ("druid", "circle-land"),
    "ranger_hunter.json": ("ranger", "hunter"),
    "sorcerer_draconic.json": ("sorcerer", "draconic-bloodline"),
    "warlock_fiend.json": ("warlock", "fiend"),
    "wizard_evocation.json": ("wizard", "school-evocation"),
}
ROOT = Path(__file__).parents[1] / "app" / "content" / "data" / "pregen_2014"


def _load(name: str) -> dict:
    try:
        return json.loads((ROOT / name).read_text(encoding="utf-8"))
    except Exception as exc:
        raise AssertionError(f"Failed to load 2014 pregen source packet {name}: {exc}") from exc


def test_six_remaining_2014_source_packets_are_complete_and_edition_isolated() -> None:
    for filename, (class_id, subclass_id) in PACKETS.items():
        packet = _load(filename)
        assert packet["ruleset"] == "2014"
        assert packet["class_id"] == class_id
        assert packet["subclass"]["id"] == subclass_id
        assert packet["status"] == "source-prepared-not-certified"
        assert "2024" not in packet["source"]
        levels = packet["levels"]
        assert len(levels) == 20
        assert [row[0] for row in levels] == list(range(1, 21))


def test_source_packets_do_not_claim_ready_or_certified_status() -> None:
    for filename in PACKETS:
        packet = _load(filename)
        serialized = json.dumps(packet).lower()
        assert '"status": "ready"' not in serialized
        assert '"status": "certified"' not in serialized
