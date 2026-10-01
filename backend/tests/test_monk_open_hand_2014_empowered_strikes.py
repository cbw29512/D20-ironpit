from __future__ import annotations

from app.content.monk_open_hand_2014_runtime import build_kael_stillwater_2014
from app.domain.damage_sources import DamageSourceQualifier


def test_ki_empowered_strikes_marks_only_level6_plus_unarmed_damage_magical() -> None:
    level5 = build_kael_stillwater_2014(5)
    level6 = build_kael_stillwater_2014(6)

    assert DamageSourceQualifier.MAGICAL not in level5.weapon_attack.damage_source_qualifiers
    assert level5.weapon_attack.weapon.id == "unarmed-strike"

    assert DamageSourceQualifier.MAGICAL in level6.weapon_attack.damage_source_qualifiers
    assert level6.weapon_attack.weapon.id == "unarmed-strike"

    shortsword = level6.alternate_weapon_attacks[0]
    assert shortsword.weapon.id == "shortsword"
    assert DamageSourceQualifier.MAGICAL not in shortsword.damage_source_qualifiers
