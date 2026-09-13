from app.content.monster_catalog_2014 import load_catalog_2014, unsupported_mechanics_2014


def _blockers(name: str) -> list[str]:
    try:
        monster = next(item for item in load_catalog_2014() if item.name == name)
        return unsupported_mechanics_2014(monster)
    except StopIteration as exc:
        raise AssertionError(f"Missing 2014 monster fixture: {name}") from exc
    except Exception as exc:
        raise AssertionError(f"Could not inventory {name} blockers.") from exc


def test_travel_and_creation_spells_are_nonblocking_but_damage_spells_remain() -> None:
    try:
        blockers = _blockers("Djinni")
        assert "spell:conjure elemental" not in blockers
        assert "spell:wind walk" not in blockers
        assert "spell:thunderwave" in blockers
    except Exception as exc:
        raise AssertionError("Arena-disabled spell scope was not applied narrowly.") from exc


def test_hard_control_and_noncombat_aboleth_features_are_nonblocking() -> None:
    try:
        blockers = _blockers("Aboleth")
        assert "action:Enslave (3/Day)" not in blockers
        assert "trait:Probing Telepathy" not in blockers
        assert "trait:Mucous Cloud" not in blockers
        assert "attack-detail:Tentacle" in blockers
    except Exception as exc:
        raise AssertionError("Aboleth arena scope removed or retained the wrong mechanics.") from exc


def test_possession_is_disabled_but_combat_fear_remains() -> None:
    try:
        blockers = _blockers("Ghost")
        assert "action:Possession (Recharge 6)" not in blockers
        assert "action:Horrifying Visage" in blockers
    except Exception as exc:
        raise AssertionError("Ghost hard-control policy was not applied narrowly.") from exc


def test_environment_only_mechanics_can_fully_unlock_monsters() -> None:
    try:
        assert _blockers("Nightmare") == []
        assert _blockers("Giant Octopus") == []
    except Exception as exc:
        raise AssertionError("Arena-only blockers still prevent otherwise runnable monsters.") from exc


def test_mimic_keeps_real_combat_blockers_after_object_disguise_is_removed() -> None:
    try:
        blockers = _blockers("Mimic")
        assert "trait:Adhesive (Object Form Only)" not in blockers
        assert "trait:False Appearance (Object Form Only)" not in blockers
        assert "attack-detail:Pseudopod" in blockers
        assert "trait:Grappler" in blockers
    except Exception as exc:
        raise AssertionError("Mimic arena scope erased a real combat mechanic.") from exc
