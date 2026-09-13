from import_2014_innate_spellcasting import parse_innate_spellcasting


def main() -> int:
    standard = (
        "<p><em><strong>Innate Spellcasting.</strong></em> The caster's innate spellcasting ability is "
        "Charisma (spell save DC 17, +9 to hit with spell attacks). It can innately cast the following "
        "spells, requiring no material components:</p>"
        "<p>At will: detect magic, thunderwave</p>"
        "<p>3/day each: fly, misty step</p>"
        "<p>1/day each: conjure elemental (air elemental only), plane shift</p>"
        "<p><em><strong>Magic Resistance.</strong></em> test</p>"
    )
    parsed = parse_innate_spellcasting(standard)
    assert parsed is not None and parsed["source_complete"] is True
    assert parsed["ability"] == "charisma" and parsed["save_dc"] == 17 and parsed["attack_bonus"] == 9
    assert parsed["spells"][0]["id"] == "detect-magic" and parsed["spells"][0]["usage"] == "at_will"
    assert parsed["spells"][2]["uses_per_day"] == 3 and parsed["spells"][2]["shared_pool"] is False
    assert parsed["spells"][4]["qualifier"] == "air elemental only"

    shared = (
        "<p><em><strong>Innate Spellcasting.</strong></em> The efreeti's innate spellcasting ability is "
        "Charisma (spell save DC 15, +7 to hit with spell attacks).</p>"
        "<p>3/day: enlarge/reduce, tongues</p>"
    )
    parsed = parse_innate_spellcasting(shared)
    assert parsed is not None
    assert all(spell["shared_pool"] for spell in parsed["spells"])

    single = (
        "<p><em><strong>Innate Spellcasting.</strong></em>(1/Day). The mephit can innately cast sleep, "
        "requiring no material components. Its innate spellcasting ability is Charisma.</p>"
    )
    parsed = parse_innate_spellcasting(single)
    assert parsed is not None and parsed["source_complete"] is True
    assert parsed["spells"] == [{
        "id": "sleep", "name": "sleep", "usage": "per_day", "uses_per_day": 1,
        "shared_pool": False, "qualifier": None,
    }]

    malformed = "<em><strong>Innate Spellcasting.</strong></em>detect magicfireballhold monster"
    parsed = parse_innate_spellcasting(malformed)
    assert parsed is not None and parsed["source_complete"] is False and parsed["spells"] == []
    print("2014 innate spellcasting parser regressions passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
