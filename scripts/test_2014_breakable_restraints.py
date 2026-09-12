from import_2014_breakable_restraints import parse_breakable_restraint_attack


ETTERCAP = '''<p><em><strong>Web (Recharge 5–6).</strong></em> <em>Ranged Weapon Attack:</em> +4 to hit, range 30/60 ft., one Large or smaller creature. <em>Hit:</em> The creature is restrained by webbing. As an action, the restrained creature can make a DC 11 Strength check, escaping from the webbing on a success. The effect also ends if the webbing is destroyed. The webbing has AC 10, 5 hit points, vulnerability to fire damage, and immunity to bludgeoning, poison, and psychic damage.</p>'''
GIANT_SPIDER = '''<p><em><strong>Web (Recharge 5–6).</strong></em> <em>Ranged Weapon Attack:</em> +5 to hit, range 30/60 ft., one creature. <em>Hit:</em> The target is restrained by webbing. As an action, the restrained target can make a DC 12 Strength check, bursting the webbing on a success. The webbing can also be attacked and destroyed (AC 10; hp 5; vulnerability to fire damage; immunity to bludgeoning, poison, and psychic damage).</p>'''


def main() -> int:
    try:
        ettercap = parse_breakable_restraint_attack(ETTERCAP, {"web": 5})
        spider = parse_breakable_restraint_attack(GIANT_SPIDER, {"web": 5})
        assert ettercap is not None and spider is not None
        assert ettercap["resource_id"] == spider["resource_id"] == "web"
        assert ettercap["breakable_restraint"]["max_target_size"] == "large"
        assert ettercap["breakable_restraint"]["escape_dc"] == 11
        assert spider["breakable_restraint"]["escape_dc"] == 12
        assert spider["damage"]["type"] is None
        assert spider["breakable_restraint"]["damage_vulnerabilities"] == ["fire"]
        assert spider["breakable_restraint"]["damage_immunities"] == ["bludgeoning", "poison", "psychic"]
        print("2014 breakable restraint parser regressions passed.")
        return 0
    except Exception as exc:
        raise AssertionError("Breakable restraint parser regression failed.") from exc


if __name__ == "__main__":
    raise SystemExit(main())
