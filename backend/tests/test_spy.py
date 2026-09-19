from app.content.monster_bonus_action_source_audit import complete_monster_bonus_action_fingerprints
from app.content.monster_catalog import build_monster_catalog, load_monster_rows
from app.content.monster_saving_throws import with_source_saving_throws
from app.content.monster_source_audit import audit_monster_source
from app.content.monsters_zero_engine import build_zero_engine_monsters
from app.domain.catalog import CoverageStatus
from app.domain.models import DamageType


def _spy_template():
    raw = next(template for template in build_zero_engine_monsters() if template.name == "Spy")
    fingerprinted = complete_monster_bonus_action_fingerprints([raw])[0]
    return with_source_saving_throws(fingerprinted)


def test_spy_source_attacks_and_cunning_action_match_srd() -> None:
    spy = _spy_template()
    row = next(row for row in load_monster_rows() if row["name"] == "Spy")

    assert spy.progression_features.cunning_action is True
    assert spy.source_bonus_action_names == ["Cunning Action"]

    attacks = {attack.weapon.name: attack for attack in [spy.weapon_attack, *spy.alternate_weapon_attacks]}
    assert set(attacks) == {"Shortsword", "Hand Crossbow"}

    shortsword = attacks["Shortsword"]
    hand_crossbow = attacks["Hand Crossbow"]
    assert (shortsword.attack_bonus, shortsword.weapon.dice_count, shortsword.weapon.dice_size, shortsword.damage_bonus) == (4, 1, 6, 2)
    assert (hand_crossbow.attack_bonus, hand_crossbow.weapon.dice_count, hand_crossbow.weapon.dice_size, hand_crossbow.damage_bonus) == (4, 1, 6, 2)
    assert (hand_crossbow.weapon.normal_range_ft, hand_crossbow.weapon.long_range_ft) == (30, 120)

    for attack in attacks.values():
        assert attack.weapon.damage_type is DamageType.PIERCING
        assert len(attack.on_hit_damage) == 1
        poison = attack.on_hit_damage[0]
        assert (poison.dice_count, poison.dice_size, poison.damage_bonus, poison.damage_type) == (2, 6, 0, DamageType.POISON)

    assert audit_monster_source(spy, row) == []


def test_spy_is_raw_ready() -> None:
    card = next(card for card in build_monster_catalog() if card.name == "Spy")
    assert card.coverage_status is CoverageStatus.RAW_READY
    assert card.runnable_template_id == "srd-spy"
    assert card.blockers == []
