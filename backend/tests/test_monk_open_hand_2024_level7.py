from __future__ import annotations

from app.combat.rogue_defenses import evasion_damage
from app.combat.state import build_combatant_state
from app.content.monk_open_hand_2014_runtime import build_kael_stillwater_2014
from app.content.monk_open_hand_2024_combat_profile import build_kael_2024_combat_profiles
from app.content.monk_open_hand_2024_profile import build_kael_stillwater_2024_profile
from app.content.monk_open_hand_2024_runtime import build_kael_stillwater_2024


def test_2024_open_hand_monk_level7_compiles_expected_delta() -> None:
    template = build_kael_stillwater_2024(7)
    profile = build_kael_stillwater_2024_profile(7)
    fingerprint = build_kael_2024_combat_profiles(7)[-1]

    assert template.level == profile.level == fingerprint.level == 7
    assert template.speed_ft == fingerprint.speed_ft == 45
    assert template.progression_features.evasion is True
    assert template.progression_features.evasion_disabled_while_incapacitated is True
    assert {item.id: item.max_uses for item in template.resources}["focus-points"] == 7
    audits = {item.feature_id: item for item in profile.feature_audits}
    assert audits["evasion"].automated is True


def test_2024_evasion_disables_while_incapacitated_but_2014_binding_does_not() -> None:
    monk2024 = build_combatant_state(build_kael_stillwater_2024(7))
    assert evasion_damage(monk2024, "dexterity", True, "half", 21) == 0
    assert evasion_damage(monk2024, "dexterity", False, "half", 21) == 10

    monk2024.active_effect_ids.append("incapacitated")
    assert evasion_damage(monk2024, "dexterity", True, "half", 21) == 10
    assert evasion_damage(monk2024, "dexterity", False, "half", 21) == 21

    monk2014 = build_combatant_state(build_kael_stillwater_2014(7))
    monk2014.active_effect_ids.append("incapacitated")
    assert evasion_damage(monk2014, "dexterity", True, "half", 21) == 0
    assert evasion_damage(monk2014, "dexterity", False, "half", 21) == 10
