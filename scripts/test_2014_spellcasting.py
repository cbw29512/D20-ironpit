from import_2014_spellcasting import parse_spellcasting


def main() -> int:
    acolyte = (
        "<p><em><strong>Spellcasting.</strong></em> The acolyte is a 1st-level spellcaster. "
        "Its spellcasting ability is Wisdom (spell save DC 12, +4 to hit with spell attacks). "
        "The acolyte has following cleric spells prepared:</p>"
        "<p>Cantrips (at will): light, sacred flame, thaumaturgy</p>"
        "<p>1st level (3 slots): bless, cure wounds, sanctuary</p>"
    )
    parsed = parse_spellcasting(acolyte)
    assert parsed is not None
    assert parsed["caster_level"] == 1
    assert parsed["ability"] == "wisdom"
    assert parsed["save_dc"] == 12
    assert parsed["attack_bonus"] == 4
    assert parsed["slots"] == {"1": 3}
    assert [spell["id"] for spell in parsed["spells"]] == [
        "light", "sacred-flame", "thaumaturgy", "bless", "cure-wounds", "sanctuary",
    ]

    flameskull = (
        "<p><em><strong>Spellcasting.</strong></em> The flameskull is a 5th-level spellcaster. "
        "Its spellcasting ability is Intelligence (spell save DC 13, +5 to hit with spell attacks).</p>"
        "<ul><li>Cantrip (at will): mage hand</li>"
        "<li>1st level (3 slots): magic missile, shield</li>"
        "<li>2nd level (2 slots): blur, flaming sphere</li>"
        "<li>3rd level (1 slot): fireball</li></ul>"
    )
    parsed = parse_spellcasting(flameskull)
    assert parsed is not None
    assert parsed["caster_level"] == 5
    assert parsed["slots"] == {"1": 3, "2": 2, "3": 1}
    assert parsed["spells"][-1]["id"] == "fireball"
    print("2014 regular spellcasting parser regressions passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
