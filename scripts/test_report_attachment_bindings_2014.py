from scripts.report_attachment_bindings_2014 import build_report, render


def test_attachment_report_scans_full_roster_and_routes_grapple_linked_cards():
    report = build_report()
    assert report["source_cards_scanned"] == 327
    assert report["applicable_cards"] == ["cloaker", "darkmantle", "mimic", "stirge"]
    assert report["wired_cards"] == ["stirge"]
    assert report["remaining_card_count"] == 3
    assert {row["reason"] for row in report["exceptions"]} == {
        "grapple_or_restrained_link_uses_shared_grapple_family",
        "conditional_control_attachment_profile_not_supported",
    }
    assert '"source_cards_scanned": 327' in render()
