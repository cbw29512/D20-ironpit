from app.content.legacy_monster_roster import build_legacy_monster_templates
from app.content.monster_catalog import build_monster_catalog, load_monster_rows
from app.content.monster_source_audit import audit_monster_source
from app.domain.catalog import CoverageStatus
from app.domain.size import CreatureSize


def _earth_elemental():
    return next(
        monster for monster in build_legacy_monster_templates()
        if monster.name == "Earth Elemental"
    )


def test_earth_elemental_source_attacks_and_prone_rider() -> None:
    elemental = _earth_elemental()
    row = next(row for row in load_monster_rows() if row["name"] == "Earth Elemental")
    attacks = {
        attack.weapon.name: attack
        for attack in [elemental.weapon_attack, *elemental.alternate_weapon_attacks]
    }

    assert elemental.source_trait_names == ["Earth Glide", "Siege Monster"]
    assert elemental.size is CreatureSize.LARGE
    assert (elemental.armor_class, elemental.max_hp, elemental.speed_ft, elemental.initiative_bonus) == (17, 147, 30, -1)
    assert elemental.movement_modes.burrow_ft == 30
    assert [item.value for item in elemental.damage_vulnerabilities] == ["thunder"]

    slam = attacks["Slam"]
    rock = attacks["Rock Launch"]
    assert (slam.attack_bonus, slam.weapon.dice_count, slam.weapon.dice_size, slam.damage_bonus) == (8, 2, 8, 5)
    assert slam.weapon.reach_ft == 10
    assert (rock.attack_bonus, rock.weapon.dice_count, rock.weapon.dice_size, rock.damage_bonus) == (8, 1, 6, 5)
    assert (rock.weapon.normal_range_ft, rock.weapon.long_range_ft) == (60, 60)
    assert rock.knocks_prone_max_size is CreatureSize.LARGE

    assert elemental.attack_action is not None
    assert len(elemental.attack_action.slots) == 2
    for slot in elemental.attack_action.slots:
        assert set(slot.attack_ids) == {slam.id, rock.id}

    assert audit_monster_source(elemental, row) == []


def test_earth_elemental_is_raw_ready() -> None:
    card = next(card for card in build_monster_catalog() if card.name == "Earth Elemental")
    assert card.coverage_status is CoverageStatus.RAW_READY
    assert card.runnable_template_id == "srd-earth-elemental"
    assert card.blockers == []
